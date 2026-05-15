import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.feynman import FeynmanAttempt
from app.schemas.feynman import FeynmanFeedback


class FeynmanRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: str,
        topic_id: str | None,
        explanation: str,
        feedback: FeynmanFeedback,
    ) -> FeynmanAttempt:
        attempt = FeynmanAttempt(
            session_id=session_id,
            topic_id=topic_id,
            student_explanation=explanation,
            comprehension_score=feedback.comprehension_score,
            strengths=json.dumps(feedback.strengths),
            gaps=json.dumps(feedback.gaps),
            misconceptions=json.dumps(feedback.misconceptions),
            simplified_correction=feedback.simplified_correction,
            encouragement_message=feedback.encouragement_message,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(attempt)
        await self.db.flush()
        await self.db.refresh(attempt)
        return attempt

    async def get_by_session(
        self,
        session_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> list[FeynmanAttempt]:
        result = await self.db.execute(
            select(FeynmanAttempt)
            .where(FeynmanAttempt.session_id == session_id)
            .order_by(FeynmanAttempt.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
