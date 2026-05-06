from pydantic import BaseModel, field_validator


class TopicAnalysis(BaseModel):
    main_topic: str
    subtopics: list[str]  # up to 5
    confidence: float  # 0.0–1.0
    needs_clarification: bool = False

    @field_validator("subtopics")
    @classmethod
    def limit_subtopics(cls, v: list[str]) -> list[str]:
        return v[:5]

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))
