from flask import Blueprint, abort, flash, g, redirect, render_template, url_for
from sqlalchemy.orm import joinedload, selectinload

from app import db
from app.auth_helpers import login_required
from app.models import GoodsOrder, GoodsOrderItem
from app.services import toss_client
from app.services.payment_service import PaymentValidationError, cancel_order_payment


order_bp = Blueprint("order", __name__)


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
    return render_template("order/detail.html", order=_user_order_or_404(order_id))


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
