import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class FeynmanAttempt(Base):
    __tablename__ = "feynman_attempts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("study_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    topic_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("topics.id"), nullable=True
    )
    student_explanation: Mapped[str] = mapped_column(Text, nullable=False)
    comprehension_score: Mapped[int] = mapped_column(Integer, nullable=False)
    strengths: Mapped[str] = mapped_column(Text, nullable=False)       # JSON array
    gaps: Mapped[str] = mapped_column(Text, nullable=False)            # JSON array
    misconceptions: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array
    simplified_correction: Mapped[str] = mapped_column(Text, nullable=False)
    encouragement_message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["StudySession"] = relationship("StudySession")  # noqa: F821
    topic: Mapped["Topic | None"] = relationship("Topic")           # noqa: F821
