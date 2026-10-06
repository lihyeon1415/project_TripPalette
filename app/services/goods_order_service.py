import re
import uuid
from datetime import UTC, datetime, timedelta

from app import db
from app.models import GoodsOrder, GoodsOrderItem, Payment, Product


MAX_ORDER_QUANTITY = 10
SHIPPING_FEE = 3000
ORDER_EXPIRATION_MINUTES = 10


class GoodsOrderValidationError(ValueError):
    def __init__(self, errors):
        super().__init__(errors[0])
        self.errors = errors


def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


def validate_checkout_data(form):
    errors = []
    cleaned = {}

    try:
        quantity = int(form.get("quantity", ""))
    except (TypeError, ValueError):
        quantity = None
    if quantity is None or not 1 <= quantity <= MAX_ORDER_QUANTITY:
        errors.append(f"수량은 1개 이상 {MAX_ORDER_QUANTITY}개 이하로 입력해 주세요.")
    else:
        cleaned["quantity"] = quantity

    limits = {
        "recipient_name": ("받는 분", 50),
        "recipient_phone": ("연락처", 20),
        "postal_code": ("우편번호", 10),
        "address": ("주소", 255),
    }
    for field, (label, maximum) in limits.items():
        value = str(form.get(field, "")).strip()
        if not value:
            errors.append(f"{label}을(를) 입력해 주세요.")
        elif len(value) > maximum:
            errors.append(f"{label}은(는) {maximum}자 이내로 입력해 주세요.")
        cleaned[field] = value

    phone = cleaned.get("recipient_phone", "")
    if phone and not re.fullmatch(r"01[016789]-?\d{3,4}-?\d{4}", phone):
        errors.append("연락처를 휴대전화 번호 형식으로 입력해 주세요.")
    postal_code = cleaned.get("postal_code", "")
    if postal_code and not re.fullmatch(r"\d{5}", postal_code):
        errors.append("우편번호는 숫자 5자리로 입력해 주세요.")

    for field, label in (
        ("address_detail", "상세 주소"),
        ("delivery_request", "배송 요청사항"),
    ):
        value = str(form.get(field, "")).strip()
        if len(value) > 255:
            errors.append(f"{label}은(는) 255자 이내로 입력해 주세요.")
        cleaned[field] = value or None

    if errors:
        raise GoodsOrderValidationError(errors)
    return cleaned


def create_goods_order(user_id, product_id, form):
    data = validate_checkout_data(form)
    product = db.session.scalar(
        db.select(Product).where(Product.id == product_id).with_for_update()
    )
    if product is None or not product.is_active:
        raise GoodsOrderValidationError(["판매 중인 상품을 찾을 수 없습니다."])
    if product.stock_quantity < data["quantity"]:
        raise GoodsOrderValidationError(["선택한 수량만큼 재고가 남아 있지 않습니다."])

    product.stock_quantity -= data["quantity"]
    items_amount = product.price * data["quantity"]
    order = GoodsOrder(
        order_number=f"GOODS-{uuid.uuid4().hex.upper()}",
        user_id=user_id,
        recipient_name=data["recipient_name"],
        recipient_phone=data["recipient_phone"],
        postal_code=data["postal_code"],
        address=data["address"],
        address_detail=data["address_detail"],
        delivery_request=data["delivery_request"],
        items_amount=items_amount,
        shipping_fee=SHIPPING_FEE,
        total_amount=items_amount + SHIPPING_FEE,
        status="PAYMENT_PENDING",
        expires_at=utcnow() + timedelta(minutes=ORDER_EXPIRATION_MINUTES),
    )
    order.items.append(
        GoodsOrderItem(
            product=product,
            product_name=product.name,
            sku=product.sku,
            unit_price=product.price,
            quantity=data["quantity"],
            subtotal=items_amount,
        )
    )
    order.payment = Payment(
        merchant_order_id=order.order_number,
        amount=order.total_amount,
        payment_status="READY",
        idempotency_key=str(uuid.uuid4()),
    )
    db.session.add(order)
    db.session.flush()
    return order


def release_goods_order_stock(order, status="CANCELLED"):
    """Restore reserved stock once while the order is awaiting payment."""
    if order.status != "PAYMENT_PENDING":
        return False
    for item in order.items:
        product = db.session.scalar(
            db.select(Product).where(Product.id == item.product_id).with_for_update()
        )
        if product is not None:
            product.stock_quantity += item.quantity
    now = utcnow()
    order.status = status
    order.cancelled_at = now
    if order.payment is not None:
        order.payment.payment_status = "CANCELLED" if status == "CANCELLED" else "FAILED"
        order.payment.cancelled_at = now
        if status == "EXPIRED":
            order.payment.failure_code = "ORDER_EXPIRED"
            order.payment.failure_message = "결제 가능 시간이 만료되었습니다."
    return True


def expire_pending_goods_orders(now=None):
    cutoff = now or utcnow()
    orders = db.session.execute(
        db.select(GoodsOrder)
        .where(
            GoodsOrder.status == "PAYMENT_PENDING",
            GoodsOrder.expires_at <= cutoff,
        )
        .with_for_update()
    ).scalars().all()
    released = sum(release_goods_order_stock(order, "EXPIRED") for order in orders)
    db.session.commit()
    return released
