from datetime import UTC, datetime

from flask import Blueprint, abort, flash, g, redirect, render_template, url_for
from sqlalchemy.orm import joinedload, selectinload

from app import db
from app.auth_helpers import login_required
from app.models import GoodsOrder, GoodsOrderItem
from app.services import toss_client
from app.services.payment_service import (
    PaymentValidationError,
    cancel_order_payment,
    expire_pending_payments,
)


order_bp = Blueprint("order", __name__)

ORDER_STATUS_LABELS = {
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

ORDER_STATUS_MESSAGES = {
    "PAYMENT_PENDING": "결제 가능 시간 안에 결제를 완료해 주세요.",
    "PAID": "결제가 완료되었습니다. 주문하신 상품을 준비하고 있습니다.",
    "PREPARING": "상품을 안전하게 포장하고 있습니다.",
    "SHIPPED": "상품이 배송 중입니다.",
    "DELIVERED": "배송이 완료되었습니다.",
    "CANCELLED": "취소된 주문입니다.",
    "REFUNDED": "결제 금액의 환불이 완료되었습니다.",
    "FAILED": "결제가 완료되지 않았습니다.",
    "PAYMENT_FAILED": "결제가 완료되지 않았습니다.",
    "EXPIRED": "결제 가능 시간이 만료되어 주문이 자동 취소되었습니다.",
}


def _user_order_or_404(order_id):
    order = db.session.scalar(
        db.select(GoodsOrder)
        .options(
            selectinload(GoodsOrder.items).joinedload(GoodsOrderItem.product),
            joinedload(GoodsOrder.payment),
        )
        .where(GoodsOrder.id == order_id)
    )
    if order is None or order.user_id != g.user.id:
        abort(404)
    return order


@order_bp.get("/<int:order_id>")
@login_required
def detail(order_id):
    expire_pending_payments()
    order = _user_order_or_404(order_id)
    return render_template(
        "order/detail.html",
        order=order,
        status_label=ORDER_STATUS_LABELS.get(order.status, order.status),
        status_message=ORDER_STATUS_MESSAGES.get(
            order.status,
            "현재 주문 상태를 확인해 주세요.",
        ),
    )


@order_bp.post("/<int:order_id>/cancel")
@login_required
def cancel(order_id):
    order = _user_order_or_404(order_id)
    try:
        cancel_order_payment(order.payment, "굿즈 주문 취소")
        db.session.commit()
        flash("주문이 취소되어 확보했던 재고를 복구했습니다.", "success")
    except (PaymentValidationError, toss_client.TossPaymentError) as error:
        db.session.rollback()
        message = error.message if isinstance(error, toss_client.TossPaymentError) else str(error)
        flash(message, "error")
    return redirect(url_for("order.detail", order_id=order.id))


@order_bp.post("/<int:order_id>/hide")
@login_required
def hide(order_id):
    expire_pending_payments()
    order = _user_order_or_404(order_id)
    if order.status not in {"EXPIRED", "CANCELLED"}:
        abort(409, description="결제 만료 또는 주문 취소 항목만 목록에서 삭제할 수 있습니다.")

    order.hidden_at = datetime.now(UTC).replace(tzinfo=None)
    db.session.commit()
    flash("주문을 주문 내역에서 삭제했습니다.", "success")
    return redirect(url_for("mypage.orders"))
