from datetime import datetime, timedelta

from flask import (
    abort,
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy.orm import selectinload
from werkzeug.security import check_password_hash

from app import db
from app.account_deletion import format_deletion_date, utcnow
from app.auth_helpers import login_required
from app.models import (
    Accommodation,
    AccommodationReview,
    Favorite,
    GoodsOrder,
    GoodsOrderItem,
    Reservation,
    Review,
)
from app.services.payment_service import expire_pending_payments

mypage_bp = Blueprint("mypage", __name__)


@mypage_bp.get("")
@login_required
def index():
    return redirect(url_for("mypage.favorites"))


@mypage_bp.get("/favorites")
@login_required
def favorites():
    user_favorites = list(
        db.session.execute(
            db.select(Favorite)
            .options(selectinload(Favorite.destination))
            .where(Favorite.user_id == g.user.id)
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        ).scalars()
    )
    return render_template("mypage/favorites.html", favorites=user_favorites)


@mypage_bp.get("/reservations")
@login_required
def reservations():
    user_reservations = list(
        db.session.execute(
            db.select(Reservation)
            .options(
                selectinload(Reservation.accommodation).selectinload(
                    Accommodation.destination
                )
            )
            .where(
                Reservation.user_id == g.user.id,
                Reservation.status.in_(("PENDING", "PAYMENT_PENDING", "CONFIRMED")),
            )
            .order_by(Reservation.created_at.desc(), Reservation.id.desc())
        ).scalars()
    )
    return render_template(
        "mypage/reservations.html",
        reservations=user_reservations,
    )


@mypage_bp.get("/orders")
@login_required
def orders():
    expire_pending_payments()
    user_orders = list(
        db.session.execute(
            db.select(GoodsOrder)
            .options(
                selectinload(GoodsOrder.items).selectinload(GoodsOrderItem.product),
                selectinload(GoodsOrder.payment),
            )
            .where(
                GoodsOrder.user_id == g.user.id,
                GoodsOrder.hidden_at.is_(None),
            )
            .order_by(GoodsOrder.created_at.desc(), GoodsOrder.id.desc())
        ).scalars()
    )
    status_labels = {
        "PAYMENT_PENDING": "결제 대기",
        "PAID": "결제 완료",
        "PREPARING": "상품 준비 중",
        "SHIPPED": "배송 중",
        "DELIVERED": "배송 완료",
        "CANCELLED": "주문 취소",
        "REFUNDED": "환불 완료",
        "FAILED": "결제 실패",
        "PAYMENT_FAILED": "결제 실패",
        "EXPIRED": "결제 만료",
    }
    return render_template(
        "mypage/orders.html",
        orders=user_orders,
        status_labels=status_labels,
    )


@mypage_bp.get("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    order = db.session.get(GoodsOrder, order_id)
    if order is None or order.user_id != g.user.id:
        abort(404)
    return redirect(url_for("order.detail", order_id=order.id))


@mypage_bp.get("/reviews")
@login_required
def reviews():
    user_reviews = list(
        db.session.execute(
            db.select(Review)
            .options(selectinload(Review.destination))
            .where(Review.user_id == g.user.id)
            .order_by(Review.created_at.desc(), Review.id.desc())
        ).scalars()
    )
    accommodation_reviews = list(
        db.session.execute(
            db.select(AccommodationReview)
            .options(
                selectinload(AccommodationReview.accommodation).selectinload(
                    Accommodation.destination
                )
            )
            .where(AccommodationReview.user_id == g.user.id)
            .order_by(
                AccommodationReview.created_at.desc(),
                AccommodationReview.id.desc(),
            )
        ).scalars()
    )
    review_items = [
        *(('destination', review) for review in user_reviews),
        *(('accommodation', review) for review in accommodation_reviews),
    ]
    review_items.sort(
        key=lambda item: (
            item[1].created_at or datetime.min,
            item[1].id,
        ),
        reverse=True,
    )
    return render_template(
        "mypage/reviews.html",
        reviews=user_reviews,
        accommodation_reviews=accommodation_reviews,
        review_items=review_items,
    )


@mypage_bp.post("/reviews/destination/<int:review_id>/delete")
@login_required
def delete_destination_review(review_id):
    review = db.session.get(Review, review_id)
    if review is None or review.user_id != g.user.id:
        abort(404)
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for("mypage.reviews"))


@mypage_bp.post("/reviews/accommodation/<int:review_id>/delete")
@login_required
def delete_accommodation_review(review_id):
    review = db.session.get(AccommodationReview, review_id)
    if review is None or review.user_id != g.user.id:
        abort(404)
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for("mypage.reviews"))


@mypage_bp.route("/profile", methods=("GET", "POST"))
@login_required
def profile():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()

        if not name or not phone:
            flash("이름과 전화번호를 모두 입력해 주세요.", "error")
        else:
            g.user.name = name
            g.user.phone = phone
            db.session.commit()
            flash("회원정보가 수정되었습니다.", "success")
            return redirect(url_for("mypage.profile"))

    return render_template(
        "mypage/profile.html",
        user=g.user,
        deletion_date=format_deletion_date(g.user.scheduled_deletion_at),
    )


@mypage_bp.post("/profile/withdrawal")
@login_required
def schedule_withdrawal():
    password = request.form.get("password") or ""
    confirmed = request.form.get("confirm_withdrawal") == "yes"

    if g.user.scheduled_deletion_at is not None:
        flash("이미 회원 탈퇴가 예약되어 있습니다.", "warning")
    elif not check_password_hash(g.user.password_hash, password):
        flash("현재 비밀번호가 올바르지 않습니다.", "error")
    elif not confirmed:
        flash("탈퇴 안내를 확인해 주세요.", "error")
    else:
        requested_at = utcnow()
        g.user.withdrawal_requested_at = requested_at
        g.user.scheduled_deletion_at = requested_at + timedelta(days=30)
        deletion_date = format_deletion_date(g.user.scheduled_deletion_at)
        db.session.commit()
        session.clear()
        flash(
            f"회원 탈퇴가 예약되었습니다. 계정은 {deletion_date}에 삭제됩니다.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return redirect(url_for("mypage.profile"))


@mypage_bp.post("/profile/withdrawal/cancel")
@login_required
def cancel_withdrawal():
    if g.user.scheduled_deletion_at is None:
        flash("예약된 회원 탈퇴가 없습니다.", "warning")
    else:
        g.user.withdrawal_requested_at = None
        g.user.scheduled_deletion_at = None
        db.session.commit()
        flash("회원 탈퇴 예약이 철회되었습니다.", "success")

    return redirect(url_for("mypage.profile"))
