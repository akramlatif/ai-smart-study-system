"""
AccuracyController service — validates explanation relevance and quiz structure.
Uses keyword overlap for relevance (no embedding API needed with Gemini).
"""
from app.schemas.common import ValidationResult
from app.schemas.explanation import ExplanationSet
from app.schemas.quiz import QuizQuestion
from app.schemas.topic import TopicAnalysis


def _keyword_overlap_score(text_a: str, text_b: str) -> float:
    """
    Simple keyword overlap relevance score.
    Returns fraction of significant words in text_a that appear in text_b.
    Used as a lightweight alternative to embedding cosine similarity.
    """
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "and",
        "or", "but", "if", "then", "that", "this", "it", "its", "not",
    }

    def keywords(text: str) -> set[str]:
        words = text.lower().split()
        return {w.strip(".,;:!?\"'()[]") for w in words if w not in stop_words and len(w) > 3}

    kw_a = keywords(text_a)
    kw_b = keywords(text_b)

    if not kw_a:
        return 1.0  # no keywords to check, pass

    overlap = kw_a & kw_b
    return len(overlap) / len(kw_a)


async def validate_explanation(
    explanation_set: ExplanationSet,
    topic: TopicAnalysis,
    source_text: str,
    openai_client=None,  # kept for signature compatibility
) -> ValidationResult:
    """
    Validate explanation relevance.
    If no source_text, skip check and return valid.
    Uses keyword overlap as relevance proxy (threshold: 0.15 for keyword overlap).
    """
    if not source_text or not source_text.strip():
        return ValidationResult(valid=True)

    combined_explanation = " ".join([
        explanation_set.basic.content,
        explanation_set.intermediate.content,
        explanation_set.advanced.content,
    ])

    score = _keyword_overlap_score(combined_explanation, source_text)

    # Keyword overlap threshold is lower than embedding similarity (0.15 vs 0.80)
    if score < 0.15:
        return ValidationResult(
            valid=False,
            error_code="RELEVANCE_BELOW_THRESHOLD",
            error_message=(
                f"Explanation relevance score {score:.2f} is below the required threshold."
            ),
        )
    return ValidationResult(valid=True)


def validate_quiz(
    questions: list[QuizQuestion],
    session_context: str,
) -> ValidationResult:
    """Validate quiz question structure."""
    valid_difficulties = {"easy", "medium", "hard"}

    for i, q in enumerate(questions):
        if q.difficulty not in valid_difficulties:
            return ValidationResult(
                valid=False,
                error_code="INVALID_DIFFICULTY",
                error_message=f"Question {i + 1} has invalid difficulty: {q.difficulty!r}",
            )

        if q.question_type == "multiple_choice":
            if not q.options or len(q.options) != 4:
                return ValidationResult(
                    valid=False,
                    error_code="INVALID_MCQ_OPTIONS",
                    error_message=(
                        f"Multiple choice question {i + 1} must have exactly 4 options, "
                        f"got {len(q.options) if q.options else 0}."
                    ),
                )
            correct_count = sum(1 for opt in q.options if opt.is_correct)
            if correct_count != 1:
                return ValidationResult(
                    valid=False,
                    error_code="INVALID_MCQ_ANSWER",
                    error_message=(
                        f"Multiple choice question {i + 1} must have exactly 1 correct "
                        f"answer, got {correct_count}."
                    ),
                )

    return ValidationResult(valid=True)
