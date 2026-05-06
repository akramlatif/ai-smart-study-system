import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.explanation import Explanation


class ExplanationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        topic_id: uuid.UUID,
        level: str,
        content: str,
        word_count: int,
    ) -> Explanation:
        explanation = Explanation(
            id=uuid.uuid4(),
            topic_id=topic_id,
            level=level,
            content=content,
            word_count=word_count,
        )
        self.db.add(explanation)
        await self.db.flush()
        await self.db.refresh(explanation)
        return explanation

    async def get_by_topic(self, topic_id: uuid.UUID) -> list[Explanation]:
        result = await self.db.execute(
            select(Explanation)
            .where(Explanation.topic_id == topic_id)
            .order_by(Explanation.created_at.asc())
        )
        return list(result.scalars().all())
