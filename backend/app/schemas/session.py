from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from app.schemas.topic import TopicAnalysis
from app.schemas.explanation import ExplanationSet
from app.schemas.quiz import QuizQuestion


class Interaction(BaseModel):
    index: int  # 1-based, max 50
    role: Literal["user", "assistant"]
    content: str
    input_type: Literal["text", "pdf", "file", "url", "shortcut"]
    timestamp: datetime


class StudySession(BaseModel):
    id: str
    user_id: str
    previous_id: str | None = None
    topics: list[TopicAnalysis] = []
    explanations: list[ExplanationSet] = []
    quiz_questions: list[QuizQuestion] = []
    interactions: list[Interaction] = []
    created_at: datetime
    last_active: datetime

    model_config = {"from_attributes": True}


class SessionSummary(BaseModel):
    session_id: str
    topics_studied: list[str]
    questions_asked: int
    quiz_questions_generated: int
    duration_minutes: float
    interactions: list[Interaction]  # chronological


class SessionCreate(BaseModel):
    pass


class SessionResponse(BaseModel):
    session_id: str
    created_at: datetime
