"""
LearnerProfileService — computes adaptive learner profiles from attempt history.

Mastery thresholds are documented as constants below. The service is designed
to be backward-compatible: if a user has no attempt history, every topic
defaults to "not_started" and difficulty defaults to "medium".
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.attempt import AttemptRepository
from app.schemas.profile import LearnerProfile, TopicMastery

# ---------------------------------------------------------------------------
# Mastery-level constants (documented thresholds)
# ---------------------------------------------------------------------------
# Minimum number of attempts before a topic can be promoted past "learning".
# This prevents a single lucky guess from upgrading mastery.
MIN_ATTEMPTS_FOR_UPGRADE = 3

# Accuracy thresholds for each mastery tier (requires MIN_ATTEMPTS_FOR_UPGRADE)
MASTERED_ACCURACY = 0.85     # >= 85% accuracy → mastered
PRACTICED_ACCURACY = 0.60    # >= 60% accuracy → practiced

# Weak / strong topic thresholds
WEAK_THRESHOLD = 0.60        # accuracy < 60% across all attempts → weak
STRONG_THRESHOLD = 0.85      # accuracy > 85% across all attempts → strong

# Difficulty recommendation thresholds (based on recent accuracy at medium)
DIFFICULTY_UPGRADE_ACCURACY = 0.80   # > 80% on medium → recommend hard
DIFFICULTY_DOWNGRADE_ACCURACY = 0.40 # < 40% on medium → recommend easy

# How many recent attempts to inspect for difficulty inference
RECENT_ATTEMPTS_WINDOW = 20


# ---------------------------------------------------------------------------
# Pure functions (testable without DB)
# ---------------------------------------------------------------------------

def compute_mastery_level(total_attempts: int, accuracy: float) -> str:
    """
    Derive mastery level from attempt count and accuracy.

    Rules:
    - "not_started"  → 0 attempts
    - "learning"     → >0 attempts but fewer than MIN_ATTEMPTS_FOR_UPGRADE,
                        OR accuracy < PRACTICED_ACCURACY
    - "practiced"    → >= MIN_ATTEMPTS_FOR_UPGRADE attempts AND accuracy >= 0.60
    - "mastered"     → >= MIN_ATTEMPTS_FOR_UPGRADE attempts AND accuracy >= 0.85
    """
    if total_attempts == 0:
        return "not_started"

    if total_attempts < MIN_ATTEMPTS_FOR_UPGRADE:
        return "learning"

    if accuracy >= MASTERED_ACCURACY:
        return "mastered"
    if accuracy >= PRACTICED_ACCURACY:
        return "practiced"

    return "learning"


def compute_preferred_difficulty(medium_accuracy: float, medium_total: int) -> str:
    """
    Infer the next recommended difficulty from recent performance on "medium".

    - If no medium attempts exist yet → default "medium"
    - If accuracy > 80% → recommend "hard"
    - If accuracy < 40% → recommend "easy"
    - Otherwise → keep "medium"
    """
    if medium_total == 0:
        return "medium"
    if medium_accuracy > DIFFICULTY_UPGRADE_ACCURACY:
        return "hard"
    if medium_accuracy < DIFFICULTY_DOWNGRADE_ACCURACY:
        return "easy"
    return "medium"


# ---------------------------------------------------------------------------
# Async service (requires DB session)
# ---------------------------------------------------------------------------

class LearnerProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.attempt_repo = AttemptRepository(db)

    async def build_profile(self, user_id: str) -> LearnerProfile:
        """Compute the full adaptive learner profile for a user."""

        # 1. Get all topics the user has attempted
        topic_ids = await self.attempt_repo.get_all_topic_ids(user_id)

        # 2. Per-topic mastery
        topic_mastery: list[TopicMastery] = []
        weak_topics: list[str] = []
        strong_topics: list[str] = []

        for tid in topic_ids:
            perf = await self.attempt_repo.get_topic_performance(user_id, tid)
            total = perf["total_attempts"]
            accuracy = perf["accuracy"]

            mastery = compute_mastery_level(total, accuracy)
            topic_mastery.append(TopicMastery(topic_id=tid, mastery_level=mastery))

            if total > 0 and accuracy < WEAK_THRESHOLD:
                weak_topics.append(tid)
            if total >= MIN_ATTEMPTS_FOR_UPGRADE and accuracy > STRONG_THRESHOLD:
                strong_topics.append(tid)

        # 3. Preferred difficulty (from recent medium-difficulty accuracy)
        medium_stats = await self.attempt_repo.get_accuracy_by_difficulty(
            user_id, "medium", limit=RECENT_ATTEMPTS_WINDOW
        )
        preferred = compute_preferred_difficulty(
            medium_stats["accuracy"], medium_stats["total"]
        )

        return LearnerProfile(
            user_id=user_id,
            preferred_difficulty=preferred,
            weak_topics=weak_topics,
            strong_topics=strong_topics,
            topic_mastery=topic_mastery,
        )
