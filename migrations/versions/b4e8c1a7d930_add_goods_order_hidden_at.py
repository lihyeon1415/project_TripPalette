"""add goods order hidden at

Revision ID: b4e8c1a7d930
Revises: a91c2d47f6b3
Create Date: 2026-10-06
"""

from alembic import op
import sqlalchemy as sa


revision = "b4e8c1a7d930"
down_revision = "a91c2d47f6b3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "goods_order",
        sa.Column("hidden_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_goods_order_hidden_at",
        "goods_order",
        ["hidden_at"],
        unique=False,
    )


def downgrade():
    op.drop_index("ix_goods_order_hidden_at", table_name="goods_order")
    op.drop_column("goods_order", "hidden_at")
