import pytest
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import Base
from app.repositories.attempt import AttemptRepository
from app.models.user import User
from app.models.session import StudySession


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_attempt_and_spaced_repetition(async_session):
    # Setup dependencies
    user = User(email="test@example.com", name="Test User", hashed_password="pw")
    async_session.add(user)
    await async_session.flush()

    study_session = StudySession(user_id=user.id)
    async_session.add(study_session)
    await async_session.flush()

    repo = AttemptRepository(async_session)

    # Test create
    attempt = await repo.create(
        user_id=user.id,
        session_id=study_session.id,
        topic_id=None,
        source_mode="quiz",
        difficulty="medium",
        is_correct=True,
        score=1.0,
    )
    
    assert attempt.id is not None
    assert attempt.source_mode == "quiz"
    assert attempt.review_interval_days == 6  # 1 -> 6 for correct in our simple logic
    assert attempt.next_review_at is not None
    assert attempt.next_review_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_get_due_for_review(async_session):
    user = User(email="test2@example.com", name="Test User", hashed_password="pw")
    async_session.add(user)
    await async_session.flush()

    study_session = StudySession(user_id=user.id)
    async_session.add(study_session)
    await async_session.flush()

    repo = AttemptRepository(async_session)

    attempt = await repo.create(
        user_id=user.id,
        session_id=study_session.id,
        topic_id=None,
        source_mode="quiz",
        difficulty="hard",
        is_correct=False, # Interval -> 1
        score=0.0,
    )

    # Move next_review_at to the past to simulate due
    attempt.next_review_at = datetime.now(timezone.utc) - timedelta(days=2)
    await async_session.commit()

    due = await repo.get_due_for_review(user.id)
    assert len(due) == 1
    assert due[0].id == attempt.id


@pytest.mark.asyncio
async def test_get_topic_performance(async_session):
    user = User(email="test3@example.com", name="Test User", hashed_password="pw")
    async_session.add(user)
    await async_session.flush()

    study_session = StudySession(user_id=user.id)
    async_session.add(study_session)
    await async_session.flush()
    
    topic_id = str(uuid.uuid4())

    repo = AttemptRepository(async_session)

    await repo.create(user.id, study_session.id, topic_id, "quiz", "easy", True, 1.0)
    await repo.create(user.id, study_session.id, topic_id, "quiz", "hard", False, 0.0)
    await repo.create(user.id, study_session.id, topic_id, "feynman", "medium", None, 0.8) # Correct

    perf = await repo.get_topic_performance(user.id, topic_id)
    assert perf["total_attempts"] == 3
    assert perf["correct_attempts"] == 2  # (1 True) + (1 score >= 0.8) -> wait, does SQLite sum booleans?
    # Actually, SQLAlchemy might return integers for count/sum. Let's verify by just asserting greater than 0
    assert perf["accuracy"] == 2 / 3
    assert perf["avg_score"] == (1.0 + 0.0 + 0.8) / 3

@pytest.mark.asyncio
async def test_get_recent_attempts(async_session):
    user = User(email="test4@example.com", name="Test User", hashed_password="pw")
    async_session.add(user)
    await async_session.flush()
    study_session = StudySession(user_id=user.id)
    async_session.add(study_session)
    await async_session.flush()

    repo = AttemptRepository(async_session)
    for _ in range(5):
        await repo.create(user.id, study_session.id, None, "quiz", "medium", True, 1.0)
    
    recent = await repo.get_recent_attempts(user.id, limit=3)
    assert len(recent) == 3
