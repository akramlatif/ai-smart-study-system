import pytest
from hypothesis import given, settings
import hypothesis.strategies as st
from app.repositories.attempt import _compute_sm2


# Property A: After any correct answer: next_interval_days > current_interval (for non-zero intervals)
@given(
    current_interval=st.integers(min_value=1, max_value=365),
    current_ease=st.floats(min_value=1.3, max_value=10.0),
)
@settings(max_examples=100)
def test_property_a_correct_increases_interval(current_interval, current_ease):
    next_interval, new_ease = _compute_sm2(
        is_correct=True,
        current_interval=current_interval,
        current_ease=current_ease
    )
    
    assert next_interval > current_interval


# Property B: After any incorrect answer: interval resets to 1 and ease factor decreases
@given(
    current_interval=st.integers(min_value=1, max_value=365),
    current_ease=st.floats(min_value=1.3, max_value=10.0),
)
@settings(max_examples=100)
def test_property_b_incorrect_resets_interval(current_interval, current_ease):
    next_interval, new_ease = _compute_sm2(
        is_correct=False,
        current_interval=current_interval,
        current_ease=current_ease
    )
    
    assert next_interval == 1
    # Check it decreased, unless it hit the floor
    if current_ease > 1.3:
        # floating point math might make it almost equal to 1.3
        assert new_ease < current_ease or new_ease == 1.3


# Property C: ease_factor never goes below 1.3 or above 10.0
@given(
    is_correct=st.booleans(),
    current_interval=st.integers(min_value=0, max_value=1000),
    current_ease=st.floats(min_value=1.3, max_value=10.0),
)
@settings(max_examples=100)
def test_property_c_ease_factor_bounds(is_correct, current_interval, current_ease):
    next_interval, new_ease = _compute_sm2(
        is_correct=is_correct,
        current_interval=current_interval,
        current_ease=current_ease
    )
    
    assert 1.3 <= new_ease <= 10.0
