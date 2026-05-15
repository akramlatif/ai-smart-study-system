"""Unit tests for SessionManager service."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.session_manager import (
    build_context_window,
    _session_key,
    MAX_INTERACTIONS,
)
from app.schemas.session import StudySession, Interaction
from app.schemas.topic import TopicAnalysis


def _make_session(session_id: str = "test-session-id", user_id: str = "test-user") -> StudySession:
    now = datetime.now(timezone.utc)
    return StudySession(
        id=session_id,
        user_id=user_id,
        previous_id=None,
        topics=[],
        explanations=[],
        quiz_questions=[],
        interactions=[],
        created_at=now,
        last_active=now,
    )


def _make_interaction(index: int, role: str, content: str) -> Interaction:
    return Interaction(
        index=index,
        role=role,
        content=content,
        input_type="text",
        timestamp=datetime.now(timezone.utc) + timedelta(seconds=index),
    )


class TestSessionKey:
    def test_session_key_format(self):
        key = _session_key("abc-123")
        assert key == "session:abc-123"


class TestBuildContextWindow:
    def test_empty_session_returns_empty_string(self):
        session = _make_session()
        result = build_context_window(session)
        assert result == ""

    def test_single_interaction_included(self):
        session = _make_session()
        session.interactions = [_make_interaction(1, "user", "What is quantum physics?")]
        result = build_context_window(session)
        assert "What is quantum physics?" in result
        assert "[USER]" in result

    def test_topic_context_included(self):
        session = _make_session()
        session.interactions = [_make_interaction(1, "user", "Explain quantum physics")]
        session.topics = [
            TopicAnalysis(
                main_topic="Quantum Physics",
                subtopics=["Superposition", "Entanglement"],
                confidence=0.95,
                needs_clarification=False,
            )
        ]
        result = build_context_window(session)
        assert "Quantum Physics" in result
        assert "Superposition" in result

    def test_first_and_last_five_included(self):
        session = _make_session()
        # Create 10 interactions
        session.interactions = [
            _make_interaction(i, "user" if i % 2 == 0 else "assistant", f"Message {i}")
            for i in range(1, 11)
        ]
        result = build_context_window(session)
        # First interaction must be included
        assert "Message 1" in result
        # Last 5 must be included
        assert "Message 10" in result
        assert "Message 9" in result

    def test_middle_interactions_summarized(self):
        session = _make_session()
        # Create 10 interactions
        session.interactions = [
            _make_interaction(i, "user", f"Message {i}")
            for i in range(1, 11)
        ]
        result = build_context_window(session)
        # Middle interactions should be summarized
        assert "earlier interactions" in result

    def test_source_excerpt_included(self):
        session = _make_session()
        long_content = "This is a very long note about quantum physics. " * 50
        session.interactions = [_make_interaction(1, "user", long_content)]
        result = build_context_window(session)
        assert "Source excerpt" in result
