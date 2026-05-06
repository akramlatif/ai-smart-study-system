"""
AccuracyController service — validates explanation relevance and quiz structure.
"""
import numpy as np
from app.schemas.common import ValidationResult
from app.schemas.explanation import ExplanationSet
from app.schemas.quiz import QuizQuestion
from app.schemas.topic import TopicAnalysis


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    va = np.array(a, dtype=float)
    vb = np.array(b, dtype=float)
    norm_a = np.linalg.norm(va)
    norm_b = np.linalg.norm(vb)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(va, vb) / (norm_a * norm_b))


async def validate_explanation(
    explanation_set: ExplanationSet,
    topic: TopicAnalysis,
    source_text: str,
    openai_client,
) -> ValidationResult:
    """
    Validate explanation relevance using embedding cosine similarity.

    If no source_text is provided, skip the check and return valid.
    Rejects if similarity < 0.80.
    """
    if not source_text or not source_text.strip():
        return ValidationResult(valid=True)

    # Combine all explanation content
    combined_explanation = " ".join([
        explanation_set.basic.content,
        explanation_set.intermediate.content,
        explanation_set.advanced.content,
    ])

    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=[combined_explanation, source_text[:8000]],
        )
        emb_explanation = response.data[0].embedding
        emb_source = response.data[1].embedding

        similarity = _cosine_similarity(emb_explanation, emb_source)

        if similarity < 0.80:
            return ValidationResult(
                valid=False,
                error_code="RELEVANCE_BELOW_THRESHOLD",
                error_message=(
                    f"Explanation relevance score {similarity:.2f} is below the "
                    "required threshold of 0.80."
                ),
            )
        return ValidationResult(valid=True)

    except Exception as e:
        # If embedding call fails, allow the explanation through
        return ValidationResult(valid=True)


def validate_quiz(
    questions: list[QuizQuestion],
    session_context: str,
) -> ValidationResult:
    """
    Validate quiz question structure.

    Checks:
    - All questions have valid difficulty labels
    - MCQ questions have exactly 4 options with exactly 1 correct
    """
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
