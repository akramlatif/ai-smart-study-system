import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.review import ReviewItem
from app.schemas.quiz import QuizQuestion
from app.repositories.attempt import AttemptRepository

router = APIRouter(tags=["review"])


@router.get("/users/{user_id}/review-queue", response_model=list[ReviewItem])
async def get_review_queue(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Return a list of items due for spaced repetition review."""
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    repo = AttemptRepository(db)
    attempts = await repo.get_due_for_review(user_id)
    
    review_items = []
    for attempt in attempts:
        # We only want to surface things we can actually review (i.e. questions)
        # Note: Future support for reviewing Feynman mode notes could be added here
        if not attempt.quiz_question:
            continue
            
        qq = attempt.quiz_question
        
        # Parse the JSON string options into dicts if they exist
        parsed_options = None
        if qq.options:
            try:
                parsed_options = json.loads(qq.options)
            except json.JSONDecodeError:
                pass

        question_schema = QuizQuestion(
            id=qq.id,
            question_type=qq.question_type,
            difficulty=qq.difficulty,
            question_text=qq.question_text,
            options=parsed_options,
            correct_answer=qq.correct_answer,
            explanation=qq.explanation,
            hint=qq.hint,
            saved_for_review=qq.saved_for_review
        )
        
        review_items.append(ReviewItem(
            attempt_id=attempt.id,
            topic_id=attempt.topic_id,
            session_id=attempt.session_id,
            source_mode=attempt.source_mode,
            difficulty=attempt.difficulty,
            next_review_at=attempt.next_review_at,
            review_interval_days=attempt.review_interval_days,
            ease_factor=attempt.ease_factor,
            question=question_schema
        ))
        
    return review_items
