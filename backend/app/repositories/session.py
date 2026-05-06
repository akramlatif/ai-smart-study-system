from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.session import StudySession


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: str, previous_id: str | None = None) -> StudySession:
        session = StudySession(user_id=user_id, previous_id=previous_id)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_by_id(self, session_id: str) -> StudySession | None:
        result = await self.db.execute(
            select(StudySession).where(StudySession.id == session_id)
        )
        return result.scalar_one_or_none()

    async def update_interaction_count(self, session_id: str, count: int) -> None:
        session = await self.get_by_id(session_id)
        if session:
            session.interaction_count = count
            await self.db.flush()

    async def end_session(self, session_id: str) -> None:
        session = await self.get_by_id(session_id)
        if session:
            session.ended_at = datetime.now(timezone.utc)
            await self.db.flush()

    async def get_user_sessions(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> list[StudySession]:
        result = await self.db.execute(
            select(StudySession)
            .where(StudySession.user_id == user_id)
            .order_by(StudySession.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
