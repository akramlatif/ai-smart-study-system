import uuid
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.session import StudySession
from app.models.topic import Topic
from app.models.tutor import TutorSession
from app.models.quiz_question import QuizQuestion

class ProgressRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_metrics(self, user_id: uuid.UUID) -> dict:
        """Aggregate learning metrics for a specific user."""
        
        # 1. Total Sessions
        sessions_stmt = select(func.count(StudySession.id)).where(StudySession.user_id == str(user_id))
        total_sessions = await self.db.scalar(sessions_stmt) or 0

        # 2. Total Topics Analyzed
        topics_stmt = (
            select(func.count(Topic.id))
            .join(StudySession)
            .where(StudySession.user_id == str(user_id))
        )
        total_topics = await self.db.scalar(topics_stmt) or 0

        # 3. Tutor Performance (Accuracy & Mastered)
        tutor_stmt = (
            select(
                func.coalesce(func.sum(TutorSession.correct_count), 0).label("correct"),
                func.coalesce(func.sum(TutorSession.incorrect_count), 0).label("incorrect"),
                func.coalesce(func.sum(case((TutorSession.is_complete == True, 1), else_=0)), 0).label("mastered")
            )
            .join(StudySession)
            .where(StudySession.user_id == str(user_id))
        )
        tutor_res = await self.db.execute(tutor_stmt)
        tutor_row = tutor_res.fetchone()
        
        correct = tutor_row.correct if tutor_row and tutor_row.correct else 0
        incorrect = tutor_row.incorrect if tutor_row and tutor_row.incorrect else 0
        mastered_topics = tutor_row.mastered if tutor_row and tutor_row.mastered else 0
        
        total_answers = correct + incorrect
        accuracy = (correct / total_answers * 100) if total_answers > 0 else 0.0

        # 4. Questions Saved for Review
        review_stmt = (
            select(func.count(QuizQuestion.id))
            .join(StudySession)
            .where(StudySession.user_id == str(user_id), QuizQuestion.saved_for_review == True)
        )
        saved_questions = await self.db.scalar(review_stmt) or 0

        return {
            "total_sessions": total_sessions,
            "total_topics": total_topics,
            "mastered_topics": mastered_topics,
            "accuracy_percentage": round(accuracy, 1),
            "questions_to_review": saved_questions
        }
