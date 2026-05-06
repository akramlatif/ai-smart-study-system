from pydantic import BaseModel


class ValidationResult(BaseModel):
    valid: bool
    error_code: str | None = None
    error_message: str | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    user_facing: bool = True
    guidance: str | None = None
    retry_allowed: bool = True


class ErrorResponse(BaseModel):
    error: ErrorDetail
