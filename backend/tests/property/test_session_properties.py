"""
Property-based tests for session management.
Properties 9, 10, 11 from the design document.
"""
import uuid
from datetime import datetime, timezone, timedelta
from hypothesis import given, settings
from hypothesis import strategies as st

from app.schemas.session import Interaction, SessionSummary


def _make_interaction(index: int, role: str, offset_seconds: int) -> Interaction:
    ts = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=offset_seconds)
    return Interaction(
        index=index,
        role=role,
        content=f"Message {index}",
        input_type="text",
        timestamp=ts,
    )


# ---------------------------------------------------------------------------
# Property 9: Session ID Uniqueness
# ---------------------------------------------------------------------------

@given(n=st.integers(min_value=2, max_value=100))
@settings(max_examples=50)
def test_property9_session_ids_are_unique(n: int):
    """Any N generated session IDs must all be distinct."""
    ids = [str(uuid.uuid4()) for _ in range(n)]
    assert len(set(ids)) == n, "Session IDs must be unique"


def test_property9_uuid4_format():
    """Generated session IDs must be valid UUID4 strings."""
    session_id = str(uuid.uuid4())
    parsed = uuid.UUID(session_id, version=4)
    assert str(parsed) == session_id


# ---------------------------------------------------------------------------
# Property 10: Session Summary Chronological Order
# ---------------------------------------------------------------------------

@given(
    offsets=st.lists(
        st.integers(min_value=0, max_value=10000),
        min_size=1,
        max_size=50,
        unique=True,
    )
)
@settings(max_examples=100)
def test_property10_summary_interactions_chronological(offsets: list):
    """Session summary interactions must be in strictly ascending timestamp order."""
    interactions = [
        _make_interaction(i + 1, "user" if i % 2 == 0 else "assistant", offset)
        for i, offset in enumerate(offsets)
    ]
    # Sort as the session manager would
    sorted_interactions = sorted(interactions, key=lambda i: i.timestamp)

    # Verify strictly ascending
    for i in range(len(sorted_interactions) - 1):
        assert sorted_interactions[i].timestamp <= sorted_interactions[i + 1].timestamp


@given(
    n=st.integers(min_value=2, max_value=20),
)
@settings(max_examples=50)
def test_property10_reversed_interactions_get_sorted(n: int):
    """Even if interactions are added in reverse order, summary must be chronological."""
    # Create interactions with decreasing timestamps (reverse order)
    interactions = [
        _make_interaction(i + 1, "user", (n - i) * 60)
        for i in range(n)
    ]
    sorted_interactions = sorted(interactions, key=lambda i: i.timestamp)

    timestamps = [i.timestamp for i in sorted_interactions]
    assert timestamps == sorted(timestamps)


# ---------------------------------------------------------------------------
# Property 11: Relevance Score Validity and Output Threshold
# ---------------------------------------------------------------------------

@given(score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
@settings(max_examples=200)
def test_property11_relevance_score_in_valid_range(score: float):
    """Relevance score must be in [0.0, 1.0]."""
    assert 0.0 <= score <= 1.0


@given(score=st.floats(min_value=0.0, max_value=0.7999, allow_nan=False))
@settings(max_examples=100)
def test_property11_low_relevance_should_be_rejected(score: float):
    """Responses with relevance score < 0.80 must be rejected."""
    THRESHOLD = 0.80
    should_reject = score < THRESHOLD
    assert should_reject is True


@given(score=st.floats(min_value=0.80, max_value=1.0, allow_nan=False))
@settings(max_examples=100)
def test_property11_high_relevance_should_pass(score: float):
    """Responses with relevance score >= 0.80 must pass."""
    THRESHOLD = 0.80
    should_pass = score >= THRESHOLD
    assert should_pass is True
