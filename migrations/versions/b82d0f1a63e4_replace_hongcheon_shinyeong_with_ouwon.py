"""replace Hongcheon Shinyeong Pension seed record with Ouwon

Revision ID: b82d0f1a63e4
Revises: e71b9a4c6d20
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b82d0f1a63e4"
down_revision = "e71b9a4c6d20"
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
)


def _hongcheon_destination_ids():
    return sa.select(destination.c.id).where(destination.c.name == "홍천")


def upgrade():
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_hongcheon_destination_ids()),
            accommodation.c.name == "홍천 신영펜션",
        )
        .values(
            name="오유원",
            address="강원특별자치도 홍천군 서면 한치골길 83-5",
            description=(
                "계곡과 산 전망, 개별 수영장을 갖춘 프라이빗 독채 풀빌라 스테이"
            ),
            price_per_night=468000,
            capacity=6,
        )
    )


def downgrade():
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_hongcheon_destination_ids()),
            accommodation.c.name == "오유원",
        )
        .values(
            name="홍천 신영펜션",
            address="강원특별자치도 홍천군",
            description="홍천 자연 속에서 머무는 펜션",
            price_per_night=90000,
            capacity=4,
        )
    )
