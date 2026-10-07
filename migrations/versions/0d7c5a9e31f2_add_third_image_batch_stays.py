"""add accommodations from third image batch

Revision ID: 0d7c5a9e31f2
Revises: f24b8e6c1d70
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0d7c5a9e31f2"
down_revision = "f24b8e6c1d70"
branch_labels = None
depends_on = None


destination = sa.table(
    "destination",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)

accommodation = sa.table(
    "accommodation",
    sa.column("id", sa.Integer),
    sa.column("destination_id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("address", sa.String),
    sa.column("description", sa.Text),
    sa.column("price_per_night", sa.Integer),
    sa.column("capacity", sa.Integer),
    sa.column("rating", sa.Numeric(2, 1)),
    sa.column("image_url", sa.String),
)


def _destination_id(name):
    return op.get_bind().execute(
        sa.select(destination.c.id).where(destination.c.name == name)
    ).scalar_one_or_none()


def _insert_if_missing(region, **values):
    destination_id = _destination_id(region)
    if destination_id is None:
        return

    exists = op.get_bind().execute(
        sa.select(accommodation.c.id).where(
            accommodation.c.destination_id == destination_id,
            accommodation.c.name == values["name"],
        )
    ).first()
    if exists is None:
        op.execute(
            sa.insert(accommodation).values(
                destination_id=destination_id,
                **values,
            )
        )


def upgrade():
    _insert_if_missing(
        "남해",
        name="남해 스포츠파크 호텔",
        address="경상남도 남해군 서면 스포츠파크길 73",
        description="남해 스포츠파크와 가까우며 산 전망과 편안한 휴식을 제공하는 호텔",
        price_per_night=86000,
        capacity=2,
        rating=None,
        image_url="/static/img/accommodation/남해/남해 스포츠파크 호텔/images (1).jpg",
    )
    _insert_if_missing(
        "산청",
        name="산청한방가족호텔",
        address="경상남도 산청군 금서면 동의보감로479번길 43",
        description="동의보감촌 안에서 한방 체험과 지리산 자락의 휴식을 함께 즐기기 좋은 가족호텔",
        price_per_night=105000,
        capacity=4,
        rating=None,
        image_url="/static/img/accommodation/산청/산청한방가족호텔/images (1).jpg",
    )
    _insert_if_missing(
        "신안",
        name="신안 1004 섬리조트 펜션",
        address="전라남도 신안군",
        description="신안의 섬과 바다 풍경을 가까이에서 즐기며 머물기 좋은 리조트형 펜션",
        price_per_night=110000,
        capacity=4,
        rating=None,
        image_url="/static/img/accommodation/신안/신안 1004 섬리조트 펜션/images (1).jpg",
    )
    _insert_if_missing(
        "완주",
        name="소양고택",
        address="전북특별자치도 완주군 소양면 송광수만로 472-23",
        description="오성한옥마을에서 전통 한옥과 정원, 책방의 고즈넉한 분위기를 경험하는 한옥스테이",
        price_per_night=180000,
        capacity=2,
        rating=None,
        image_url="/static/img/accommodation/완주/소양고택/05438e3a8ca47.jpg",
    )


def downgrade():
    for region, name in (
        ("남해", "남해 스포츠파크 호텔"),
        ("산청", "산청한방가족호텔"),
        ("신안", "신안 1004 섬리조트 펜션"),
        ("완주", "소양고택"),
    ):
        destination_id = _destination_id(region)
        if destination_id is not None:
            op.execute(
                sa.delete(accommodation).where(
                    accommodation.c.destination_id == destination_id,
                    accommodation.c.name == name,
                )
            )
