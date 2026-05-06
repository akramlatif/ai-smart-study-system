import json
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import SESSION_TTL_SECONDS
from app.repositories.session import SessionRepository
from app.schemas.session import (
    Interaction,
    SessionSummary,
    StudySession,
)

MAX_INTERACTIONS = 50
SESSION_KEY_PREFIX = "session:"


def _session_key(session_id: str) -> str:
    return f"{SESSION_KEY_PREFIX}{session_id}"


def _serialize_session(session: StudySession) -> str:
    return session.model_dump_json()


def _deserialize_session(data: str) -> StudySession:
    return StudySession.model_validate_json(data)


async def create_session(
    user_id: str,
    db: AsyncSession,
    redis: Any,
) -> StudySession:
    """Create a new study session in Postgres/SQLite and cache it in Redis/memory."""
    repo = SessionRepository(db)
    db_session = await repo.create(user_id)

    now = datetime.now(timezone.utc)
    session = StudySession(
        id=str(db_session.id),
        user_id=user_id,
        previous_id=None,
        topics=[],
        explanations=[],
        quiz_questions=[],
        interactions=[],
        created_at=now,
        last_active=now,
    )

    await redis.setex(
        _session_key(str(db_session.id)),
        SESSION_TTL_SECONDS,
        _serialize_session(session),
    )
    return session


async def get_session(
    session_id: str,
    db: AsyncSession,
    redis: Any,
) -> StudySession | None:
    """Try Redis/memory first, fall back to Postgres/SQLite."""
    cached = await redis.get(_session_key(session_id))
    if cached:
        return _deserialize_session(cached)

    # Fallback: reconstruct from database
    repo = SessionRepository(db)
    db_session = await repo.get_by_id(session_id)
    if not db_session:
        return None

    now = datetime.now(timezone.utc)
    session = StudySession(
        id=str(db_session.id),
        user_id=str(db_session.user_id),
        previous_id=str(db_session.previous_id) if db_session.previous_id else None,
        topics=[],
        explanations=[],
        quiz_questions=[],
        interactions=[],
        created_at=db_session.created_at,
        last_active=now,
    )
    # Re-cache
    await redis.setex(
        _session_key(session_id),
        SESSION_TTL_SECONDS,
        _serialize_session(session),
    )
    return session


async def append_interaction(
    session_id: str,
    interaction: Interaction,
    redis: Any,
) -> None:
    """Append an interaction to the session in Redis and reset TTL."""
    cached = await redis.get(_session_key(session_id))
    if not cached:
        return

    session = _deserialize_session(cached)

    # Enforce max 50 interactions
    if len(session.interactions) >= MAX_INTERACTIONS:
        session.interactions = session.interactions[1:]  # drop oldest

    session.interactions.append(interaction)
    session.last_active = datetime.now(timezone.utc)

    await redis.setex(
        _session_key(session_id),
        SESSION_TTL_SECONDS,
        _serialize_session(session),
    )


async def reset_session(
    session_id: str,
    user_id: str,
    db: AsyncSession,
    redis: Any,
) -> StudySession:
    """End the current session and create a new one, preserving previous_id."""
    # End old session in database
    repo = SessionRepository(db)
    await repo.end_session(session_id)

    # Clear cache
    await redis.delete(_session_key(session_id))

    # Create new session with previous_id pointing to old session
    db_new = await repo.create(user_id=user_id, previous_id=session_id)

    now = datetime.now(timezone.utc)
    new_session = StudySession(
        id=str(db_new.id),
        user_id=user_id,
        previous_id=session_id,
        topics=[],
        explanations=[],
        quiz_questions=[],
        interactions=[],
        created_at=now,
        last_active=now,
    )

    await redis.setex(
        _session_key(str(db_new.id)),
        SESSION_TTL_SECONDS,
        _serialize_session(new_session),
    )
    return new_session


async def get_summary(
    session_id: str,
    db: AsyncSession,
    redis: Any,
) -> SessionSummary:
    """Build a session summary from Redis (or Postgres fallback)."""
    session = await get_session(session_id, db, redis)
    if not session:
        return SessionSummary(
            session_id=session_id,
            topics_studied=[],
            questions_asked=0,
            quiz_questions_generated=0,
            duration_minutes=0.0,
            interactions=[],
        )

    topics_studied = [t.main_topic for t in session.topics]
    questions_asked = sum(
        1 for i in session.interactions if i.role == "user"
    )
    quiz_questions_generated = len(session.quiz_questions)

    # Duration
    if session.interactions:
        first_ts = session.interactions[0].timestamp
        last_ts = session.interactions[-1].timestamp
        duration_minutes = (last_ts - first_ts).total_seconds() / 60.0
    else:
        duration_minutes = 0.0

    # Chronological order
    sorted_interactions = sorted(session.interactions, key=lambda i: i.timestamp)

    return SessionSummary(
        session_id=session_id,
        topics_studied=topics_studied,
        questions_asked=questions_asked,
        quiz_questions_generated=quiz_questions_generated,
        duration_minutes=duration_minutes,
        interactions=sorted_interactions,
    )


def build_context_window(session: StudySession) -> str:
    """
    Build a context string for AI prompts using a sliding window strategy:
    - Always include first interaction
    - Always include last 5 interactions
    - Include source excerpt (first 2000 chars of first user content)
    """
    interactions = session.interactions
    if not interactions:
        return ""

    lines: list[str] = []

    # First interaction
    first = interactions[0]
    lines.append(f"[{first.role.upper()}]: {first.content}")

    # Middle interactions (summarized if needed)
    if len(interactions) > 6:
        middle = interactions[1:-5]
        if middle:
            lines.append(f"[... {len(middle)} earlier interactions ...]")

    # Last 5 interactions
    last_five = interactions[-5:] if len(interactions) > 1 else []
    for interaction in last_five:
        if interaction != first:
            lines.append(f"[{interaction.role.upper()}]: {interaction.content}")

    # Source excerpt from first user message
    user_messages = [i for i in interactions if i.role == "user"]
    if user_messages:
        source_excerpt = user_messages[0].content[:2000]
        if len(user_messages[0].content) > 2000:
            lines.append(f"\n[Source excerpt]: {source_excerpt}...")
        else:
            lines.append(f"\n[Source excerpt]: {source_excerpt}")

    # Topic context
    if session.topics:
        topic = session.topics[-1]
        lines.append(f"\n[Current topic]: {topic.main_topic}")
        if topic.subtopics:
            lines.append(f"[Subtopics]: {', '.join(topic.subtopics)}")

    return "\n".join(lines)
