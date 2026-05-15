from pydantic import BaseModel, Field
from datetime import datetime


class FeynmanRequest(BaseModel):
    explanation: str = Field(..., min_length=50, max_length=5000)


class FeynmanFeedback(BaseModel):
    comprehension_score: int = Field(..., ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    misconceptions: list[str] = Field(default_factory=list)
    simplified_correction: str
    encouragement_message: str


class FeynmanAttemptResponse(BaseModel):
    attempt_id: str
    feedback: FeynmanFeedback
    topic: str
    created_at: datetime
