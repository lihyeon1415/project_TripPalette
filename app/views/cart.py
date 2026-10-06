from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload

from app import db
from app.auth_helpers import login_required
from app.models import CartItem, Product
from app.services.goods_order_service import (
    MAX_ORDER_QUANTITY,
    SHIPPING_FEE,
    GoodsOrderValidationError,
    create_goods_order_from_cart,
)
from app.services.payment_service import expire_pending_payments


cart_bp = Blueprint("cart", __name__)


def _quantity(value):
    try:
        quantity = int(value)
    except (TypeError, ValueError):
        return None
    return quantity if 1 <= quantity <= MAX_ORDER_QUANTITY else None


def _cart_item_or_404(item_id):
    item = db.session.scalar(
        db.select(CartItem)
        .options(joinedload(CartItem.product))
        .where(CartItem.id == item_id)
    )
    if item is None or item.user_id != g.user.id:
        abort(404)
    return item


def _cart_context(form_data=None, checkout_modal_open=False):
    items = db.session.execute(
        db.select(CartItem)
        .options(joinedload(CartItem.product))
        .where(CartItem.user_id == g.user.id)
        .order_by(CartItem.created_at, CartItem.id)
    ).scalars().all()
    items_amount = sum(item.product.price * item.quantity for item in items)
    if form_data is None:
        form_data = {
            "recipient_name": g.user.name,
            "recipient_phone": g.user.phone,
        }
    return {
        "items": items,
        "items_amount": items_amount,
        "shipping_fee": SHIPPING_FEE if items else 0,
        "total_amount": items_amount + (SHIPPING_FEE if items else 0),
        "form_data": form_data,
        "checkout_modal_open": checkout_modal_open,
    }


@cart_bp.get("")
@login_required
def detail():
    expire_pending_payments()
    return render_template("cart/mypage_cart.html", **_cart_context())


@cart_bp.post("/items/<int:product_id>")
@login_required
def add_item(product_id):
    quantity = _quantity(request.form.get("quantity", "1"))
    product = db.session.get(Product, product_id)
    if product is None or not product.is_active:
        abort(404)
    if quantity is None:
        flash(f"수량은 1개 이상 {MAX_ORDER_QUANTITY}개 이하로 선택해 주세요.", "error")
        return redirect(url_for("goods.detail", product_id=product.id))

    item = db.session.scalar(
        db.select(CartItem).where(
            CartItem.user_id == g.user.id,
            CartItem.product_id == product.id,
        )
    )
    next_quantity = quantity + (item.quantity if item else 0)
    if next_quantity > MAX_ORDER_QUANTITY:
        flash(f"상품별 최대 {MAX_ORDER_QUANTITY}개까지 담을 수 있습니다.", "error")
        return redirect(url_for("goods.detail", product_id=product.id))
    if next_quantity > product.stock_quantity:
        flash("선택한 수량만큼 재고가 남아 있지 않습니다.", "error")
        return redirect(url_for("goods.detail", product_id=product.id))

    if item is None:
        item = CartItem(user_id=g.user.id, product_id=product.id, quantity=quantity)
        db.session.add(item)
    else:
        item.quantity = next_quantity
    db.session.commit()
    return redirect(url_for("cart.detail"))


@cart_bp.post("/items/<int:item_id>/quantity")
@login_required
def update_item(item_id):
    item = _cart_item_or_404(item_id)
    quantity = _quantity(request.form.get("quantity"))
    if quantity is None or quantity > item.product.stock_quantity:
        flash("변경할 수량과 재고를 확인해 주세요.", "error")
    else:
        item.quantity = quantity
        db.session.commit()
    return redirect(url_for("cart.detail"))


@cart_bp.post("/items/<int:item_id>/delete")
@login_required
def delete_item(item_id):
    item = _cart_item_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("cart.detail"))


@cart_bp.post("/items/delete-selected")
@login_required
def delete_selected_items():
    item_ids = request.form.getlist("cart_item_ids", type=int)
    if not item_ids:
        flash("삭제할 상품을 선택해 주세요.", "error")
        return redirect(url_for("cart.detail"))
    items = db.session.execute(
        db.select(CartItem).where(
            CartItem.user_id == g.user.id,
            CartItem.id.in_(item_ids),
        )
    ).scalars().all()
    for item in items:
        db.session.delete(item)
    db.session.commit()
    return redirect(url_for("cart.detail"))


@cart_bp.post("/checkout")
@login_required
def checkout():
    expire_pending_payments()
    form_data = request.form.to_dict()
    selected_ids = request.form.getlist("cart_item_ids", type=int)
    if request.form.get("selection_present") == "1" and not selected_ids:
        flash("주문할 상품을 선택해 주세요.", "error")
        return render_template(
            "cart/mypage_cart.html",
            **_cart_context(form_data=form_data, checkout_modal_open=True),
        ), 400
    try:
        order = create_goods_order_from_cart(
            g.user.id,
            request.form,
            cart_item_ids=selected_ids or None,
        )
        db.session.commit()
    except GoodsOrderValidationError as error:
        db.session.rollback()
        for message in error.errors:
            flash(message, "error")
        return render_template(
            "cart/mypage_cart.html",
            **_cart_context(form_data=form_data, checkout_modal_open=True),
        ), 400
    except Exception:
        db.session.rollback()
        raise
    return redirect(url_for("payment.checkout", payment_id=order.payment.id))
