"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "study_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "previous_id",
            sa.String(36),
            sa.ForeignKey("study_sessions.id"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("interaction_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_index("ix_study_sessions_user_id", "study_sessions", ["user_id"])

    op.create_table(
        "topics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("study_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("is_main", sa.Boolean(), server_default="1", nullable=False),
        sa.Column(
            "parent_id",
            sa.String(36),
            sa.ForeignKey("topics.id"),
            nullable=True,
        ),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_topics_session_id", "topics", ["session_id"])

    op.create_table(
        "explanations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "topic_id",
            sa.String(36),
            sa.ForeignKey("topics.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "level IN ('basic', 'intermediate', 'advanced')",
            name="ck_explanation_level",
        ),
    )
    op.create_index("ix_explanations_topic_id", "explanations", ["topic_id"])

    op.create_table(
        "quiz_questions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("study_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "topic_id",
            sa.String(36),
            sa.ForeignKey("topics.id"),
            nullable=True,
        ),
        sa.Column("question_type", sa.String(20), nullable=False),
        sa.Column("difficulty", sa.String(10), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options", sa.Text(), nullable=True),  # JSON string
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("saved_for_review", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "question_type IN ('multiple_choice', 'short_answer')",
            name="ck_quiz_question_type",
        ),
        sa.CheckConstraint(
            "difficulty IN ('easy', 'medium', 'hard')",
            name="ck_quiz_difficulty",
        ),
    )
    op.create_index("ix_quiz_questions_session_id", "quiz_questions", ["session_id"])

    op.create_table(
        "documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "session_id",
            sa.String(36),
            sa.ForeignKey("study_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("file_type", sa.String(20), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("quality_flag", sa.String(20), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "quality_flag IN ('ok', 'low_quality', 'unreadable')",
            name="ck_document_quality_flag",
        ),
    )
    op.create_index("ix_documents_session_id", "documents", ["session_id"])
    op.create_index("ix_documents_user_id", "documents", ["user_id"])


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_table("quiz_questions")
    op.drop_table("explanations")
    op.drop_table("topics")
    op.drop_table("study_sessions")
    op.drop_table("users")
