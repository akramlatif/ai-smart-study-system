import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, Text, ForeignKey, CheckConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    __table_args__ = ()

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("study_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("topics.id"), nullable=True
    )
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(10), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    saved_for_review: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["StudySession"] = relationship(  # noqa: F821
        "StudySession", back_populates="quiz_questions"
    )
    topic: Mapped["Topic | None"] = relationship(  # noqa: F821
        "Topic", back_populates="quiz_questions"
    )
