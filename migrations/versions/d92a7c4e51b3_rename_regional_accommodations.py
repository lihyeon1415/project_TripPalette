"""rename regional accommodations

Revision ID: d92a7c4e51b3
Revises: c81f4a2d6e30
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d92a7c4e51b3"
down_revision = "c81f4a2d6e30"
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
    ).scalar_one()


def _rename(region, old_name, new_name, description=None):
    values = {"name": new_name}
    if description is not None:
        values["description"] = description

    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id == _destination_id(region),
            accommodation.c.name == old_name,
        )
        .values(**values)
    )


def upgrade():
    _rename("영주", "무섬마을 한옥민박", "무섬마을 마당넓은집")
    _rename(
        "남해",
        "남해 스포츠파크 호텔",
        "남해 라피스 호텔",
        "남해 여행에서 편안하게 머무르기 좋은 호텔",
    )
    _rename("울릉", "힐링스테이 코스모스", "코스모스 울릉도")
    _rename("울릉", "울릉 다와라 펜션", "스테이너와")

    jeju_id = _destination_id("제주")
    exists = op.get_bind().execute(
        sa.select(accommodation.c.id).where(
            accommodation.c.destination_id == jeju_id,
            accommodation.c.name == "제주자연인펜션글램핑",
        )
    ).first()
    if exists is None:
        op.execute(
            sa.insert(accommodation).values(
                destination_id=jeju_id,
                name="제주자연인펜션글램핑",
                address="제주특별자치도 제주시",
                description="제주의 자연을 가까이에서 즐기기 좋은 펜션형 글램핑 숙소",
                price_per_night=100000,
                capacity=4,
                rating=None,
                image_url=None,
            )
        )


def downgrade():
    op.execute(
        sa.delete(accommodation).where(
            accommodation.c.destination_id == _destination_id("제주"),
            accommodation.c.name == "제주자연인펜션글램핑",
        )
    )
    _rename("울릉", "스테이너와", "울릉 다와라 펜션")
    _rename("울릉", "코스모스 울릉도", "힐링스테이 코스모스")
    _rename(
        "남해",
        "남해 라피스 호텔",
        "남해 스포츠파크 호텔",
        "남해 스포츠파크 인근의 실용적인 호텔",
    )
    _rename("영주", "무섬마을 마당넓은집", "무섬마을 한옥민박")
