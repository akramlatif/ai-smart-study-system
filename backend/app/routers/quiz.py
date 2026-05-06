import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.repositories.quiz import QuizRepository
from app.repositories.session import SessionRepository
from app.schemas.quiz import QuizQuestion

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
