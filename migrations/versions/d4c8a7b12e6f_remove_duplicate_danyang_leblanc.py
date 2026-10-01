"""remove duplicate Danyang Le Blanc Pension

Revision ID: d4c8a7b12e6f
Revises: 6a4f2c9d17e8
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d4c8a7b12e6f"
down_revision = "6a4f2c9d17e8"
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


def _danyang_destination_ids():
    return sa.select(destination.c.id).where(destination.c.name == "단양")


def upgrade():
    op.execute(
        sa.delete(accommodation).where(
            accommodation.c.destination_id.in_(_danyang_destination_ids()),
            accommodation.c.name == "단양 르블랑펜션",
            accommodation.c.image_url.is_(None),
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
                sa.literal("단양 르블랑펜션"),
                sa.literal("충청북도 단양군"),
                sa.literal("남한강과 단양 관광지를 둘러보기 좋은 펜션"),
                sa.literal(90000),
                sa.literal(4),
                sa.null(),
                sa.null(),
            ).where(destination.c.name == "단양"),
        )
    )
