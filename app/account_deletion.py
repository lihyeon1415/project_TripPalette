from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app import db
from app.models import (
    AccommodationReview,
    Favorite,
    Payment,
    Reservation,
    Review,
    User,
    UserPreference,
)


def utcnow():
    """DB DateTime 컬럼과 비교할 timezone-naive UTC 시각을 반환한다."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def format_deletion_date(value):
    """UTC로 저장한 삭제 예정 시각을 한국 날짜로 표시한다."""
    if value is None:
        return None
    korea_time = value.replace(tzinfo=timezone.utc).astimezone(
        timezone(timedelta(hours=9))
    )
    return korea_time.strftime("%Y년 %m월 %d일")


def delete_accounts(user_ids):
    """탈퇴 계정과 계정에 귀속된 데이터를 외래키 순서대로 삭제한다."""
    user_ids = tuple(user_ids)
    if not user_ids:
        return 0

    reservation_ids = db.select(Reservation.id).where(
        Reservation.user_id.in_(user_ids)
    )
    statements = (
        delete(Payment).where(Payment.reservation_id.in_(reservation_ids)),
        delete(Reservation).where(Reservation.user_id.in_(user_ids)),
        delete(UserPreference).where(UserPreference.user_id.in_(user_ids)),
        delete(Favorite).where(Favorite.user_id.in_(user_ids)),
        delete(AccommodationReview).where(
            AccommodationReview.user_id.in_(user_ids)
        ),
        delete(Review).where(Review.user_id.in_(user_ids)),
        delete(User).where(User.id.in_(user_ids)),
    )
    for statement in statements:
        db.session.execute(
            statement.execution_options(synchronize_session=False)
        )
    return len(user_ids)


def purge_expired_accounts(now=None):
    """30일의 유예기간이 지난 탈퇴 예약 계정을 영구 삭제한다."""
    now = now or utcnow()
    user_ids = tuple(
        db.session.scalars(
            db.select(User.id).where(
                User.scheduled_deletion_at.is_not(None),
                User.scheduled_deletion_at <= now,
            )
        )
    )
    deleted_count = delete_accounts(user_ids)
    if deleted_count:
        db.session.commit()
    return deleted_count
