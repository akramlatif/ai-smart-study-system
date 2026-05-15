"""Add feynman and socratic tables

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "feynman_attempts",
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
        sa.Column("student_explanation", sa.Text(), nullable=False),
        sa.Column("comprehension_score", sa.Integer(), nullable=False),
        sa.Column("strengths", sa.Text(), nullable=False),
        sa.Column("gaps", sa.Text(), nullable=False),
        sa.Column("misconceptions", sa.Text(), nullable=False),
        sa.Column("simplified_correction", sa.Text(), nullable=False),
        sa.Column("encouragement_message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_feynman_attempts_session_id", "feynman_attempts", ["session_id"])

    op.create_table(
        "socratic_sessions",
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
        sa.Column("depth_reached", sa.Integer(), server_default="1", nullable=False),
        sa.Column("is_complete", sa.Boolean(), server_default="0", nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("key_insights", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_socratic_sessions_session_id", "socratic_sessions", ["session_id"])

    op.create_table(
        "socratic_qa_pairs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "socratic_session_id",
            sa.String(36),
            sa.ForeignKey("socratic_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_index", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(20), nullable=False),
        sa.Column("depth_level", sa.Integer(), nullable=False),
        sa.Column("student_answer", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("answered_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_socratic_qa_pairs_session_id",
        "socratic_qa_pairs",
        ["socratic_session_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_socratic_qa_pairs_session_id", table_name="socratic_qa_pairs")
    op.drop_table("socratic_qa_pairs")
    op.drop_index("ix_socratic_sessions_session_id", table_name="socratic_sessions")
    op.drop_table("socratic_sessions")
    op.drop_index("ix_feynman_attempts_session_id", table_name="feynman_attempts")
    op.drop_table("feynman_attempts")
