import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    quiz_question_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("quiz_questions.id"), nullable=True
    )
    topic_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("topics.id"), nullable=True
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_mode: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    
    answered_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    next_review_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, index=True
    )
    review_interval_days: Mapped[int] = mapped_column(Integer, default=1)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5)

    user: Mapped["User"] = relationship("User")  # noqa: F821
    session: Mapped["StudySession"] = relationship("StudySession")  # noqa: F821
    quiz_question: Mapped["QuizQuestion | None"] = relationship("QuizQuestion")  # noqa: F821
    topic: Mapped["Topic | None"] = relationship("Topic")  # noqa: F821
