"""add account withdrawal schedule

Revision ID: a8c21e94f630
Revises: f451dbed44b8
Create Date: 2026-09-29 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "a8c21e94f630"
down_revision = "f451dbed44b8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(
            sa.Column("withdrawal_requested_at", sa.DateTime(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("scheduled_deletion_at", sa.DateTime(), nullable=True)
        )
        batch_op.create_index(
            "ix_user_scheduled_deletion_at",
            ["scheduled_deletion_at"],
            unique=False,
        )


def downgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.drop_index("ix_user_scheduled_deletion_at")
        batch_op.drop_column("scheduled_deletion_at")
        batch_op.drop_column("withdrawal_requested_at")
