"""
TutorSession and TutorStep ORM models for Interactive Tutor Mode.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Integer, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class TutorSession(Base):
    """Tracks an interactive tutoring session for step-by-step learning."""
    __tablename__ = "tutor_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("study_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    subtopics_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    current_subtopic_index: Mapped[int] = mapped_column(Integer, default=0)
    difficulty_level: Mapped[str] = mapped_column(String(10), default="medium")
    weak_areas_json: Mapped[str] = mapped_column(Text, default="[]")
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_count: Mapped[int] = mapped_column(Integer, default=0)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    steps: Mapped[list["TutorStep"]] = relationship(
        "TutorStep", back_populates="tutor_session", cascade="all, delete-orphan",
        order_by="TutorStep.subtopic_index"
    )


class TutorStep(Base):
    """Each teaching step: subtopic explanation + question + student answer."""
    __tablename__ = "tutor_steps"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tutor_session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tutor_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subtopic_name: Mapped[str] = mapped_column(Text, nullable=False)
    subtopic_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    student_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    is_skipped: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    tutor_session: Mapped["TutorSession"] = relationship(
        "TutorSession", back_populates="steps"
    )
