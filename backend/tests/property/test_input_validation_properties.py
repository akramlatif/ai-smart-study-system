"""
Property-based tests for input validation.
Properties 1, 2, 12, 13 from the design document.
"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.services.input_handler import validate_text, validate_file, detect_shortcut
from app.services.content_extractor import assess_quality


# ---------------------------------------------------------------------------
# Property 1: Input Length Validation
# ---------------------------------------------------------------------------

@given(st.text(min_size=0, max_size=600))
@settings(max_examples=200)
def test_property1_question_length_validation(text: str):
    """For any text, validate_text(question) accepts iff trimmed length is 3-500."""
    result = validate_text(text, input_type="question")
    trimmed = text.strip()
    length = len(trimmed)

    if length == 0:
        assert not result.valid
        assert result.error_code == "INPUT_EMPTY"
    elif length < 3:
        assert not result.valid
        assert result.error_code == "INPUT_TOO_SHORT"
    elif length > 500:
        assert not result.valid
        assert result.error_code == "INPUT_TOO_LONG"
    else:
        assert result.valid


@given(st.text(min_size=0, max_size=11000))
@settings(max_examples=200)
def test_property1_notes_length_validation(text: str):
    """For any text, validate_text(notes) accepts iff trimmed length is 3-10000."""
    result = validate_text(text, input_type="notes")
    trimmed = text.strip()
    length = len(trimmed)

    if length == 0:
        assert not result.valid
        assert result.error_code == "INPUT_EMPTY"
    elif length < 3:
        assert not result.valid
        assert result.error_code == "INPUT_TOO_SHORT"
    elif length > 10_000:
        assert not result.valid
        assert result.error_code == "INPUT_TOO_LONG"
    else:
        assert result.valid


# ---------------------------------------------------------------------------
# Property 2: Input Preservation Round-Trip
# ---------------------------------------------------------------------------

@given(st.text(min_size=3, max_size=500).filter(lambda t: len(t.strip()) >= 3))
@settings(max_examples=100)
def test_property2_valid_input_is_accepted(text: str):
    """Any text with trimmed length 3-500 must be accepted as a valid question."""
    result = validate_text(text, input_type="question")
    trimmed = text.strip()
    if 3 <= len(trimmed) <= 500:
        assert result.valid
        assert result.error_code is None


# ---------------------------------------------------------------------------
# Property 12: Shortcut Phrase Recognition
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("phrase", [
    "simplify this",
    "explain simply",
    "make it easier",
    "simplify",
    "Please simplify this for me",
    "Can you make it easier to understand?",
])
def test_property12_simplify_shortcuts_detected(phrase: str):
    """All simplification shortcut phrases must be classified as 'simplify'."""
    result = detect_shortcut(phrase)
    assert result == "simplify", f"Expected 'simplify' for '{phrase}', got '{result}'"


@pytest.mark.parametrize("phrase", [
    "go deeper",
    "more advanced",
    "technical details",
    "I want to go deeper into this",
    "Give me more advanced content",
])
def test_property12_deepen_shortcuts_detected(phrase: str):
    """All depth shortcut phrases must be classified as 'deepen'."""
    result = detect_shortcut(phrase)
    assert result == "deepen", f"Expected 'deepen' for '{phrase}', got '{result}'"


@pytest.mark.parametrize("phrase", [
    "hard questions",
    "hard quiz",
    "difficult questions",
    "Give me hard questions from this topic",
])
def test_property12_hard_quiz_shortcuts_detected(phrase: str):
    """All hard quiz shortcut phrases must be classified as 'hard_quiz'."""
    result = detect_shortcut(phrase)
    assert result == "hard_quiz", f"Expected 'hard_quiz' for '{phrase}', got '{result}'"


@given(st.text(min_size=1, max_size=200).filter(
    lambda t: not any(p in t.lower() for p in [
        "simplify", "explain simply", "make it easier",
        "go deeper", "more advanced", "technical details",
        "hard questions", "hard quiz", "difficult questions",
    ])
))
@settings(max_examples=100)
def test_property12_non_shortcut_returns_none(text: str):
    """Text without shortcut patterns must return None."""
    result = detect_shortcut(text)
    assert result is None


# ---------------------------------------------------------------------------
# Property 13: Document Quality Flag Threshold
# ---------------------------------------------------------------------------

@given(st.text(min_size=0, max_size=200))
@settings(max_examples=200)
def test_property13_quality_flag_threshold(text: str):
    """
    For any text:
    - char_count < 50 → quality_flag == 'low_quality'
    - char_count >= 50 → quality_flag == 'ok'
    """
    result = assess_quality(text)
    assert result.char_count == len(text)

    if len(text) < 50:
        assert result.flag == "low_quality"
        assert result.message is not None
    else:
        assert result.flag == "ok"
        assert result.message is None


@given(st.integers(min_value=0, max_value=49))
@settings(max_examples=50)
def test_property13_short_text_always_low_quality(length: int):
    """Any text shorter than 50 chars must be flagged as low_quality."""
    text = "a" * length
    result = assess_quality(text)
    assert result.flag == "low_quality"


@given(st.integers(min_value=50, max_value=10000))
@settings(max_examples=50)
def test_property13_sufficient_text_always_ok(length: int):
    """Any text of 50+ chars must be flagged as ok."""
    text = "a" * length
    result = assess_quality(text)
    assert result.flag == "ok"
