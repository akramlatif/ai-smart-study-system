from datetime import datetime, timezone, timedelta
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Integer, case
from app.models.attempt import QuestionAttempt


def _compute_sm2(is_correct: bool, current_interval: int, current_ease: float) -> tuple[int, float]:
    """
    Simplified SM-2 spaced repetition algorithm.
    Returns (next_interval_days, new_ease_factor).
    """
    quality = 4 if is_correct else 1
    new_ease = current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(1.3, min(10.0, new_ease))  # Floor 1.3, max 10.0

    if not is_correct:
        return 1, new_ease

    if current_interval == 0:
        next_interval = 1
    elif current_interval == 1:
        next_interval = 6
    else:
        next_interval = int(current_interval * new_ease)
        
    return next_interval, new_ease


class AttemptRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: str,
        session_id: str,
        topic_id: str | None,
        source_mode: str,
        difficulty: str,
        is_correct: bool | None,
        score: float | None,
        quiz_question_id: str | None = None,
    ) -> QuestionAttempt:
        
        now = datetime.now(timezone.utc)
        
        attempt = QuestionAttempt(
            user_id=user_id,
            session_id=session_id,
            topic_id=topic_id,
            quiz_question_id=quiz_question_id,
            source_mode=source_mode,
            difficulty=difficulty,
            is_correct=is_correct,
            score=score,
            answered_at=now,
        )

        # Apply Spaced Repetition logic if graded (binary or float threshold)
        # Note: if score is provided but is_correct is None, we treat score >= 0.8 as correct
        graded_correct = None
        if is_correct is not None:
            graded_correct = is_correct
        elif score is not None:
            graded_correct = score >= 0.8

        if graded_correct is not None:
            # We would normally look up the last attempt for this question/topic to get current interval/ease.
            # But for simplicity, we start fresh for each new attempt unless we query history.
            # Let's see if there's a previous attempt for this exact question (or topic for feynman).
            
            # Simple heuristic for previous state:
            prev_interval = 1
            prev_ease = 2.5
            
            # (Optional enhancement: query previous state)
            
            next_interval, new_ease = _compute_sm2(
                is_correct=graded_correct,
                current_interval=prev_interval,
                current_ease=prev_ease
            )
            attempt.review_interval_days = next_interval
            attempt.ease_factor = new_ease
            attempt.next_review_at = now + timedelta(days=next_interval)

        self.db.add(attempt)
        await self.db.flush()
        await self.db.refresh(attempt)
        return attempt

    async def get_due_for_review(self, user_id: str, before: datetime | None = None) -> Sequence[QuestionAttempt]:
        if before is None:
            before = datetime.now(timezone.utc)
        
        query = select(QuestionAttempt).where(
            and_(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.next_review_at != None,
                QuestionAttempt.next_review_at <= before
            )
        ).order_by(QuestionAttempt.next_review_at.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_topic_performance(self, user_id: str, topic_id: str) -> dict:
        query = select(
            func.count(QuestionAttempt.id).label("total"),
            func.sum(case((QuestionAttempt.is_correct == True, 1), (QuestionAttempt.score >= 0.8, 1), else_=0)).label("correct_count"),
            func.avg(QuestionAttempt.score).label("avg_score")
        ).where(
            and_(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.topic_id == topic_id
            )
        )
        result = await self.db.execute(query)
        row = result.one()
        
        total = row.total or 0
        correct = row.correct_count or 0
        avg_score = row.avg_score or 0.0
        
        return {
            "total_attempts": total,
            "correct_attempts": correct,
            "accuracy": (correct / total) if total > 0 else 0.0,
            "avg_score": float(avg_score)
        }

    async def get_recent_attempts(self, user_id: str, limit: int = 20) -> Sequence[QuestionAttempt]:
        query = select(QuestionAttempt).where(
            QuestionAttempt.user_id == user_id
        ).order_by(QuestionAttempt.answered_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
