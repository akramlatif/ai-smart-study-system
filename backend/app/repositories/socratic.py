import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.socratic import SocraticSession, SocraticQAPair
from app.schemas.socratic import SocraticQuestion


class SocraticRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        session_id: str,
        topic_id: str | None,
    ) -> SocraticSession:
        socratic_session = SocraticSession(
            session_id=session_id,
            topic_id=topic_id,
            depth_reached=1,
            is_complete=False,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(socratic_session)
        await self.db.flush()
        await self.db.refresh(socratic_session)
        return socratic_session

    async def get_session(self, socratic_session_id: str) -> SocraticSession | None:
        result = await self.db.execute(
            select(SocraticSession).where(SocraticSession.id == socratic_session_id)
        )
        return result.scalar_one_or_none()

    async def add_question(
        self,
        socratic_session_id: str,
        question: SocraticQuestion,
        index: int,
    ) -> SocraticQAPair:
        qa_pair = SocraticQAPair(
            socratic_session_id=socratic_session_id,
            question_index=index,
            question_text=question.question_text,
            question_type=question.question_type,
            depth_level=question.depth_level,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(qa_pair)
        await self.db.flush()
        await self.db.refresh(qa_pair)
        return qa_pair

    async def answer_question(
        self,
        qa_pair_id: str,
        answer: str,
    ) -> SocraticQAPair:
        result = await self.db.execute(
            select(SocraticQAPair).where(SocraticQAPair.id == qa_pair_id)
        )
        qa_pair = result.scalar_one_or_none()
        if qa_pair:
            qa_pair.student_answer = answer
            qa_pair.answered_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(qa_pair)
        return qa_pair

    async def complete_session(
        self,
        socratic_session_id: str,
        summary: str,
        key_insights: list[str],
        depth_reached: int,
    ) -> SocraticSession:
        result = await self.db.execute(
            select(SocraticSession).where(SocraticSession.id == socratic_session_id)
        )
        socratic_session = result.scalar_one_or_none()
        if socratic_session:
            socratic_session.is_complete = True
            socratic_session.summary = summary
            socratic_session.key_insights = json.dumps(key_insights)
            socratic_session.depth_reached = depth_reached
            socratic_session.completed_at = datetime.now(timezone.utc)
            await self.db.flush()
            await self.db.refresh(socratic_session)
        return socratic_session

    async def update_depth(
        self,
        socratic_session_id: str,
        depth_reached: int,
    ) -> None:
        result = await self.db.execute(
            select(SocraticSession).where(SocraticSession.id == socratic_session_id)
        )
        socratic_session = result.scalar_one_or_none()
        if socratic_session and depth_reached > socratic_session.depth_reached:
            socratic_session.depth_reached = depth_reached
            await self.db.flush()

    async def get_qa_pairs(self, socratic_session_id: str) -> list[SocraticQAPair]:
        result = await self.db.execute(
            select(SocraticQAPair)
            .where(SocraticQAPair.socratic_session_id == socratic_session_id)
            .order_by(SocraticQAPair.question_index.asc())
        )
        return list(result.scalars().all())
