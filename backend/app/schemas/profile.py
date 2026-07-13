from pydantic import BaseModel
from typing import Literal


class TopicMastery(BaseModel):
    topic_id: str
    mastery_level: Literal["not_started", "learning", "practiced", "mastered"]


class LearnerProfile(BaseModel):
    user_id: str
    preferred_difficulty: Literal["easy", "medium", "hard"]
    weak_topics: list[str]
    strong_topics: list[str]
    topic_mastery: list[TopicMastery]
