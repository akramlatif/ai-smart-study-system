from typing import AsyncGenerator, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.config import settings
from app.core.security import get_current_user_id
from app.schemas.session import Interaction
from app.schemas.topic import TopicAnalysis
import app.services.session_manager as session_manager
import app.services.input_handler as input_handler
import app.services.content_extractor as content_extractor
import app.services.topic_analyzer as topic_analyzer
import app.services.explanation_generator as explanation_generator
import app.services.quiz_generator as quiz_generator
import app.services.accuracy_controller as accuracy_controller
from app.repositories.topic import TopicRepository
from app.repositories.explanation import ExplanationRepository
from app.repositories.quiz import QuizRepository

from datetime import datetime, timezone
from openai import AsyncOpenAI


def _get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def _run_pipeline(
    session_id: str,
    user_id: str,
    text: str,
    input_type: str,
    source_text: str,
    db: AsyncSession,
    redis: Any,
    openai_client: AsyncOpenAI,
    difficulty_filter: str | None = None,
) -> dict:
    """Run the full AI pipeline and return results."""
    session = await session_manager.get_session(session_id, db, redis)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    context = session_manager.build_context_window(session)

    # Stage 2: Topic Analysis
    topic = await topic_analyzer.analyze(text, context, openai_client)

    if topic.needs_clarification:
        return {
            "session_id": session_id,
            "response_type": "clarification",
            "message": (
                f"I'm not entirely sure what topic you're studying "
                f"(confidence: {topic.confidence:.0%}). Could you provide more context?"
            ),
            "topic": topic,
        }

    # Persist topic
    topic_repo = TopicRepository(db)
    db_topic = await topic_repo.create(
        session_id=session_id,
        name=topic.main_topic,
        confidence=topic.confidence,
        is_main=True,
    )
    for subtopic_name in topic.subtopics:
        await topic_repo.create(
            session_id=session_id,
            name=subtopic_name,
            confidence=topic.confidence,
            is_main=False,
            parent_id=db_topic.id,
        )

    # Stage 3: Explanation Generation
    explanations = await explanation_generator.generate(
        topic=topic,
        session_context=context,
        source_text=source_text,
        openai_client=openai_client,
        topic_id=str(db_topic.id),
    )

    # Stage 4: Accuracy Validation
    validation = await accuracy_controller.validate_explanation(
        explanation_set=explanations,
        topic=topic,
        source_text=source_text,
        openai_client=openai_client,
    )
    if not validation.valid:
        # Retry once with stricter prompt
        explanations = await explanation_generator.generate(
            topic=topic,
            session_context=context,
            source_text=source_text,
            openai_client=openai_client,
            topic_id=str(db_topic.id),
        )

    # Persist explanations
    exp_repo = ExplanationRepository(db)
    for level_name in ("basic", "intermediate", "advanced"):
        level_content = getattr(explanations, level_name)
        await exp_repo.create(
            topic_id=db_topic.id,
            level=level_name,
            content=level_content.content,
            word_count=level_content.word_count,
        )

    # Stage 5: Quiz Generation
    quiz_questions = await quiz_generator.generate(
        topic=topic,
        explanations=explanations,
        session_context=context,
        openai_client=openai_client,
        difficulty_filter=difficulty_filter,
    )

    # Validate quiz
    quiz_validation = accuracy_controller.validate_quiz(quiz_questions, context)

    # Persist quiz questions
    quiz_repo = QuizRepository(db)
    questions_data = []
    for q in quiz_questions:
        options_json = None
        if q.options:
            options_json = [o.model_dump() for o in q.options]
        questions_data.append({
            "session_id": session_id,
            "topic_id": db_topic.id,
            "question_type": q.question_type,
            "difficulty": q.difficulty,
            "question_text": q.question_text,
            "options": options_json,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
        })
    if questions_data:
        await quiz_repo.create_many(questions_data)

    # Stage 6: Session Update
    now = datetime.now(timezone.utc)
    interaction_index = len(session.interactions) + 1
    user_interaction = Interaction(
        index=interaction_index,
        role="user",
        content=text,
        input_type=input_type,
        timestamp=now,
    )
    await session_manager.append_interaction(session_id, user_interaction, redis)

    # Update session topics/explanations/quiz in Redis
    updated_session = await session_manager.get_session(session_id, db, redis)
    if updated_session:
        updated_session.topics.append(topic)
        updated_session.explanations.append(explanations)
        updated_session.quiz_questions.extend(quiz_questions)
        from app.core.redis import SESSION_TTL_SECONDS
        await redis.setex(
            f"session:{session_id}",
            SESSION_TTL_SECONDS,
            updated_session.model_dump_json(),
        )

    return {
        "session_id": session_id,
        "topic": topic,
        "explanations": explanations,
        "quiz_questions": quiz_questions,
    }


router = APIRouter(tags=["analysis"])


@router.post("/sessions/{session_id}/analyze")
async def analyze(
    session_id: str,
    input_type: str = Form("text"),
    content: str | None = Form(None),
    url: str | None = Form(None),
    file: UploadFile | None = File(None),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    openai_client = _get_openai_client()
    text = ""
    source_text = ""

    if file and file.filename:
        file_bytes = await file.read()
        validation = input_handler.validate_file(
            file.filename, len(file_bytes), file.content_type or ""
        )
        if not validation.valid:
            raise HTTPException(status_code=422, detail=validation.error_message)

        storage_path = await content_extractor.save_file(
            file_bytes, file.filename, user_id, session_id
        )
        lower = file.filename.lower()
        if lower.endswith(".pdf"):
            result = content_extractor.extract_pdf(storage_path)
        else:
            result = content_extractor.extract_text_file(storage_path)

        text = result["text"]
        source_text = text
        input_type = "pdf" if lower.endswith(".pdf") else "file"

    elif content:
        validation = input_handler.validate_text(content, "notes")
        if not validation.valid:
            raise HTTPException(status_code=422, detail=validation.error_message)
        text = content.strip()
        source_text = text
        input_type = "text"
    else:
        raise HTTPException(status_code=422, detail="No input provided.")

    return await _run_pipeline(
        session_id=session_id,
        user_id=user_id,
        text=text,
        input_type=input_type,
        source_text=source_text,
        db=db,
        redis=redis,
        openai_client=openai_client,
    )


@router.post("/sessions/{session_id}/chat")
async def chat(
    session_id: str,
    body: dict,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    message = body.get("message", "")
    if not message:
        raise HTTPException(status_code=422, detail="Message is required.")

    openai_client = _get_openai_client()

    # Detect shortcuts
    shortcut = input_handler.detect_shortcut(message)
    difficulty_filter = None
    if shortcut == "hard_quiz":
        difficulty_filter = "hard"

    session = await session_manager.get_session(session_id, db, redis)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    # Validate text
    validation = input_handler.validate_text(message, "question")
    if not validation.valid:
        raise HTTPException(status_code=422, detail=validation.error_message)

    source_text = ""
    if session.interactions:
        user_msgs = [i for i in session.interactions if i.role == "user"]
        if user_msgs:
            source_text = user_msgs[0].content

    result = await _run_pipeline(
        session_id=session_id,
        user_id=user_id,
        text=message,
        input_type="shortcut" if shortcut else "text",
        source_text=source_text,
        db=db,
        redis=redis,
        openai_client=openai_client,
        difficulty_filter=difficulty_filter,
    )
    result["response_type"] = "explanation"
    if shortcut == "hard_quiz":
        result["response_type"] = "quiz"
    return result


@router.get("/sessions/{session_id}/analyze/stream")
async def analyze_stream(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    """SSE endpoint for streaming analysis progress."""
    import json as _json

    async def event_generator() -> AsyncGenerator[str, None]:
        stages = [
            ("extracting", 20),
            ("analyzing_topics", 40),
            ("generating_explanations", 65),
            ("validating", 80),
            ("generating_quiz", 90),
            ("complete", 100),
        ]
        for stage, progress in stages:
            data = _json.dumps({"stage": stage, "progress": progress})
            yield f"data: {data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
