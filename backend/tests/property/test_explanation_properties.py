"""
Property-based tests for explanation generation.
Properties 5, 6 from the design document.
"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.schemas.explanation import ExplanationContent, ExplanationSet


def _make_content(level: str, word_count: int) -> ExplanationContent:
    content = " ".join(["word"] * word_count)
    return ExplanationContent(
        level=level,
        content=content,
        word_count=word_count,
        source_references=[],
    )


# ---------------------------------------------------------------------------
# Property 5: Explanation Word Count Bounds
# ---------------------------------------------------------------------------

@given(word_count=st.integers(min_value=150, max_value=300))
@settings(max_examples=100)
def test_property5_basic_word_count_in_bounds(word_count: int):
    """Basic explanation word count must be in [150, 300]."""
    content = _make_content("basic", word_count)
    assert 150 <= content.word_count <= 300


@given(word_count=st.integers(min_value=300, max_value=500))
@settings(max_examples=100)
def test_property5_intermediate_word_count_in_bounds(word_count: int):
    """Intermediate explanation word count must be in [300, 500]."""
    content = _make_content("intermediate", word_count)
    assert 300 <= content.word_count <= 500


@given(word_count=st.integers(min_value=400, max_value=700))
@settings(max_examples=100)
def test_property5_advanced_word_count_in_bounds(word_count: int):
    """Advanced explanation word count must be in [400, 700]."""
    content = _make_content("advanced", word_count)
    assert 400 <= content.word_count <= 700


# ---------------------------------------------------------------------------
# Property 6: Explanation Set Completeness
# ---------------------------------------------------------------------------

@given(
    basic_wc=st.integers(min_value=150, max_value=300),
    intermediate_wc=st.integers(min_value=300, max_value=500),
    advanced_wc=st.integers(min_value=400, max_value=700),
    topic_id=st.uuids().map(str),
)
@settings(max_examples=100)
def test_property6_explanation_set_has_all_three_levels(
    basic_wc: int, intermediate_wc: int, advanced_wc: int, topic_id: str
):
    """ExplanationSet must contain all three levels with non-empty content."""
    explanation_set = ExplanationSet(
        topic_id=topic_id,
        basic=_make_content("basic", basic_wc),
        intermediate=_make_content("intermediate", intermediate_wc),
        advanced=_make_content("advanced", advanced_wc),
    )
    assert explanation_set.basic is not None
    assert explanation_set.intermediate is not None
    assert explanation_set.advanced is not None
    assert len(explanation_set.basic.content) > 0
    assert len(explanation_set.intermediate.content) > 0
    assert len(explanation_set.advanced.content) > 0
    assert explanation_set.basic.level == "basic"
    assert explanation_set.intermediate.level == "intermediate"
    assert explanation_set.advanced.level == "advanced"


def test_property6_missing_level_raises():
    """ExplanationSet missing any level must fail validation."""
    with pytest.raises(Exception):
        ExplanationSet(
            topic_id="test-id",
            basic=_make_content("basic", 200),
            intermediate=_make_content("intermediate", 400),
            # missing advanced
        )
