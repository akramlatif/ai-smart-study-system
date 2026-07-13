from datetime import datetime, timezone, timedelta
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Integer, case
from sqlalchemy.orm import joinedload
from app.models.attempt import QuestionAttempt


from app.services.spaced_repetition import calculate_sm2


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
        graded_correct = None
        if is_correct is not None:
            graded_correct = is_correct
        elif score is not None:
            graded_correct = score >= 0.8

        if graded_correct is not None:
            prev_interval = 0
            prev_ease = 2.5

            # Find the most recent prior attempt for this exact item
            prior_query = select(QuestionAttempt).where(
                QuestionAttempt.user_id == user_id,
            ).order_by(QuestionAttempt.answered_at.desc()).limit(1)

            if quiz_question_id:
                prior_query = prior_query.where(QuestionAttempt.quiz_question_id == quiz_question_id)
            elif topic_id:
                prior_query = prior_query.where(
                    and_(
                        QuestionAttempt.topic_id == topic_id,
                        QuestionAttempt.source_mode == source_mode
                    )
                )
            else:
                prior_query = None # Fallback if we don't have enough context

            if prior_query is not None:
                result = await self.db.execute(prior_query)
                prior_attempt = result.scalar_one_or_none()
                if prior_attempt:
                    prev_interval = prior_attempt.review_interval_days
                    prev_ease = prior_attempt.ease_factor
            
            next_interval, new_ease = calculate_sm2(
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
        
        query = select(QuestionAttempt).options(
            joinedload(QuestionAttempt.quiz_question)
        ).where(
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

    async def get_all_topic_ids(self, user_id: str) -> list[str]:
        """Return all distinct topic_ids for a user (excluding nulls)."""
        query = select(QuestionAttempt.topic_id).where(
            and_(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.topic_id != None,
            )
        ).distinct()
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def get_accuracy_by_difficulty(self, user_id: str, difficulty: str, limit: int = 20) -> dict:
        """Return accuracy for a specific difficulty level from the most recent N attempts."""
        subq = select(QuestionAttempt).where(
            and_(
                QuestionAttempt.user_id == user_id,
                QuestionAttempt.difficulty == difficulty,
            )
        ).order_by(QuestionAttempt.answered_at.desc()).limit(limit).subquery()

        query = select(
            func.count(subq.c.id).label("total"),
            func.sum(case((subq.c.is_correct == True, 1), (subq.c.score >= 0.8, 1), else_=0)).label("correct_count"),
        )
        result = await self.db.execute(query)
        row = result.one()
        total = row.total or 0
        correct = row.correct_count or 0
        return {
            "total": total,
            "correct": correct,
            "accuracy": (correct / total) if total > 0 else 0.0,
        }

