"""
Property-based tests for Feynman and Socratic learning modes.
Properties from the feynman-socratic-learning spec.
"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.schemas.feynman import FeynmanFeedback
from app.schemas.socratic import SocraticQuestion, SocraticComplete, SocraticResponse


# ---------------------------------------------------------------------------
# Property: Feynman Score Validity (score ∈ [0, 100])
# ---------------------------------------------------------------------------

@given(score=st.integers(min_value=0, max_value=100))
@settings(max_examples=100)
def test_feynman_score_in_valid_range(score: int):
    """FeynmanFeedback comprehension_score must be in [0, 100]."""
    feedback = FeynmanFeedback(
        comprehension_score=score,
        strengths=["Good understanding of basics"],
        gaps=[],
        misconceptions=[],
        simplified_correction="Corrected explanation.",
        encouragement_message="Keep going!",
    )
    assert 0 <= feedback.comprehension_score <= 100


@given(score=st.integers().filter(lambda x: x < 0 or x > 100))
@settings(max_examples=50)
def test_feynman_score_out_of_range_rejected(score: int):
    """FeynmanFeedback with score outside [0, 100] must be rejected."""
    with pytest.raises(Exception):
        FeynmanFeedback(
            comprehension_score=score,
            strengths=[],
            gaps=[],
            misconceptions=[],
            simplified_correction="",
            encouragement_message="",
        )


# ---------------------------------------------------------------------------
# Property: Feynman Feedback Completeness (strengths present if score > 30)
# ---------------------------------------------------------------------------

@given(score=st.integers(min_value=31, max_value=100))
@settings(max_examples=100)
def test_feynman_high_score_has_strengths(score: int):
    """When score > 30, strengths list must contain at least one item."""
    feedback = FeynmanFeedback(
        comprehension_score=score,
        strengths=["Correctly identified the main concept"],
        gaps=[],
        misconceptions=[],
        simplified_correction="Good explanation.",
        encouragement_message="Well done!",
    )
    assert len(feedback.strengths) >= 1


# ---------------------------------------------------------------------------
# Property: Socratic Question Type Validity
# ---------------------------------------------------------------------------

VALID_QUESTION_TYPES = {"probing", "clarifying", "hypothetical", "evaluative"}


@given(question_type=st.sampled_from(list(VALID_QUESTION_TYPES)))
@settings(max_examples=50)
def test_socratic_question_type_valid(question_type: str):
    """SocraticQuestion question_type must be one of the 4 valid types."""
    q = SocraticQuestion(
        question_text="What do you think about this?",
        question_type=question_type,
        depth_level=1,
    )
    assert q.question_type in VALID_QUESTION_TYPES


def test_socratic_invalid_question_type_rejected():
    """SocraticQuestion with invalid question_type must be rejected."""
    with pytest.raises(Exception):
        SocraticQuestion(
            question_text="What?",
            question_type="invalid_type",
            depth_level=1,
        )


# ---------------------------------------------------------------------------
# Property: Socratic Depth Monotonicity (depth never decreases, max 5)
# ---------------------------------------------------------------------------

@given(
    depths=st.lists(
        st.integers(min_value=1, max_value=5),
        min_size=2,
        max_size=10,
    ).filter(lambda d: all(d[i] <= d[i+1] for i in range(len(d)-1)))
)
@settings(max_examples=100)
def test_socratic_depth_monotonically_non_decreasing(depths: list):
    """Depth levels in a Socratic session must never decrease."""
    for i in range(len(depths) - 1):
        assert depths[i] <= depths[i + 1], "Depth must be non-decreasing"


@given(depth=st.integers(min_value=1, max_value=5))
@settings(max_examples=50)
def test_socratic_depth_in_valid_range(depth: int):
    """SocraticQuestion depth_level must be in [1, 5]."""
    q = SocraticQuestion(
        question_text="Why do you think that?",
        question_type="probing",
        depth_level=depth,
    )
    assert 1 <= q.depth_level <= 5


@given(depth=st.integers().filter(lambda x: x < 1 or x > 5))
@settings(max_examples=50)
def test_socratic_invalid_depth_rejected(depth: int):
    """SocraticQuestion with depth outside [1, 5] must be rejected."""
    with pytest.raises(Exception):
        SocraticQuestion(
            question_text="What?",
            question_type="probing",
            depth_level=depth,
        )


# ---------------------------------------------------------------------------
# Property: Socratic Completion Consistency
# ---------------------------------------------------------------------------

@given(
    depth_reached=st.integers(min_value=1, max_value=5),
    n_insights=st.integers(min_value=3, max_value=8),
)
@settings(max_examples=50)
def test_socratic_completion_has_required_fields(depth_reached: int, n_insights: int):
    """SocraticComplete must have summary, key_insights (>=3), and depth_reached."""
    insights = [f"Insight {i}" for i in range(n_insights)]
    completion = SocraticComplete(
        summary="A" * 150,  # at least 100 chars
        key_insights=insights,
        depth_reached=depth_reached,
    )
    assert len(completion.summary) >= 100
    assert len(completion.key_insights) >= 3
    assert 1 <= completion.depth_reached <= 5


def test_socratic_response_complete_has_completion():
    """SocraticResponse with is_complete=True must have completion field."""
    completion = SocraticComplete(
        summary="A" * 150,
        key_insights=["Insight 1", "Insight 2", "Insight 3"],
        depth_reached=5,
    )
    response = SocraticResponse(
        is_complete=True,
        question=None,
        completion=completion,
    )
    assert response.is_complete is True
    assert response.completion is not None
    assert response.completion.depth_reached == 5


def test_socratic_response_incomplete_has_question():
    """SocraticResponse with is_complete=False must have question field."""
    question = SocraticQuestion(
        question_text="Why do you think that?",
        question_type="probing",
        depth_level=2,
    )
    response = SocraticResponse(
        is_complete=False,
        question=question,
        completion=None,
    )
    assert response.is_complete is False
    assert response.question is not None
    assert response.question.depth_level == 2
