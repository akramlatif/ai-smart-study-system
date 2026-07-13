import pytest
from app.services.spaced_repetition import calculate_sm2

def test_sm2_correct_answer_initial():
    """First correct answer should set interval to 1"""
    next_interval, new_ease = calculate_sm2(is_correct=True, current_interval=0, current_ease=2.5)
    assert next_interval == 1
    assert new_ease > 2.5  # quality 4 increases ease slightly

def test_sm2_correct_answer_second_time():
    """Second correct answer should set interval to 6"""
    next_interval, new_ease = calculate_sm2(is_correct=True, current_interval=1, current_ease=2.5)
    assert next_interval == 6

def test_sm2_correct_answer_streak():
    """Subsequent correct answers multiply interval by ease factor"""
    next_interval, new_ease = calculate_sm2(is_correct=True, current_interval=6, current_ease=2.6)
    assert next_interval == int(6 * 2.6) # 15

def test_sm2_incorrect_answer_resets_streak():
    """Incorrect answer should set interval back to 1 and reduce ease"""
    next_interval, new_ease = calculate_sm2(is_correct=False, current_interval=15, current_ease=2.6)
    assert next_interval == 1
    assert new_ease < 2.6

def test_sm2_ease_factor_floor():
    """Ease factor should never drop below 1.3"""
    # Force many incorrect answers
    ease = 1.4
    for _ in range(5):
        _, ease = calculate_sm2(is_correct=False, current_interval=1, current_ease=ease)
    
    assert ease == 1.3

def test_sm2_ease_factor_ceiling():
    """Ease factor should not exceed 10.0"""
    ease = 9.9
    for _ in range(5):
        _, ease = calculate_sm2(is_correct=True, current_interval=1, current_ease=ease, quality_modifier=1.0)
    
    assert ease == 10.0

def test_sm2_quality_modifier_increases_ease():
    """Higher quality modifier (confident) increases ease more than standard correct answer"""
    _, ease_normal = calculate_sm2(is_correct=True, current_interval=0, current_ease=2.5)
    _, ease_high = calculate_sm2(is_correct=True, current_interval=0, current_ease=2.5, quality_modifier=1.0)
    assert ease_high > ease_normal

def test_sm2_quality_modifier_decreases_ease():
    """Lower quality modifier (hesitant) decreases ease compared to standard correct answer"""
    _, ease_normal = calculate_sm2(is_correct=True, current_interval=0, current_ease=2.5)
    _, ease_low = calculate_sm2(is_correct=True, current_interval=0, current_ease=2.5, quality_modifier=-1.0)
    assert ease_low < ease_normal
