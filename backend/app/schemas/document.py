from typing import Literal
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    quality_flag: Literal["ok", "low_quality", "unreadable"]
    extracted_char_count: int


class QualityAssessment(BaseModel):
    char_count: int
    flag: Literal["ok", "low_quality", "unreadable"]
    message: str | None = None
