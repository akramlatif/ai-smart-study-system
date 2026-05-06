from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.topic import Topic


class TopicRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        session_id: str,
        name: str,
        confidence: float,
        is_main: bool = True,
        parent_id: str | None = None,
    ) -> Topic:
        topic = Topic(
            session_id=session_id,
            name=name,
            is_main=is_main,
            parent_id=parent_id,
            confidence=confidence,
        )
        self.db.add(topic)
        await self.db.flush()
        await self.db.refresh(topic)
        return topic

    async def get_by_session(self, session_id: str) -> list[Topic]:
        result = await self.db.execute(
            select(Topic)
            .where(Topic.session_id == session_id)
            .order_by(Topic.created_at.asc())
        )
        return list(result.scalars().all())
