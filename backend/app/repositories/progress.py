import uuid
from datetime import datetime, timezone, timedelta, date
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

    async def get_weekly_activity(self, user_id: uuid.UUID) -> dict:
        """Sessions and quiz questions per day for the last 7 days."""
        today = datetime.now(timezone.utc).date()
        start = today - timedelta(days=6)

        # Sessions per day
        sessions_stmt = (
            select(
                func.date(StudySession.created_at).label("day"),
                func.count(StudySession.id).label("count"),
            )
            .where(
                StudySession.user_id == str(user_id),
                func.date(StudySession.created_at) >= start,
                func.date(StudySession.created_at) <= today,
            )
            .group_by(func.date(StudySession.created_at))
        )
        sessions_res = await self.db.execute(sessions_stmt)
        sessions_by_day = {str(row.day): row.count for row in sessions_res.fetchall()}

        # Quiz questions per day
        quiz_stmt = (
            select(
                func.date(QuizQuestion.created_at).label("day"),
                func.count(QuizQuestion.id).label("count"),
            )
            .join(StudySession)
            .where(
                StudySession.user_id == str(user_id),
                func.date(QuizQuestion.created_at) >= start,
                func.date(QuizQuestion.created_at) <= today,
            )
            .group_by(func.date(QuizQuestion.created_at))
        )
        quiz_res = await self.db.execute(quiz_stmt)
        quiz_by_day = {str(row.day): row.count for row in quiz_res.fetchall()}

        days = []
        total_sessions = 0
        total_questions = 0
        weekday_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        for offset in range(7):
            d = start + timedelta(days=offset)
            d_str = d.isoformat()
            sessions = sessions_by_day.get(d_str, 0)
            questions = quiz_by_day.get(d_str, 0)
            total_sessions += sessions
            total_questions += questions
            days.append({
                "date": d_str,
                "label": weekday_labels[d.weekday()],
                "sessions": sessions,
                "quiz_questions": questions,
            })

        return {
            "days": days,
            "total_sessions": total_sessions,
            "total_questions": total_questions,
        }

    async def get_study_streak(self, user_id: uuid.UUID) -> dict:
        """Current and longest study streaks, plus total active days."""
        days_stmt = (
            select(func.date(StudySession.created_at).label("day"))
            .where(StudySession.user_id == str(user_id))
            .group_by(func.date(StudySession.created_at))
            .order_by(func.date(StudySession.created_at).desc())
        )
        days_res = await self.db.execute(days_stmt)
        active_days = [str(row.day) for row in days_res.fetchall()]

        if not active_days:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "days_active": 0,
                "last_active_date": None,
            }

        def parse_day(s: str) -> date:
            # Handles both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM:SS.mmmmmm" shapes
            return date.fromisoformat(s.split(" ")[0])

        today = datetime.now(timezone.utc).date()
        day_set = {parse_day(s) for s in active_days}

        # Current streak: count back from today (or yesterday if today has no session yet)
        current_streak = 0
        cursor = today if today in day_set else today - timedelta(days=1)
        while cursor in day_set:
            current_streak += 1
            cursor -= timedelta(days=1)

        # Longest streak: scan all active days
        sorted_days = sorted(day_set)
        longest_streak = 1
        run = 1
        for prev, curr in zip(sorted_days, sorted_days[1:]):
            if (curr - prev).days == 1:
                run += 1
                longest_streak = max(longest_streak, run)
            else:
                run = 1

        last_active = max(day_set)

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "days_active": len(day_set),
            "last_active_date": datetime.combine(last_active, datetime.min.time(), tzinfo=timezone.utc),
        }
