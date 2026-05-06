"""
InputHandler service — validates text/file inputs and detects shortcut phrases.
"""
import re
from app.schemas.common import ValidationResult

# Shortcut patterns
_SIMPLIFY_PATTERNS = [
    r"simplify\s+this",
    r"explain\s+simply",
    r"make\s+it\s+easier",
    r"\bsimplify\b",
]

_DEEPEN_PATTERNS = [
    r"go\s+deeper",
    r"more\s+advanced",
    r"technical\s+details",
]

_HARD_QUIZ_PATTERNS = [
    r"hard\s+questions",
    r"hard\s+quiz",
    r"difficult\s+questions",
]

_SIMPLIFY_RE = re.compile("|".join(_SIMPLIFY_PATTERNS), re.IGNORECASE)
_DEEPEN_RE = re.compile("|".join(_DEEPEN_PATTERNS), re.IGNORECASE)
_HARD_QUIZ_RE = re.compile("|".join(_HARD_QUIZ_PATTERNS), re.IGNORECASE)


def validate_text(text: str, input_type: str = "question") -> ValidationResult:
    """
    Validate text input.

    input_type:
      - "question": trimmed length must be 3–500 chars
      - "notes":    trimmed length must be 3–10,000 chars
    """
    if not text or not text.strip():
        return ValidationResult(
            valid=False,
            error_code="INPUT_EMPTY",
            error_message="Input cannot be empty or whitespace only.",
        )

    trimmed = text.strip()
    length = len(trimmed)

    if input_type == "question":
        min_len, max_len = 3, 500
    else:  # notes
        min_len, max_len = 3, 10_000

    if length < min_len:
        return ValidationResult(
            valid=False,
            error_code="INPUT_TOO_SHORT",
            error_message=f"Input must be at least {min_len} characters.",
        )

    if length > max_len:
        return ValidationResult(
            valid=False,
            error_code="INPUT_TOO_LONG",
            error_message=f"Input exceeds the {max_len:,} character limit.",
        )

    return ValidationResult(valid=True)


def validate_file(filename: str, size_bytes: int, content_type: str) -> ValidationResult:
    """
    Validate uploaded file by name, size, and content type.
    """
    lower = filename.lower()

    if content_type == "application/pdf" or lower.endswith(".pdf"):
        max_bytes = 10 * 1024 * 1024  # 10 MB
        if size_bytes > max_bytes:
            return ValidationResult(
                valid=False,
                error_code="FILE_TOO_LARGE",
                error_message="PDF files must be 10 MB or smaller.",
            )
        if content_type not in ("application/pdf", "application/octet-stream"):
            return ValidationResult(
                valid=False,
                error_code="UNSUPPORTED_FORMAT",
                error_message="File does not appear to be a valid PDF.",
            )
        return ValidationResult(valid=True)

    text_extensions = (".txt", ".md", ".rtf")
    if any(lower.endswith(ext) for ext in text_extensions):
        max_bytes = 5 * 1024 * 1024  # 5 MB
        if size_bytes > max_bytes:
            return ValidationResult(
                valid=False,
                error_code="FILE_TOO_LARGE",
                error_message="Text files must be 5 MB or smaller.",
            )
        return ValidationResult(valid=True)

    return ValidationResult(
        valid=False,
        error_code="UNSUPPORTED_FORMAT",
        error_message="Unsupported file format. Accepted formats: PDF, .txt, .md, .rtf",
    )


def detect_shortcut(text: str) -> str | None:
    """
    Detect shortcut phrases in user input.

    Returns:
      "simplify"  — simplification shortcut
      "deepen"    — depth/advanced shortcut
      "hard_quiz" — hard quiz shortcut
      None        — no shortcut detected
    """
    if _SIMPLIFY_RE.search(text):
        return "simplify"
    if _DEEPEN_RE.search(text):
        return "deepen"
    if _HARD_QUIZ_RE.search(text):
        return "hard_quiz"
    return None
