import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.quiz_question import QuizQuestion


class QuizRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_many(self, questions_data: list[dict]) -> list[QuizQuestion]:
        questions = []
        for data in questions_data:
            # Serialize options list to JSON string for SQLite
            if "options" in data and data["options"] is not None:
                data = {**data, "options": json.dumps(data["options"])}
            q = QuizQuestion(**data)
            self.db.add(q)
            questions.append(q)
        await self.db.flush()
        for q in questions:
            await self.db.refresh(q)
        return questions

    async def get_by_session(
        self,
        session_id: str,
        difficulty: str | None = None,
        question_type: str | None = None,
    ) -> list[QuizQuestion]:
        query = select(QuizQuestion).where(QuizQuestion.session_id == session_id)
        if difficulty:
            query = query.where(QuizQuestion.difficulty == difficulty)
        if question_type:
            query = query.where(QuizQuestion.question_type == question_type)
        query = query.order_by(QuizQuestion.created_at.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_saved_for_review(self, question_id: str, saved: bool) -> QuizQuestion | None:
        result = await self.db.execute(
            select(QuizQuestion).where(QuizQuestion.id == question_id)
        )
        question = result.scalar_one_or_none()
        if question:
            question.saved_for_review = saved
            await self.db.flush()
        return question

    async def get_by_id(self, question_id: str) -> QuizQuestion | None:
        result = await self.db.execute(
            select(QuizQuestion).where(QuizQuestion.id == question_id)
        )
        return result.scalar_one_or_none()
