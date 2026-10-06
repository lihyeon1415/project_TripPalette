from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, update

from app import db
from app.models import (
    AccommodationReview,
    Favorite,
    GoodsOrder,
    Payment,
    Reservation,
    Review,
    User,
    UserPreference,
)


GOODS_ORDER_TERMINAL_STATUSES = {
    "DELIVERED",
    "CANCELLED",
    "REFUNDED",
    "FAILED",
    "PAYMENT_FAILED",
    "EXPIRED",
}


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
    """진행 중 주문이 없는 탈퇴 계정을 삭제하고 거래 개인정보를 익명화한다."""
    user_ids = tuple(user_ids)
    if not user_ids:
        return 0

    blocked_user_ids = set(
        db.session.scalars(
            db.select(GoodsOrder.user_id).where(
                GoodsOrder.user_id.in_(user_ids),
                GoodsOrder.status.not_in(GOODS_ORDER_TERMINAL_STATUSES),
            )
        )
    )
    deletable_user_ids = tuple(
        user_id for user_id in user_ids if user_id not in blocked_user_ids
    )
    if not deletable_user_ids:
        return 0

    reservation_ids = db.select(Reservation.id).where(
        Reservation.user_id.in_(deletable_user_ids)
    )
    statements = (
        delete(Payment).where(Payment.reservation_id.in_(reservation_ids)),
        delete(Reservation).where(Reservation.user_id.in_(deletable_user_ids)),
        delete(UserPreference).where(UserPreference.user_id.in_(deletable_user_ids)),
        delete(Favorite).where(Favorite.user_id.in_(deletable_user_ids)),
        delete(AccommodationReview).where(
            AccommodationReview.user_id.in_(deletable_user_ids)
        ),
        delete(Review).where(Review.user_id.in_(deletable_user_ids)),
        update(GoodsOrder)
        .where(GoodsOrder.user_id.in_(deletable_user_ids))
        .values(
            user_id=None,
            recipient_name="탈퇴 회원",
            recipient_phone="",
            postal_code="",
            address="삭제된 배송지",
            address_detail=None,
            delivery_request=None,
        ),
        delete(User).where(User.id.in_(deletable_user_ids)),
    )
    for statement in statements:
        db.session.execute(
            statement.execution_options(synchronize_session=False)
        )
    return len(deletable_user_ids)


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
