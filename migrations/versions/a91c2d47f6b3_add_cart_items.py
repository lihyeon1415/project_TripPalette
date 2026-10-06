"""add cart items

Revision ID: a91c2d47f6b3
Revises: df817ec37b80
Create Date: 2026-10-06
"""

from alembic import op
import sqlalchemy as sa


revision = "a91c2d47f6b3"
down_revision = "df817ec37b80"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cart_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity >= 1 AND quantity <= 10",
            name="ck_cart_item_quantity_range",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["product.id"],
            name="fk_cart_item_product_id_product",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_cart_item_user_id_user",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_cart_item_user_product",
        ),
    )
    op.create_index("ix_cart_item_user_id", "cart_item", ["user_id"], unique=False)


def downgrade():
    op.drop_index("ix_cart_item_user_id", table_name="cart_item")
    op.drop_table("cart_item")
