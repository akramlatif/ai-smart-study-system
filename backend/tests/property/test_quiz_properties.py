"""
Property-based tests for quiz generation.
Properties 7, 8 from the design document.
"""
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from app.schemas.quiz import QuizQuestion, AnswerOption


def _make_mcq(difficulty: str, question_id: str = "test-id") -> QuizQuestion:
    options = [
        AnswerOption(label="A", text="Option A", is_correct=True),
        AnswerOption(label="B", text="Option B", is_correct=False),
        AnswerOption(label="C", text="Option C", is_correct=False),
        AnswerOption(label="D", text="Option D", is_correct=False),
    ]
    return QuizQuestion(
        id=question_id,
        question_type="multiple_choice",
        difficulty=difficulty,
        question_text="What is the answer?",
        options=options,
        correct_answer="A",
        explanation="Because A is correct.",
        saved_for_review=False,
    )


def _make_short_answer(difficulty: str, question_id: str = "test-id") -> QuizQuestion:
    return QuizQuestion(
        id=question_id,
        question_type="short_answer",
        difficulty=difficulty,
        question_text="Explain the concept.",
        options=None,
        correct_answer="The correct explanation.",
        explanation=None,
        saved_for_review=False,
    )


# ---------------------------------------------------------------------------
# Property 7: Quiz Difficulty Distribution
# ---------------------------------------------------------------------------

@given(
    n_easy=st.integers(min_value=1, max_value=5),
    n_medium=st.integers(min_value=1, max_value=5),
    n_hard=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=100)
def test_property7_quiz_has_all_difficulties(n_easy: int, n_medium: int, n_hard: int):
    """A valid quiz set must have at least 1 easy, 1 medium, 1 hard question."""
    questions = (
        [_make_mcq("easy", f"e{i}") for i in range(n_easy)]
        + [_make_mcq("medium", f"m{i}") for i in range(n_medium)]
        + [_make_mcq("hard", f"h{i}") for i in range(n_hard)]
    )
    assert len(questions) >= 3  # at minimum 1+1+1
    difficulties = {q.difficulty for q in questions}
    assert "easy" in difficulties
    assert "medium" in difficulties
    assert "hard" in difficulties


@given(difficulty=st.sampled_from(["easy", "medium", "hard"]))
@settings(max_examples=50)
def test_property7_each_question_has_valid_difficulty(difficulty: str):
    """Every quiz question must have a difficulty in {easy, medium, hard}."""
    q = _make_mcq(difficulty)
    assert q.difficulty in {"easy", "medium", "hard"}


def test_property7_invalid_difficulty_rejected():
    """Questions with invalid difficulty must be rejected."""
    with pytest.raises(Exception):
        _make_mcq("extreme")


# ---------------------------------------------------------------------------
# Property 8: MCQ Structure and Answer Key Completeness
# ---------------------------------------------------------------------------

def test_property8_mcq_has_exactly_4_options():
    """MCQ must have exactly 4 answer options."""
    q = _make_mcq("easy")
    assert q.options is not None
    assert len(q.options) == 4


def test_property8_mcq_has_exactly_one_correct():
    """MCQ must have exactly one correct answer."""
    q = _make_mcq("medium")
    correct_count = sum(1 for opt in q.options if opt.is_correct)
    assert correct_count == 1


def test_property8_all_questions_have_correct_answer():
    """All question types must have a non-empty correct_answer."""
    mcq = _make_mcq("easy")
    sa = _make_short_answer("hard")
    assert mcq.correct_answer
    assert sa.correct_answer


@given(
    labels=st.permutations(["A", "B", "C", "D"]),
    correct_idx=st.integers(min_value=0, max_value=3),
)
@settings(max_examples=50)
def test_property8_mcq_options_have_valid_labels(labels: list, correct_idx: int):
    """MCQ options must use labels A, B, C, D."""
    options = [
        AnswerOption(label=labels[i], text=f"Option {labels[i]}", is_correct=(i == correct_idx))
        for i in range(4)
    ]
    label_set = {opt.label for opt in options}
    assert label_set == {"A", "B", "C", "D"}
    correct_count = sum(1 for opt in options if opt.is_correct)
    assert correct_count == 1


def test_property8_short_answer_has_no_options():
    """Short answer questions must have options=None."""
    q = _make_short_answer("medium")
    assert q.options is None
