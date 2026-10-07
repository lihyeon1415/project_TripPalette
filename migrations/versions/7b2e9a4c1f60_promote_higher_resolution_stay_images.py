"""promote higher-resolution accommodation images

Revision ID: 7b2e9a4c1f60
Revises: 0d7c5a9e31f2
Create Date: 2026-10-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "7b2e9a4c1f60"
down_revision = "0d7c5a9e31f2"
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
    sa.column("image_url", sa.String),
)


IMAGE_CHANGES = (
    (
        "창원 진해",
        "진해 인터시티호텔",
        "unnamed (1).jpg",
        "main-upscaled-v1.png",
    ),
    ("삼척", "산티아고펜션", "다운로드 (1).jpg", "main-upscaled-v1.png"),
    (
        "삼척",
        "힐스노클비치호텔",
        "다운로드 (1).jpg",
        "main-upscaled-v1.png",
    ),
    ("속초", "HJ하우스펜션", "다운로드 (1).jpg", "main-upscaled-v1.png"),
    ("무주", "나오스펜션", "다운로드 (1).jpg", "main-upscaled-v1.png"),
    ("무주", "무주아일랜드", "다운로드 (1).jpg", "main-upscaled-v1.png"),
    ("보령", "여기도글램핑펜션식당", "images (1).jpg", "main-upscaled-v1.png"),
    ("산청", "휴롬산청빌리지", "images (1).jpg", "main-upscaled-v1.png"),
    ("정읍", "앨리스데이", "다운로드 (1).jpg", "main-upscaled-v1.png"),
    ("정선", "하이원 그랜드호텔", "unnamed (1).jpg", "main-upscaled-v1.png"),
    ("담양", "그라스풀빌라리조트", "images (1).jpg", "main-upscaled-v1.png"),
    ("담양", "라온글램핑", "다운로드 (1).jpg", "main-upscaled-v1.png"),
    ("안동", "안동마애펜션", "images (1).jpg", "main-upscaled-v1.png"),
    ("평창", "AM호텔", "다운로드 (3).jpg", "main-upscaled-v1.png"),
    ("인제", "자작나무숲 자작향기펜션", "images (1).jpg", "main-upscaled-v1.png"),
    ("정선", "메이힐스리조트", "unnamed (1).jpg", "main-upscaled-v1.png"),
    ("경주", "라한셀렉트 경주", "images (1).jpg", "main-upscaled-v1.png"),
    ("고창", "고창 람사르펜션", "images (1).jpg", "main-upscaled-v1.png"),
    ("거제", "거제삼성호텔", "images (1).jpg", "main-upscaled-v1.png"),
    ("거제", "더100펜션", "다운로드 (1).jpg", "main-upscaled-v1.png"),
    ("군산", "에이본 호텔 군산", "images (1).jpg", "main-upscaled-v1.png"),
    ("군산", "유로빌리지", "images (1).jpg", "main-upscaled-v1.png"),
    ("서귀포", "굿데이펜션", "images (1).jpg", "main-upscaled-v1.png"),
    ("서귀포", "팜핑제주카라반", "images (1).jpg", "main-upscaled-v1.png"),
    ("정선", "트라움벨리 호텔", "images (1).jpg", "main-upscaled-v1.png"),
    ("제천", "하운드호텔 제천역", "unnamed (1).jpg", "main-upscaled-v1.png"),
    ("정선", "아우라지글램핑", "images (1).jpg", "main-upscaled-v1.png"),
    ("청송", "청송 주노글램핑 청송점", "images (1).jpg", "main-upscaled-v1.png"),
    ("철원", "철원 솔향기 펜션", "unnamed (1).jpg", "main-upscaled-v1.png"),
    ("거제", "쉼표 글램핑&캠핑", "images (1).jpg", "main-upscaled-v1.png"),
    ("여수", "신라스테이 여수", "images (1).jpg", "main-upscaled-v1.png"),
    ("여수", "비고리조트", "images (1).jpg", "main-upscaled-v1.png"),
    ("춘천", "춘천 에스턴호텔", "images (1).jpg", "main-upscaled-v1.png"),
    ("통영", "통영아이펜션", "images (1).jpg", "main-upscaled-v1.png"),
    ("원주", "원주 센트럴 호텔", "images (1).jpg", "main-upscaled-v1.png"),
    ("이천", "이천 인트라다 호텔", "unnamed (1).jpg", "main-upscaled-v1.png"),
    ("전주", "전주 나무그늘 펜션", "images (1).jpg", "main-upscaled-v1.png"),
    ("익산", "익산 하늘숲 펜션", "images (1).jpg", "main-upscaled-v1.png"),
    ("익산", "탑클라우드호텔 익산", "images (1).jpg", "main-upscaled-v1.png"),
    ("고창", "고창 웰파크 호텔", "images (1).jpg", "main-upscaled-v1.png"),
    ("서귀포", "호텔더본제주", "다운로드 (1).jpg", "main-upscaled-v1.png"),
    ("신안", "신안 1004 섬리조트 펜션", "images (1).jpg", "main-upscaled-v1.png"),
)


def _image_url(region, stay, filename):
    return f"/static/img/accommodation/{region}/{stay}/{filename}"


def _update_image(region, stay, filename):
    destination_id = op.get_bind().execute(
        sa.select(destination.c.id).where(destination.c.name == region)
    ).scalar_one_or_none()
    if destination_id is None:
        return

    op.execute(
        sa.update(accommodation)
        .where(
            accommodation.c.destination_id == destination_id,
            accommodation.c.name == stay,
        )
        .values(image_url=_image_url(region, stay, filename))
    )


def upgrade():
    for region, stay, _old_filename, new_filename in IMAGE_CHANGES:
        _update_image(region, stay, new_filename)


def downgrade():
    for region, stay, old_filename, _new_filename in IMAGE_CHANGES:
        _update_image(region, stay, old_filename)
