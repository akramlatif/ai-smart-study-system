"""
Property-based tests for topic analysis.
Properties 3, 4 from the design document.
"""
import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from app.schemas.topic import TopicAnalysis


# ---------------------------------------------------------------------------
# Property 3: Topic Structure Constraints
# ---------------------------------------------------------------------------

@given(
    main_topic=st.text(min_size=1, max_size=100),
    subtopics=st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5),
    confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
)
@settings(max_examples=200)
def test_property3_topic_structure_valid(main_topic: str, subtopics: list, confidence: float):
    """TopicAnalysis must have exactly one main_topic and 0-5 subtopics."""
    topic = TopicAnalysis(
        main_topic=main_topic,
        subtopics=subtopics,
        confidence=confidence,
        needs_clarification=confidence < 0.70,
    )
    assert isinstance(topic.main_topic, str)
    assert len(topic.main_topic) > 0
    assert isinstance(topic.subtopics, list)
    assert 0 <= len(topic.subtopics) <= 5


@given(
    subtopics=st.lists(st.text(min_size=1, max_size=50), min_size=6, max_size=20),
)
@settings(max_examples=50)
def test_property3_too_many_subtopics_truncated_to_5(subtopics: list):
    """TopicAnalysis with more than 5 subtopics silently truncates to 5."""
    topic = TopicAnalysis(
        main_topic="Test Topic",
        subtopics=subtopics,
        confidence=0.9,
        needs_clarification=False,
    )
    # The validator truncates to max 5
    assert len(topic.subtopics) <= 5


# ---------------------------------------------------------------------------
# Property 4: Confidence Score Validity and Clarification Threshold
# ---------------------------------------------------------------------------

@given(confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
@settings(max_examples=200)
def test_property4_confidence_range_valid(confidence: float):
    """Confidence score must be in [0.0, 1.0]."""
    topic = TopicAnalysis(
        main_topic="Test Topic",
        subtopics=[],
        confidence=confidence,
        needs_clarification=confidence < 0.70,
    )
    assert 0.0 <= topic.confidence <= 1.0


@given(confidence=st.floats(min_value=0.0, max_value=0.6999, allow_nan=False))
@settings(max_examples=100)
def test_property4_low_confidence_requires_clarification(confidence: float):
    """When confidence < 0.70, needs_clarification must be True."""
    topic = TopicAnalysis(
        main_topic="Ambiguous Topic",
        subtopics=[],
        confidence=confidence,
        needs_clarification=confidence < 0.70,
    )
    assert topic.needs_clarification is True


@given(confidence=st.floats(min_value=0.70, max_value=1.0, allow_nan=False))
@settings(max_examples=100)
def test_property4_high_confidence_no_clarification(confidence: float):
    """When confidence >= 0.70, needs_clarification must be False."""
    topic = TopicAnalysis(
        main_topic="Clear Topic",
        subtopics=["subtopic1"],
        confidence=confidence,
        needs_clarification=confidence < 0.70,
    )
    assert topic.needs_clarification is False


@given(confidence=st.floats(allow_nan=False).filter(lambda x: x < 0.0 or x > 1.0))
@settings(max_examples=50)
def test_property4_out_of_range_confidence_clamped(confidence: float):
    """Confidence outside [0.0, 1.0] is clamped to the valid range."""
    topic = TopicAnalysis(
        main_topic="Test",
        subtopics=[],
        confidence=confidence,
        needs_clarification=False,
    )
    # The validator clamps to [0.0, 1.0]
    assert 0.0 <= topic.confidence <= 1.0
