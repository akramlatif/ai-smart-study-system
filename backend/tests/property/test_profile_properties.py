"""
Property-based tests for the adaptive learner profile mastery calculation.

Tests the pure functions in learner_profile.py:
- Property 1: mastery_level never jumps past "learning" with fewer than
              MIN_ATTEMPTS_FOR_UPGRADE attempts (single lucky guess protection)
- Property 2: mastery_level monotonically increases (or stays flat) as accuracy
              goes up, provided minimum sample size is met
- Property 3: 0 attempts always yields "not_started"
- Property 4: preferred_difficulty follows documented thresholds
"""
from hypothesis import given, settings, assume
import hypothesis.strategies as st

from app.services.learner_profile import (
    compute_mastery_level,
    compute_preferred_difficulty,
    MIN_ATTEMPTS_FOR_UPGRADE,
    MASTERED_ACCURACY,
    PRACTICED_ACCURACY,
    DIFFICULTY_UPGRADE_ACCURACY,
    DIFFICULTY_DOWNGRADE_ACCURACY,
)

# Ordered mastery levels for comparison
_MASTERY_ORDER = {
    "not_started": 0,
    "learning": 1,
    "practiced": 2,
    "mastered": 3,
}


# ---------------------------------------------------------------------------
# Property 1: A single lucky guess (total < MIN_ATTEMPTS_FOR_UPGRADE) can
# NEVER produce a level higher than "learning", regardless of accuracy.
# ---------------------------------------------------------------------------
@given(
    total=st.integers(min_value=1, max_value=MIN_ATTEMPTS_FOR_UPGRADE - 1),
    accuracy=st.floats(min_value=0.0, max_value=1.0),
)
@settings(max_examples=200)
def test_property1_single_guess_never_upgrades_past_learning(total, accuracy):
    """With fewer than MIN_ATTEMPTS_FOR_UPGRADE attempts, mastery must be 'learning'."""
    level = compute_mastery_level(total, accuracy)
    assert _MASTERY_ORDER[level] <= _MASTERY_ORDER["learning"]


# ---------------------------------------------------------------------------
# Property 2: Mastery is monotonically non-decreasing with accuracy, when
# sample size is sufficient.
# ---------------------------------------------------------------------------
@given(
    total=st.integers(min_value=MIN_ATTEMPTS_FOR_UPGRADE, max_value=200),
    accuracy_low=st.floats(min_value=0.0, max_value=1.0),
    accuracy_high=st.floats(min_value=0.0, max_value=1.0),
)
@settings(max_examples=200)
def test_property2_mastery_monotonically_increases_with_accuracy(total, accuracy_low, accuracy_high):
    """Higher accuracy should never produce a *lower* mastery level."""
    assume(accuracy_high >= accuracy_low)

    level_low = compute_mastery_level(total, accuracy_low)
    level_high = compute_mastery_level(total, accuracy_high)

    assert _MASTERY_ORDER[level_high] >= _MASTERY_ORDER[level_low]


# ---------------------------------------------------------------------------
# Property 3: 0 attempts → "not_started", always.
# ---------------------------------------------------------------------------
@given(accuracy=st.floats(min_value=0.0, max_value=1.0))
@settings(max_examples=50)
def test_property3_zero_attempts_always_not_started(accuracy):
    """Zero attempts must always yield 'not_started'."""
    assert compute_mastery_level(0, accuracy) == "not_started"


# ---------------------------------------------------------------------------
# Property 4: preferred_difficulty follows thresholds correctly.
# ---------------------------------------------------------------------------
@given(
    accuracy=st.floats(min_value=0.0, max_value=1.0),
    total=st.integers(min_value=1, max_value=100),
)
@settings(max_examples=200)
def test_property4_preferred_difficulty_follows_thresholds(accuracy, total):
    """The difficulty recommendation must follow the documented thresholds."""
    result = compute_preferred_difficulty(accuracy, total)

    if accuracy > DIFFICULTY_UPGRADE_ACCURACY:
        assert result == "hard"
    elif accuracy < DIFFICULTY_DOWNGRADE_ACCURACY:
        assert result == "easy"
    else:
        assert result == "medium"


def test_property4_no_medium_attempts_defaults_to_medium():
    """With zero medium attempts, difficulty must default to 'medium'."""
    assert compute_preferred_difficulty(0.99, 0) == "medium"
    assert compute_preferred_difficulty(0.01, 0) == "medium"
