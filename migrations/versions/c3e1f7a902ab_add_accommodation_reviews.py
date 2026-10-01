"""add accommodation reviews

Revision ID: c3e1f7a902ab
Revises: a8c21e94f630
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c3e1f7a902ab"
down_revision = "a8c21e94f630"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "accommodation_review",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("accommodation_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_accommodation_review_rating_range",
        ),
        sa.ForeignKeyConstraint(["accommodation_id"], ["accommodation.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "accommodation_id",
            name="uq_accommodation_review_user_accommodation",
        ),
    )


def downgrade():
    op.drop_table("accommodation_review")
