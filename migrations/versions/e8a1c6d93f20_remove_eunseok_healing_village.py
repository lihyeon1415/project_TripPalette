"""remove Eunseok Healing Village accommodation

Revision ID: e8a1c6d93f20
Revises: d4c8a7b12e6f
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e8a1c6d93f20"
down_revision = "d4c8a7b12e6f"
branch_labels = None
depends_on = None


destination = sa.table(
    "destination",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

accommodation = sa.table(
    "accommodation",
    sa.column("destination_id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("address", sa.String),
    sa.column("description", sa.Text),
    sa.column("price_per_night", sa.Integer),
    sa.column("capacity", sa.Integer),
    sa.column("rating", sa.Numeric(2, 1)),
    sa.column("image_url", sa.String),
)


def _jeongseon_destination_ids():
    return sa.select(destination.c.id).where(destination.c.name == "정선")


def upgrade():
    op.execute(
        sa.delete(accommodation).where(
            accommodation.c.destination_id.in_(_jeongseon_destination_ids()),
            accommodation.c.name == "은석힐링마을",
        )
    )


def downgrade():
    op.execute(
        sa.insert(accommodation).from_select(
            (
                "destination_id",
                "name",
                "address",
                "description",
                "price_per_night",
                "capacity",
                "rating",
                "image_url",
            ),
            sa.select(
                destination.c.id,
                sa.literal("은석힐링마을"),
                sa.literal("강원특별자치도 정선군"),
                sa.literal("정선에서 편안하게 머무르기 좋은 숙소"),
                sa.literal(110000),
                sa.literal(4),
                sa.null(),
                sa.null(),
            ).where(destination.c.name == "정선"),
        )
    )
