from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class SocraticQuestion(BaseModel):
    question_text: str
    question_type: Literal["probing", "clarifying", "hypothetical", "evaluative"]
    depth_level: int = Field(..., ge=1, le=5)


class SocraticComplete(BaseModel):
    summary: str
    key_insights: list[str]
    depth_reached: int = Field(..., ge=1, le=5)


class SocraticResponse(BaseModel):
    is_complete: bool
    question: SocraticQuestion | None = None
    completion: SocraticComplete | None = None


class SocraticRespondRequest(BaseModel):
    socratic_session_id: str
    answer: str = Field(..., min_length=10, max_length=2000)


class QuestionAnswerPair(BaseModel):
    question_index: int
    question: SocraticQuestion
    student_answer: str | None = None


class SocraticSessionResponse(BaseModel):
    socratic_session_id: str
    question: SocraticQuestion


class SocraticHistoryResponse(BaseModel):
    socratic_session_id: str
    topic: str
    pairs: list[QuestionAnswerPair]
    is_complete: bool
    completion: SocraticComplete | None = None
    depth_reached: int
    created_at: datetime
