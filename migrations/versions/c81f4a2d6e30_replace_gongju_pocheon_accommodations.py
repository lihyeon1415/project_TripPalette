"""replace Gongju Geumgang and Pocheon duplicate pension

Revision ID: c81f4a2d6e30
Revises: b63e1d7a4f90
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c81f4a2d6e30"
down_revision = "b63e1d7a4f90"
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
    sa.column("image_url", sa.String),
)


def _destination_ids(name):
    return sa.select(destination.c.id).where(destination.c.name == name)


def _replace(region, old_name, **values):
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_destination_ids(region)),
            accommodation.c.name == old_name,
        )
        .values(**values)
    )


def upgrade():
    _replace(
        "공주",
        "공주호텔금강",
        name="공주호텔어반티",
        address="충청남도 공주시 번영1로 13",
        description="공주종합버스터미널과 금강신관공원에서 가까운 도심형 호텔",
        price_per_night=70000,
        capacity=2,
        image_url="/static/img/accommodation/공주/공주호텔어반티/1.jpg",
    )
    _replace(
        "포천",
        "포천산정호수계곡 늘푸른허브펜션",
        name="포천 아일랜드펜션",
        address="경기도 포천시 영북면 산정호수로 911",
        description="산정호수와 가까워 가족 여행에서 편안하게 머물기 좋은 펜션",
        price_per_night=110000,
        capacity=4,
        image_url="/static/img/accommodation/포천/포천 아일랜드펜션/1.jpg",
    )


def downgrade():
    _replace(
        "공주",
        "공주호텔어반티",
        name="공주호텔금강",
        address="충청남도 공주시",
        description="공주의 주요 여행지로 이동하기 편리한 호텔",
        price_per_night=90000,
        capacity=2,
        image_url=None,
    )
    _replace(
        "포천",
        "포천 아일랜드펜션",
        name="포천산정호수계곡 늘푸른허브펜션",
        address="경기도 포천시",
        description="포천에서 편안하게 머무르기 좋은 숙소",
        price_per_night=110000,
        capacity=4,
        image_url=None,
    )
