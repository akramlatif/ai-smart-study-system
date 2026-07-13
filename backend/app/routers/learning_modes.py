import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import get_current_user_id
from app.schemas.feynman import FeynmanRequest, FeynmanFeedback, FeynmanAttemptResponse
from app.schemas.socratic import (
    SocraticRespondRequest,
    SocraticResponse,
    SocraticSessionResponse,
    SocraticHistoryResponse,
    QuestionAnswerPair,
    SocraticQuestion,
    SocraticComplete,
)
import app.services.session_manager as session_manager
import app.services.feynman_evaluator as feynman_evaluator
import app.services.socratic_tutor as socratic_tutor
from app.repositories.feynman import FeynmanRepository
from app.repositories.socratic import SocraticRepository
from app.repositories.topic import TopicRepository
from app.repositories.attempt import AttemptRepository

router = APIRouter(tags=["learning-modes"])


# ---------------------------------------------------------------------------
# Feynman Technique Endpoints
# ---------------------------------------------------------------------------

@router.post("/sessions/{session_id}/feynman", response_model=FeynmanAttemptResponse)
async def submit_feynman(
    session_id: str,
    body: FeynmanRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not study_session.topics:
        raise HTTPException(status_code=422, detail="No active topic in session. Please analyze a topic first.")

    current_topic = study_session.topics[-1]
    topic_repo = TopicRepository(db)
    db_topics = await topic_repo.get_by_session(session_id)
    main_topics = [t for t in db_topics if t.is_main]
    topic_id = main_topics[-1].id if main_topics else None

    context = session_manager.build_context_window(study_session)
    feedback = await feynman_evaluator.evaluate(
        student_explanation=body.explanation,
        topic=current_topic,
        session_context=context,
    )

    feynman_repo = FeynmanRepository(db)
    attempt = await feynman_repo.create(
        session_id=session_id,
        topic_id=topic_id,
        explanation=body.explanation,
        feedback=feedback,
    )
    
    # Write attempt history
    attempt_repo = AttemptRepository(db)
    await attempt_repo.create(
        user_id=user_id,
        session_id=session_id,
        topic_id=topic_id,
        source_mode="feynman",
        difficulty="medium",
        is_correct=None,
        score=feedback.comprehension_score / 100.0,
    )
    
    await db.commit()

    return FeynmanAttemptResponse(
        attempt_id=attempt.id,
        feedback=feedback,
        topic=current_topic.main_topic,
        created_at=attempt.created_at,
    )


@router.get("/sessions/{session_id}/feynman/history")
async def get_feynman_history(
    session_id: str,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    feynman_repo = FeynmanRepository(db)
    attempts = await feynman_repo.get_by_session(session_id, limit=limit, offset=offset)

    result = []
    for attempt in attempts:
        result.append({
            "attempt_id": attempt.id,
            "topic_id": attempt.topic_id,
            "comprehension_score": attempt.comprehension_score,
            "strengths": json.loads(attempt.strengths),
            "gaps": json.loads(attempt.gaps),
            "misconceptions": json.loads(attempt.misconceptions),
            "simplified_correction": attempt.simplified_correction,
            "encouragement_message": attempt.encouragement_message,
            "created_at": attempt.created_at.isoformat(),
        })
    return {"attempts": result, "total": len(result)}


# ---------------------------------------------------------------------------
# Socratic Method Endpoints
# ---------------------------------------------------------------------------

@router.post("/sessions/{session_id}/socratic/start", response_model=SocraticSessionResponse)
async def start_socratic(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not study_session.topics:
        raise HTTPException(status_code=422, detail="No active topic in session. Please analyze a topic first.")

    current_topic = study_session.topics[-1]
    topic_repo = TopicRepository(db)
    db_topics = await topic_repo.get_by_session(session_id)
    main_topics = [t for t in db_topics if t.is_main]
    topic_id = main_topics[-1].id if main_topics else None

    context = session_manager.build_context_window(study_session)
    first_question = await socratic_tutor.start(
        topic=current_topic,
        session_context=context,
    )

    socratic_repo = SocraticRepository(db)
    socratic_session = await socratic_repo.create_session(session_id=session_id, topic_id=topic_id)
    await socratic_repo.add_question(socratic_session_id=socratic_session.id, question=first_question, index=1)
    await db.commit()

    return SocraticSessionResponse(socratic_session_id=socratic_session.id, question=first_question)


@router.post("/sessions/{session_id}/socratic/respond", response_model=SocraticResponse)
async def respond_socratic(
    session_id: str,
    body: SocraticRespondRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    socratic_repo = SocraticRepository(db)
    socratic_session = await socratic_repo.get_session(body.socratic_session_id)
    if not socratic_session or socratic_session.session_id != session_id:
        raise HTTPException(status_code=404, detail="Socratic session not found.")

    if socratic_session.is_complete:
        raise HTTPException(status_code=422, detail="Socratic session is already complete.")

    qa_pairs_db = await socratic_repo.get_qa_pairs(body.socratic_session_id)
    unanswered = next((p for p in reversed(qa_pairs_db) if p.student_answer is None), None)
    if not unanswered:
        raise HTTPException(status_code=422, detail="No pending question to answer.")

    await socratic_repo.answer_question(unanswered.id, body.answer)

    question_chain = [
        QuestionAnswerPair(
            question_index=pair.question_index,
            question=SocraticQuestion(
                question_text=pair.question_text,
                question_type=pair.question_type,  # type: ignore[arg-type]
                depth_level=pair.depth_level,
            ),
            student_answer=body.answer if pair.id == unanswered.id else pair.student_answer,
        )
        for pair in qa_pairs_db
    ]

    context = session_manager.build_context_window(study_session)
    response = await socratic_tutor.respond(
        student_answer=body.answer,
        question_chain=question_chain,
        current_depth=unanswered.depth_level,
        session_context=context,
    )

    if response.is_complete and response.completion:
        await socratic_repo.complete_session(
            socratic_session_id=body.socratic_session_id,
            summary=response.completion.summary,
            key_insights=response.completion.key_insights,
            depth_reached=response.completion.depth_reached,
        )
    elif response.question:
        await socratic_repo.add_question(
            socratic_session_id=body.socratic_session_id,
            question=response.question,
            index=len(qa_pairs_db) + 1,
        )
        await socratic_repo.update_depth(body.socratic_session_id, response.question.depth_level)

    await db.commit()
    return response


@router.get("/sessions/{session_id}/socratic/{socratic_session_id}", response_model=SocraticHistoryResponse)
async def get_socratic_history(
    session_id: str,
    socratic_session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
):
    study_session = await session_manager.get_session(session_id, db, redis)
    if not study_session or study_session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    socratic_repo = SocraticRepository(db)
    socratic_session = await socratic_repo.get_session(socratic_session_id)
    if not socratic_session or socratic_session.session_id != session_id:
        raise HTTPException(status_code=404, detail="Socratic session not found.")

    qa_pairs_db = await socratic_repo.get_qa_pairs(socratic_session_id)
    pairs = [
        QuestionAnswerPair(
            question_index=p.question_index,
            question=SocraticQuestion(
                question_text=p.question_text,
                question_type=p.question_type,  # type: ignore[arg-type]
                depth_level=p.depth_level,
            ),
            student_answer=p.student_answer,
        )
        for p in qa_pairs_db
    ]

    topic_name = study_session.topics[-1].main_topic if study_session.topics else ""
    completion = None
    if socratic_session.is_complete and socratic_session.summary:
        key_insights = json.loads(socratic_session.key_insights) if socratic_session.key_insights else []
        completion = SocraticComplete(
            summary=socratic_session.summary,
            key_insights=key_insights,
            depth_reached=socratic_session.depth_reached,
        )

    return SocraticHistoryResponse(
        socratic_session_id=socratic_session.id,
        topic=topic_name,
        pairs=pairs,
        is_complete=socratic_session.is_complete,
        completion=completion,
        depth_reached=socratic_session.depth_reached,
        created_at=socratic_session.created_at,
    )
