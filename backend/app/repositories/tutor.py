"""
Repository for TutorSession and TutorStep CRUD operations.
"""
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.tutor import TutorSession, TutorStep


class TutorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        session_id: str,
        topic: str,
        subtopics: list[str],
        difficulty: str = "medium",
    ) -> TutorSession:
        tutor_session = TutorSession(
            session_id=session_id,
            topic=topic,
            subtopics_json=json.dumps(subtopics),
            difficulty_level=difficulty,
        )
        self.db.add(tutor_session)
        await self.db.flush()
        return tutor_session

    async def get_session(self, tutor_session_id: str) -> TutorSession | None:
        result = await self.db.execute(
            select(TutorSession)
            .where(TutorSession.id == tutor_session_id)
            .options(selectinload(TutorSession.steps))
        )
        return result.scalar_one_or_none()

    async def get_session_by_study_session(self, session_id: str) -> TutorSession | None:
        """Get the latest active tutor session for a study session."""
        result = await self.db.execute(
            select(TutorSession)
            .where(TutorSession.session_id == session_id)
            .where(TutorSession.is_complete == False)
            .options(selectinload(TutorSession.steps))
            .order_by(TutorSession.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def add_step(
        self,
        tutor_session_id: str,
        subtopic_name: str,
        subtopic_index: int,
        explanation: str,
        question_text: str,
    ) -> TutorStep:
        step = TutorStep(
            tutor_session_id=tutor_session_id,
            subtopic_name=subtopic_name,
            subtopic_index=subtopic_index,
            explanation=explanation,
            question_text=question_text,
        )
        self.db.add(step)
        await self.db.flush()
        return step

    async def get_current_step(self, tutor_session_id: str) -> TutorStep | None:
        """Get the latest unanswered step."""
        result = await self.db.execute(
            select(TutorStep)
            .where(TutorStep.tutor_session_id == tutor_session_id)
            .where(TutorStep.student_answer == None)
            .where(TutorStep.is_skipped == False)
            .order_by(TutorStep.subtopic_index.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def update_step_answer(
        self,
        step_id: str,
        student_answer: str,
        is_correct: bool,
        score: float,
        feedback: str,
        hint: str | None = None,
        attempts: int = 1,
    ) -> None:
        result = await self.db.execute(
            select(TutorStep).where(TutorStep.id == step_id)
        )
        step = result.scalar_one_or_none()
        if step:
            step.student_answer = student_answer
            step.is_correct = is_correct
            step.score = score
            step.feedback = feedback
            step.hint = hint
            step.attempts = attempts

    async def mark_step_skipped(self, step_id: str) -> None:
        result = await self.db.execute(
            select(TutorStep).where(TutorStep.id == step_id)
        )
        step = result.scalar_one_or_none()
        if step:
            step.is_skipped = True

    async def update_session_progress(
        self,
        tutor_session_id: str,
        current_index: int,
        correct_count: int,
        incorrect_count: int,
        difficulty: str | None = None,
        weak_areas: list[str] | None = None,
        is_complete: bool = False,
    ) -> None:
        result = await self.db.execute(
            select(TutorSession).where(TutorSession.id == tutor_session_id)
        )
        session = result.scalar_one_or_none()
        if session:
            session.current_subtopic_index = current_index
            session.correct_count = correct_count
            session.incorrect_count = incorrect_count
            session.is_complete = is_complete
            if difficulty:
                session.difficulty_level = difficulty
            if weak_areas is not None:
                session.weak_areas_json = json.dumps(weak_areas)

    async def get_all_sessions(self, session_id: str) -> list[TutorSession]:
        result = await self.db.execute(
            select(TutorSession)
            .where(TutorSession.session_id == session_id)
            .options(selectinload(TutorSession.steps))
            .order_by(TutorSession.created_at.desc())
        )
        return list(result.scalars().all())
