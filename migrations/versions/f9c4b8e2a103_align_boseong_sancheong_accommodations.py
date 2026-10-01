"""align Boseong and Sancheong accommodations with supplied images

Revision ID: f9c4b8e2a103
Revises: e8a1c6d93f20
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "f9c4b8e2a103"
down_revision = "e8a1c6d93f20"
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
        "보성",
        "율포솔밭오토캠핑장 & 글램핑",
        name="해오름펜션",
        address="전라남도 보성군 회천면",
        description="보성 율포 해변 여행에서 편안하게 머물기 좋은 펜션",
        price_per_night=110000,
        capacity=4,
        image_url="/static/img/accommodation/보성/해오름펜션/1.jpg",
    )
    _replace(
        "보성",
        "보성 다향리조트",
        name="보성다비치콘도",
        address="전라남도 보성군 회천면 충의로 36",
        description="율포해수욕장 인근에서 바다 여행과 휴식을 함께 즐기기 좋은 콘도",
        price_per_night=90000,
        capacity=4,
        image_url="/static/img/accommodation/보성/보성다비치콘도/1.jpg",
    )
    _replace(
        "산청",
        "지리산 산청 카라반캠핑",
        name="월명 글램핑",
        address="경상남도 산청군 산청읍 웅석봉로285번길 80-20",
        description="웅석봉 자연 속에서 바베큐와 휴식을 즐길 수 있는 글램핑 숙소",
        price_per_night=200000,
        capacity=4,
        image_url="/static/img/accommodation/산청/월명 글램핑/1.jpg",
    )
    _replace(
        "산청",
        "동의보감촌 한옥스테이",
        name="동의본가",
        address="경상남도 산청군 금서면 동의보감로555번길 45-6",
        description="동의보감촌에서 한옥 숙박과 한방 치유 체험을 함께 즐길 수 있는 한옥스테이",
        price_per_night=120000,
        capacity=4,
        image_url="/static/img/accommodation/산청/동의본가/1.jpg",
    )


def downgrade():
    _replace(
        "보성",
        "해오름펜션",
        name="율포솔밭오토캠핑장 & 글램핑",
        address="전라남도 보성군",
        description="보성의 자연을 가까이에서 즐기는 캠핑형 숙소",
        price_per_night=140000,
        capacity=4,
        image_url=None,
    )
    _replace(
        "보성",
        "보성다비치콘도",
        name="보성 다향리조트",
        address="전라남도 보성군",
        description="보성 여행에서 여유롭게 쉬기 좋은 리조트형 숙소",
        price_per_night=150000,
        capacity=4,
        image_url=None,
    )
    _replace(
        "산청",
        "월명 글램핑",
        name="지리산 산청 카라반캠핑",
        address="경상남도 산청군",
        description="산청의 자연을 가까이에서 즐기는 캠핑형 숙소",
        price_per_night=140000,
        capacity=4,
        image_url=None,
    )
    _replace(
        "산청",
        "동의본가",
        name="동의보감촌 한옥스테이",
        address="경상남도 산청군",
        description="산청에서 편안하게 머무르기 좋은 숙소",
        price_per_night=110000,
        capacity=4,
        image_url=None,
    )
