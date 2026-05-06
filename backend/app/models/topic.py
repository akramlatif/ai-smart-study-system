import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("study_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("topics.id"), nullable=True
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    session: Mapped["StudySession"] = relationship("StudySession", back_populates="topics")  # noqa: F821
    parent: Mapped["Topic | None"] = relationship(
        "Topic", remote_side="Topic.id", foreign_keys="[Topic.parent_id]", back_populates="subtopics"
    )
    subtopics: Mapped[list["Topic"]] = relationship(
        "Topic", foreign_keys="[Topic.parent_id]", back_populates="parent"
    )
    explanations: Mapped[list["Explanation"]] = relationship(  # noqa: F821
        "Explanation", back_populates="topic", cascade="all, delete-orphan"
    )
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(  # noqa: F821
        "QuizQuestion", back_populates="topic"
    )
