"""replace outdated accommodation seed records

Revision ID: 6a4f2c9d17e8
Revises: b82d0f1a63e4
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "6a4f2c9d17e8"
down_revision = "b82d0f1a63e4"
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


def upgrade():
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_destination_ids("순천")),
            accommodation.c.name.in_(
                (
                    "순천만S호텔",
                    "순천승주CC글램핑",
                    "순천 승주 CC 글램핑",
                    "승주CC글램핑",
                    "승주 CC 글램핑",
                )
            ),
        )
        .values(
            name="포라이즌글램핑",
            address="전라남도 순천시 별량면 오실길 333-1",
            description=(
                "편백나무 숲에서 순천만 풍경과 바비큐를 즐기는 "
                "자연 친화형 글램핑"
            ),
            price_per_night=150000,
            capacity=4,
            image_url=None,
        )
    )
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_destination_ids("완주")),
            accommodation.c.name == "브라운도트호텔 완주 봉동점",
        )
        .values(
            name="더 클래식 바이 호텔원",
            address="전북특별자치도 완주군 이서면 오공로 21-19",
            description=(
                "전주 혁신도시에 자리해 관광과 비즈니스 이동이 편리한 호텔"
            ),
            price_per_night=70000,
            capacity=2,
            image_url=None,
        )
    )
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_destination_ids("창원 진해")),
            accommodation.c.name == "깨끗한 호텔 외인촌",
        )
        .values(
            name="그랜드 머큐어 앰배서더 창원",
            address="경상남도 창원시 성산구 원이대로 332",
            description=(
                "창원컨벤션센터와 시티세븐에 인접한 도심형 특급 호텔"
            ),
            price_per_night=160000,
            capacity=2,
            image_url=None,
        )
    )


def downgrade():
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_destination_ids("순천")),
            accommodation.c.name == "포라이즌글램핑",
        )
        .values(
            name="순천만S호텔",
            address="전라남도 순천시",
            description="순천만 여행을 위한 실속형 호텔",
            price_per_night=60000,
            capacity=2,
            image_url=None,
        )
    )
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_destination_ids("완주")),
            accommodation.c.name == "더 클래식 바이 호텔원",
        )
        .values(
            name="브라운도트호텔 완주 봉동점",
            address="전북특별자치도 완주군 봉동읍",
            description="완주 여행의 거점으로 이용하기 좋은 호텔",
            price_per_night=70000,
            capacity=2,
            image_url=None,
        )
    )
    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id.in_(_destination_ids("창원 진해")),
            accommodation.c.name == "그랜드 머큐어 앰배서더 창원",
        )
        .values(
            name="깨끗한 호텔 외인촌",
            address="경상남도 창원시 진해구",
            description="진해 여행을 위한 도심형 숙소",
            price_per_night=32000,
            capacity=2,
            image_url="/static/img/창원(봄)/깨끗한 호텔외인촌/방.jpg",
        )
    )
