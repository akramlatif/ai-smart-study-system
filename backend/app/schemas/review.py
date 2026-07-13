from datetime import datetime
from pydantic import BaseModel

from app.schemas.quiz import QuizQuestion


class ReviewItem(BaseModel):
    """
    Represents an item that is due for review.
    It combines the spaced repetition metadata from the last QuestionAttempt
    with the actual question content from QuizQuestion.
    """
    attempt_id: str
    topic_id: str | None
    session_id: str
    source_mode: str
    difficulty: str
    
    # SM-2 info
    next_review_at: datetime
    review_interval_days: int
    ease_factor: float
    
    # The actual question content to display
    question: QuizQuestion | None

    model_config = {"from_attributes": True}
