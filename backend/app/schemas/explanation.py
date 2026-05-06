from typing import Literal
from pydantic import BaseModel


class ExplanationContent(BaseModel):
    level: Literal["basic", "intermediate", "advanced"]
    content: str
    word_count: int
    source_references: list[str] = []


class ExplanationSet(BaseModel):
    topic_id: str
    basic: ExplanationContent
    intermediate: ExplanationContent
    advanced: ExplanationContent
