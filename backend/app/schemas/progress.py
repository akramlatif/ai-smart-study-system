from pydantic import BaseModel
from datetime import datetime


class UserMetrics(BaseModel):
    total_sessions: int
    total_topics: int
    mastered_topics: int
    accuracy_percentage: float
    questions_to_review: int


class DailyActivity(BaseModel):
    date: str
    label: str
    sessions: int
    quiz_questions: int


class WeeklyActivity(BaseModel):
    days: list[DailyActivity]
    total_sessions: int
    total_questions: int


class StudyStreak(BaseModel):
    current_streak: int
    longest_streak: int
    days_active: int
    last_active_date: datetime | None
