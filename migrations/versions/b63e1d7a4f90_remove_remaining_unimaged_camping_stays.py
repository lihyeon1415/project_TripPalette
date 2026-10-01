"""remove remaining unimaged stays categorized as camping

Revision ID: b63e1d7a4f90
Revises: a17d6c4e9b20
Create Date: 2026-09-30 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b63e1d7a4f90"
down_revision = "a17d6c4e9b20"
branch_labels = None
depends_on = None


accommodation = sa.table(
    "accommodation",
    sa.column("id", sa.Integer),
    sa.column("description", sa.Text),
    sa.column("image_url", sa.String),
)

accommodation_review = sa.table(
    "accommodation_review",
    sa.column("accommodation_id", sa.Integer),
)

reservation = sa.table(
    "reservation",
    sa.column("id", sa.Integer),
    sa.column("accommodation_id", sa.Integer),
)

payment = sa.table(
    "payment",
    sa.column("reservation_id", sa.Integer),
)


def upgrade():
    bind = op.get_bind()
    accommodation_ids = list(
        bind.execute(
            sa.select(accommodation.c.id).where(
                accommodation.c.image_url.is_(None),
                accommodation.c.description.like("%캠핑형 숙소%"),
            )
        ).scalars()
    )
    if not accommodation_ids:
        return

    reservation_ids = list(
        bind.execute(
            sa.select(reservation.c.id).where(
                reservation.c.accommodation_id.in_(accommodation_ids)
            )
        ).scalars()
    )
    if reservation_ids:
        op.execute(
            sa.delete(payment).where(payment.c.reservation_id.in_(reservation_ids))
        )
        op.execute(
            sa.delete(reservation).where(reservation.c.id.in_(reservation_ids))
        )

    op.execute(
        sa.delete(accommodation_review).where(
            accommodation_review.c.accommodation_id.in_(accommodation_ids)
        )
    )
    op.execute(
        sa.delete(accommodation).where(accommodation.c.id.in_(accommodation_ids))
    )


def downgrade():
    # 삭제 당시의 사용자 데이터까지 완전히 복원할 수 없어 자동 복구하지 않는다.
    pass
