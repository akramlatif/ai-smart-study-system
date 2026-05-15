import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class SocraticSession(Base):
    __tablename__ = "socratic_sessions"

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
    depth_reached: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    key_insights: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    session: Mapped["StudySession"] = relationship("StudySession")  # noqa: F821
    topic: Mapped["Topic | None"] = relationship("Topic")           # noqa: F821
    qa_pairs: Mapped[list["SocraticQAPair"]] = relationship(
        "SocraticQAPair", back_populates="socratic_session",
        cascade="all, delete-orphan", order_by="SocraticQAPair.question_index"
    )


class SocraticQAPair(Base):
    __tablename__ = "socratic_qa_pairs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    socratic_session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("socratic_sessions.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    question_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    depth_level: Mapped[int] = mapped_column(Integer, nullable=False)
    student_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    answered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    socratic_session: Mapped["SocraticSession"] = relationship(
        "SocraticSession", back_populates="qa_pairs"
    )
