from datetime import date, timedelta

from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy.orm import joinedload

from app import db
from app.auth_helpers import login_required
from app.models import Accommodation, Reservation
from app.services import toss_client
from app.services.payment_service import (
    PaymentValidationError,
    cancel_order_payment,
    create_reservation_payment,
    expire_pending_payments,
)


reservation_bp = Blueprint("reservation", __name__)


def _parse_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


@reservation_bp.route("/new/<int:accommodation_id>", methods=("GET", "POST"))
@login_required
def create(accommodation_id):
    accommodation = db.get_or_404(Accommodation, accommodation_id)
    today = date.today()
    form_data = {
        "check_in": request.form.get("check_in", ""),
        "check_out": request.form.get("check_out", ""),
        "people_count": request.form.get("people_count", "1"),
    }

    if request.method == "GET":
        form_data["check_in"] = (today + timedelta(days=1)).isoformat()
        form_data["check_out"] = (today + timedelta(days=2)).isoformat()

    if request.method == "POST":
        # 스케줄러 실행 사이에도 새 예약이 만료 건에 막히지 않도록 먼저 정리한다.
        expire_pending_payments()
        check_in = _parse_date(form_data["check_in"])
        check_out = _parse_date(form_data["check_out"])
        try:
            people_count = int(form_data["people_count"])
        except (TypeError, ValueError):
            people_count = None

        error = None
        if check_in is None or check_out is None:
            error = "체크인과 체크아웃 날짜를 정확히 선택해 주세요."
        elif check_in < today:
            error = "오늘 이전 날짜로는 예약할 수 없습니다."
        elif check_out <= check_in:
            error = "체크아웃은 체크인 이후 날짜여야 합니다."
        elif people_count is None or people_count < 1:
            error = "예약 인원은 1명 이상이어야 합니다."
        elif people_count > accommodation.capacity:
            error = f"이 숙소는 최대 {accommodation.capacity}명까지 예약할 수 있습니다."
        else:
            conflicting_reservation = db.session.scalar(
                db.select(Reservation.id).where(
                    Reservation.accommodation_id == accommodation.id,
                    Reservation.status.in_(("PENDING", "PAYMENT_PENDING", "CONFIRMED")),
                    Reservation.check_in < check_out,
                    Reservation.check_out > check_in,
                )
            )
            if conflicting_reservation is not None:
                error = "선택한 날짜에는 이미 예약이 있습니다. 다른 날짜를 선택해 주세요."

        if error is None:
            nights = (check_out - check_in).days
            reservation = Reservation(
                user_id=g.user.id,
                accommodation_id=accommodation.id,
                check_in=check_in,
                check_out=check_out,
                people_count=people_count,
                total_price=accommodation.price_per_night * nights,
                status="PAYMENT_PENDING",
            )
            db.session.add(reservation)
            payment = create_reservation_payment(reservation)
            db.session.commit()
            return redirect(url_for("payment.checkout", payment_id=payment.id))

        flash(error, "error")

    return render_template(
        "reservation/form.html",
        accommodation=accommodation,
        form_data=form_data,
        today=today.isoformat(),
    )


def _get_user_reservation_or_404(reservation_id):
    reservation = db.session.scalar(
        db.select(Reservation)
        .options(
            joinedload(Reservation.accommodation).joinedload(
                Accommodation.destination
            )
        )
        .where(Reservation.id == reservation_id)
    )
    if reservation is None or reservation.user_id != g.user.id:
        abort(404)
    return reservation


@reservation_bp.get("/<int:id>/payment")
@login_required
def payment(id):
    reservation = _get_user_reservation_or_404(id)
    if reservation.payment is None:
        abort(404)
    return redirect(url_for("payment.checkout", payment_id=reservation.payment.id))


@reservation_bp.get("/<int:id>/complete")
@login_required
def complete(id):
    reservation = _get_user_reservation_or_404(id)
    if reservation.status == "PAYMENT_PENDING" and reservation.payment:
        return redirect(url_for("payment.checkout", payment_id=reservation.payment.id))
    return render_template("reservation/complete.html", reservation=reservation)


@reservation_bp.post("/<int:id>/cancel")
@login_required
def cancel(id):
    reservation = _get_user_reservation_or_404(id)
    if reservation.payment is None:
        if reservation.status in ("PENDING", "CONFIRMED"):
            reservation.status = "CANCELLED"
            db.session.commit()
        return redirect(url_for("reservation.complete", id=reservation.id))
    try:
        cancel_order_payment(reservation.payment, "숙소 예약 취소")
        db.session.commit()
    except (PaymentValidationError, toss_client.TossPaymentError) as error:
        db.session.rollback()
        message = error.message if isinstance(error, toss_client.TossPaymentError) else str(error)
        flash(message, "error")
    return redirect(url_for("reservation.complete", id=reservation.id))
