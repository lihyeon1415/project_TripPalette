from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from sqlalchemy.orm import selectinload

from app import db
from app.auth_helpers import login_required
from app.models import Product, ProductCategory
from app.services.goods_order_service import (
    SHIPPING_FEE,
    GoodsOrderValidationError,
    create_goods_order,
)
from app.services.payment_service import expire_pending_payments


goods_bp = Blueprint("goods", __name__)
ALLOWED_CATEGORIES = {"all", "travel", "daily", "stationery"}
CATEGORY_LABELS = {
    "travel": "PALLY TRAVEL",
    "daily": "PALLY DAILY",
    "stationery": "PALLY STATIONERY",
}


def _active_product_or_404(product_id):
    product = db.session.scalar(
        db.select(Product)
        .options(selectinload(Product.images), selectinload(Product.categories))
        .where(Product.id == product_id, Product.is_active.is_(True))
    )
    if product is None:
        abort(404)
    return product


def _detail_context(product, form_data=None, buy_modal_open=False):
    related_products = db.session.execute(
        db.select(Product)
        .options(selectinload(Product.images))
        .where(Product.is_active.is_(True), Product.id != product.id)
        .order_by(Product.id)
        .limit(2)
    ).scalars().all()
    category_names = {category.category for category in product.categories}
    category = next(
        (name for name in ("travel", "daily", "stationery") if name in category_names),
        "daily",
    )
    if form_data is None:
        form_data = {
            "quantity": "1",
            "recipient_name": g.user.name if g.user else "",
            "recipient_phone": g.user.phone if g.user else "",
        }
    return {
        "product": product,
        "related_products": related_products,
        "category_label": CATEGORY_LABELS[category],
        "shipping_fee": SHIPPING_FEE,
        "form_data": form_data,
        "buy_modal_open": buy_modal_open,
    }


@goods_bp.get("")
def list_products():
    category = request.args.get("category", "all")
    if category not in ALLOWED_CATEGORIES:
        abort(404)
    statement = (
        db.select(Product)
        .options(selectinload(Product.images), selectinload(Product.categories))
        .where(Product.is_active.is_(True))
        .order_by(Product.id)
    )
    if category != "all":
        statement = statement.where(Product.categories.any(ProductCategory.category == category))
    products = db.session.execute(statement).scalars().all()
    return render_template("goods/list.html", products=products, category=category)


@goods_bp.get("/<int:product_id>")
def detail(product_id):
    product = _active_product_or_404(product_id)
    return render_template(
        "goods/detail.html",
        **_detail_context(
            product,
            buy_modal_open=request.args.get("buy") == "1",
        ),
    )


@goods_bp.get("/<int:product_id>/checkout")
@login_required
def checkout(product_id):
    _active_product_or_404(product_id)
    return redirect(url_for("goods.detail", product_id=product_id, buy=1))


@goods_bp.post("/<int:product_id>/orders")
@login_required
def create_order(product_id):
    # 만료된 주문이 확보한 재고를 새 주문 전에 즉시 반환한다.
    expire_pending_payments()
    product = _active_product_or_404(product_id)
    form_data = request.form.to_dict()
    try:
        order = create_goods_order(g.user.id, product.id, request.form)
        db.session.commit()
    except GoodsOrderValidationError as error:
        db.session.rollback()
        for message in error.errors:
            flash(message, "error")
        return (
            render_template(
                "goods/detail.html",
                **_detail_context(product, form_data=form_data, buy_modal_open=True),
            ),
            400,
        )
    except Exception:
        db.session.rollback()
        raise
    return redirect(url_for("payment.checkout", payment_id=order.payment.id))
