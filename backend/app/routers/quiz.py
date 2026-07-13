import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.repositories.quiz import QuizRepository
from app.repositories.session import SessionRepository
from app.repositories.attempt import AttemptRepository
from app.schemas.quiz import QuizQuestion, QuizAnswerRequest, QuizAnswerResponse

router = APIRouter(tags=["quiz"])


@router.get("/sessions/{session_id}/quiz", response_model=list[QuizQuestion])
async def get_quiz(
    session_id: str,
    difficulty: str | None = Query(None),
    question_type: str | None = Query(None, alias="type"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # Verify session ownership
    session_repo = SessionRepository(db)
    session = await session_repo.get_by_id(uuid.UUID(session_id))
    if not session or str(session.user_id) != user_id:
        raise HTTPException(status_code=404, detail="Session not found.")

    quiz_repo = QuizRepository(db)
    questions = await quiz_repo.get_by_session(
        uuid.UUID(session_id),
        difficulty=difficulty,
        question_type=question_type,
    )

    result = []
    for q in questions:
        options = None
        if q.options and isinstance(q.options, list):
            from app.schemas.quiz import AnswerOption
            options = [AnswerOption(**o) for o in q.options]
        result.append(
            QuizQuestion(
                id=str(q.id),
                question_type=q.question_type,
                difficulty=q.difficulty,
                question_text=q.question_text,
                options=options,
                correct_answer=q.correct_answer,
                explanation=q.explanation,
                hint=q.hint,
                saved_for_review=q.saved_for_review,
            )
        )
    return result


@router.patch("/quiz-questions/{question_id}/save-for-review")
async def save_for_review(
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    quiz_repo = QuizRepository(db)
    question = await quiz_repo.update_saved_for_review(uuid.UUID(question_id), saved=True)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")
    return {"saved": True}


@router.get("/sessions/{session_id}/quiz/{question_id}/answer")
async def get_answer(
    session_id: str,
    question_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    quiz_repo = QuizRepository(db)
    question = await quiz_repo.get_by_id(uuid.UUID(question_id))
    if not question or str(question.session_id) != session_id:
        raise HTTPException(status_code=404, detail="Question not found.")
    return {"correct_answer": question.correct_answer, "explanation": question.explanation}


@router.post("/sessions/{session_id}/quiz/{question_id}/answer", response_model=QuizAnswerResponse)
async def submit_answer(
    session_id: str,
    question_id: str,
    body: QuizAnswerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    # 1. Verify access and get question
    quiz_repo = QuizRepository(db)
    question = await quiz_repo.get_by_id(uuid.UUID(question_id))
    if not question or str(question.session_id) != session_id:
        raise HTTPException(status_code=404, detail="Question not found.")

    # 2. Check correctness (simple matching for MCQ, otherwise requires LLM for open-ended, 
    # but for simplicity we'll assume basic string match for MCQ and true_false)
    # The requirement says "checks correctness against correct_answer"
    is_correct = (body.answer.strip().lower() == str(question.correct_answer).strip().lower())

    # 3. Write attempt history
    attempt_repo = AttemptRepository(db)
    await attempt_repo.create(
        user_id=user_id,
        session_id=session_id,
        topic_id=str(question.topic_id) if question.topic_id else None,
        source_mode="quiz",
        difficulty=question.difficulty,
        is_correct=is_correct,
        score=1.0 if is_correct else 0.0,
        quiz_question_id=str(question.id)
    )
    await db.commit()

    return QuizAnswerResponse(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation
    )
