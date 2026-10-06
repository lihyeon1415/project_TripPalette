from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload, selectinload

from app import db
from app.auth_helpers import login_required
from app.models import GoodsOrder, GoodsOrderItem, Payment, Reservation
from app.services import toss_client
from app.services.payment_service import (
    PaymentValidationError,
    approve_payment,
    ensure_customer_key,
    expire_payment,
    fail_pending_payment,
    payment_order_name,
    payment_owner_id,
    payment_target,
)


payment_bp = Blueprint("payment", __name__)


def _user_payment_or_404(payment_id, lock=False):
    statement = (
        db.select(Payment)
        .options(
            joinedload(Payment.reservation).joinedload(Reservation.accommodation),
            joinedload(Payment.goods_order)
            .selectinload(GoodsOrder.items)
            .joinedload(GoodsOrderItem.product),
        )
        .where(Payment.id == payment_id)
    )
    if lock:
        statement = statement.with_for_update()
    payment = db.session.scalar(statement)
    if payment is None or payment_owner_id(payment) != g.user.id:
        abort(404)
    return payment


@payment_bp.get("/<int:payment_id>")
@login_required
def checkout(payment_id):
    payment = _user_payment_or_404(payment_id)
    if payment.payment_status == "APPROVED":
        return redirect(url_for("payment.complete", payment_id=payment.id))
    if expire_payment(payment):
        db.session.commit()
        flash("결제 가능 시간이 만료되었습니다. 다시 예약하거나 주문해 주세요.", "error")
        return redirect(url_for("payment.failed", payment_id=payment.id))
    if payment.payment_status != "READY":
        return redirect(url_for("payment.failed", payment_id=payment.id))

    customer_key = ensure_customer_key(g.user)
    db.session.commit()
    return render_template(
        "payment/checkout.html",
        payment=payment,
        target=payment_target(payment),
        order_name=payment_order_name(payment),
        customer_key=customer_key,
        client_key=current_app.config.get("TOSS_CLIENT_KEY", ""),
        success_url=url_for("payment.success", payment_id=payment.id, _external=True),
        fail_url=url_for("payment.fail", payment_id=payment.id, _external=True),
    )


@payment_bp.get("/<int:payment_id>/success")
@login_required
def success(payment_id):
    payment = _user_payment_or_404(payment_id)
    try:
        approve_payment(
            payment.id,
            request.args.get("paymentKey"),
            request.args.get("orderId"),
            request.args.get("amount"),
        )
        db.session.commit()
    except (PaymentValidationError, toss_client.TossPaymentError) as error:
        db.session.commit()
        message = error.message if isinstance(error, toss_client.TossPaymentError) else str(error)
        flash(message, "error")
        return redirect(url_for("payment.failed", payment_id=payment.id))
    return redirect(url_for("payment.complete", payment_id=payment.id))


@payment_bp.get("/<int:payment_id>/fail")
@login_required
def fail(payment_id):
    payment = _user_payment_or_404(payment_id, lock=True)
    code = request.args.get("code", "PAYMENT_FAILED")
    message = request.args.get("message", "결제가 완료되지 않았습니다.")
    order_id = request.args.get("orderId")
    if order_id and order_id != payment.merchant_order_id:
        abort(400)
    fail_pending_payment(payment, code, message)
    db.session.commit()
    flash(message, "error")
    return redirect(url_for("payment.failed", payment_id=payment.id))


@payment_bp.get("/<int:payment_id>/complete")
@login_required
def complete(payment_id):
    payment = _user_payment_or_404(payment_id)
    if payment.payment_status != "APPROVED":
        return redirect(url_for("payment.failed", payment_id=payment.id))
    if payment.reservation:
        return redirect(url_for("reservation.complete", id=payment.reservation.id))
    return redirect(url_for("order.detail", order_id=payment.goods_order.id))


@payment_bp.get("/<int:payment_id>/failed")
@login_required
def failed(payment_id):
    payment = _user_payment_or_404(payment_id)
    return render_template("payment/failed.html", payment=payment, target=payment_target(payment))
