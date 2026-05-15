from pydantic import BaseModel

class UserMetrics(BaseModel):
    total_sessions: int
    total_topics: int
    mastered_topics: int
    accuracy_percentage: float
    questions_to_review: int
