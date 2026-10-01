"""replace Inje Hotel seed record with Malgeunmul Resort

Revision ID: e71b9a4c6d20
Revises: c3e1f7a902ab
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e71b9a4c6d20"
down_revision = "c3e1f7a902ab"
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


def _inje_destination_ids():
    return sa.select(destination.c.id).where(destination.c.name == "인제")


def upgrade():
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_inje_destination_ids()),
            accommodation.c.name == "인제호텔",
        )
        .values(
            name="맑은물리조트",
            address="강원특별자치도 인제군 기린면 내린천로 4723",
            description=(
                "내린천 전망의 테라스와 수영장·세미나실을 갖춘 가족형 리조트"
            ),
            price_per_night=162000,
            capacity=4,
        )
    )


def downgrade():
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_inje_destination_ids()),
            accommodation.c.name == "맑은물리조트",
        )
        .values(
            name="인제호텔",
            address="강원특별자치도 인제군",
            description="인제 도심에 위치한 실속형 호텔",
            price_per_night=70000,
            capacity=2,
        )
    )
