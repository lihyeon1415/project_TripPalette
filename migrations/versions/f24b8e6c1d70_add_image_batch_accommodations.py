"""add and replace accommodations from image batch

Revision ID: f24b8e6c1d70
Revises: d92a7c4e51b3
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "f24b8e6c1d70"
down_revision = "d92a7c4e51b3"
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


def _replace(region, old_name, **values):
    destination_id = _destination_id(region)
    if destination_id is None:
        return

    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id == destination_id,
            accommodation.c.name == old_name,
        )
        .values(**values)
    )


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
    _replace(
        "제주 한림",
        "곁겹",
        name="아루미호텔 협재",
        address="제주특별자치도 제주시 한림읍 한림로 545",
        description="협재해수욕장과 한림공원으로 이동하기 편리한 한림 지역 호텔",
        price_per_night=67000,
        capacity=2,
        image_url="/static/img/accommodation/제주 한림/아루미호텔 협재/1.jpg",
    )
    _replace(
        "포항",
        "오션힐스 골프리조트",
        name="코랄트리풀빌라",
        address="경상북도 포항시 남구 호미곶면 구만길 188",
        description="호미곶 바다 전망과 개별 수영장을 갖춘 프라이빗 풀빌라",
        price_per_night=235000,
        capacity=2,
        image_url="/static/img/accommodation/포항/코랄트리풀빌라/1.jpg",
    )
    _insert_if_missing(
        "제주 조천",
        name="제주 베스트힐 글램핑 & 펜션",
        address="제주특별자치도 제주시 조천읍 남조로 2109-36",
        description="곶자왈 숲과 바농오름 자락에서 자연을 가까이 즐기는 펜션형 글램핑 숙소",
        price_per_night=99000,
        capacity=4,
        rating=None,
        image_url="/static/img/accommodation/제주 조천/제주 베스트힐 글램핑 & 펜션/1.jpg",
    )
    _insert_if_missing(
        "진주",
        name="호텔오름",
        address="경상남도 진주시 판문로 64-9",
        description="진양호 인근에서 조용하고 편안하게 머물기 좋은 도심형 호텔",
        price_per_night=75000,
        capacity=2,
        rating=None,
        image_url="/static/img/accommodation/진주/호텔오름/1.png",
    )


def downgrade():
    for region, name in (
        ("제주 조천", "제주 베스트힐 글램핑 & 펜션"),
        ("진주", "호텔오름"),
    ):
        destination_id = _destination_id(region)
        if destination_id is not None:
            op.execute(
                sa.delete(accommodation).where(
                    accommodation.c.destination_id == destination_id,
                    accommodation.c.name == name,
                )
            )

    _replace(
        "포항",
        "코랄트리풀빌라",
        name="오션힐스 골프리조트",
        address="경상북도 포항시",
        description="골프와 휴양을 함께 즐기는 리조트형 숙소",
        price_per_night=130000,
        capacity=4,
        image_url=None,
    )
    _replace(
        "제주 한림",
        "아루미호텔 협재",
        name="곁겹",
        address="제주특별자치도 제주시 한림읍",
        description="제주 한림에서 편안하게 머무르기 좋은 숙소",
        price_per_night=110000,
        capacity=4,
        image_url=None,
    )
