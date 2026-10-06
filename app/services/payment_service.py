import uuid
from datetime import UTC, datetime, timedelta

from app import db
from app.models import GoodsOrder, Payment, Product, Reservation
from app.services import toss_client
from app.services.goods_order_service import release_goods_order_stock


PAYMENT_EXPIRATION_MINUTES = 10


class PaymentValidationError(ValueError):
    pass


def utcnow():
    return datetime.now(UTC).replace(tzinfo=None)


def new_order_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex.upper()}"


def ensure_customer_key(user):
    if not user.payment_customer_key:
        user.payment_customer_key = f"tp_{uuid.uuid4().hex}"
    return user.payment_customer_key


def create_reservation_payment(reservation):
    reservation.status = "PAYMENT_PENDING"
    reservation.expires_at = utcnow() + timedelta(minutes=PAYMENT_EXPIRATION_MINUTES)
    payment = Payment(
        reservation=reservation,
        merchant_order_id=new_order_id("STAY"),
        amount=reservation.total_price,
        payment_status="READY",
        idempotency_key=str(uuid.uuid4()),
    )
    db.session.add(payment)
    return payment


def payment_target(payment):
    return payment.reservation or payment.goods_order


def payment_owner_id(payment):
    target = payment_target(payment)
    return target.user_id if target else None


def payment_order_name(payment):
    if payment.reservation:
        return f"{payment.reservation.accommodation.name} 숙소 예약"[:100]
    if payment.goods_order and payment.goods_order.items:
        first = payment.goods_order.items[0]
        extra = len(payment.goods_order.items) - 1
        return (first.product_name if extra == 0 else f"{first.product_name} 외 {extra}건")[:100]
    return "TripPalette 결제"


def _release_reservation(reservation, status):
    if reservation.status != "PAYMENT_PENDING":
        return False
    reservation.status = status
    return True


def fail_pending_payment(payment, code, message, target_status="FAILED"):
    if payment.payment_status != "READY":
        return False
    if payment.reservation:
        _release_reservation(payment.reservation, target_status)
    elif payment.goods_order:
        release_goods_order_stock(payment.goods_order, target_status)
    payment.payment_status = "FAILED" if target_status != "CANCELLED" else "CANCELLED"
    payment.failure_code = (code or "PAYMENT_FAILED")[:100]
    payment.failure_message = (message or "결제가 완료되지 않았습니다.")[:255]
    payment.cancelled_at = utcnow()
    return True


def expire_payment(payment, now=None):
    cutoff = now or utcnow()
    target = payment_target(payment)
    if payment.payment_status != "READY" or target is None:
        return False
    if target.expires_at is None or target.expires_at > cutoff:
        return False
    return fail_pending_payment(
        payment,
        "PAYMENT_EXPIRED",
        "결제 가능 시간이 만료되었습니다.",
        "EXPIRED",
    )


def expire_pending_payments(now=None):
    cutoff = now or utcnow()
    payments = db.session.execute(
        db.select(Payment)
        .where(
            Payment.payment_status == "READY",
            db.or_(
                Payment.reservation.has(Reservation.expires_at <= cutoff),
                Payment.goods_order.has(GoodsOrder.expires_at <= cutoff),
            ),
        )
        .with_for_update()
    ).scalars().all()
    count = sum(expire_payment(payment, cutoff) for payment in payments)
    db.session.commit()
    return count


def _validate_approved_response(payment, result, payment_key):
    if result.get("paymentKey") != payment_key:
        raise PaymentValidationError("승인된 결제키가 요청값과 일치하지 않습니다.")
    if result.get("orderId") != payment.merchant_order_id:
        raise PaymentValidationError("승인된 주문번호가 서버 주문번호와 일치하지 않습니다.")
    if result.get("totalAmount") != payment.amount:
        raise PaymentValidationError("승인된 금액이 서버 결제금액과 일치하지 않습니다.")
    if result.get("status") != "DONE":
        raise PaymentValidationError("결제가 최종 승인 상태가 아닙니다.")


def _complete_payment(payment, result, payment_key):
    _validate_approved_response(payment, result, payment_key)
    now = utcnow()
    payment.payment_key = payment_key
    payment.payment_method = result.get("method")
    payment.payment_status = "APPROVED"
    payment.paid_at = now
    payment.failure_code = None
    payment.failure_message = None
    if payment.reservation:
        payment.reservation.status = "CONFIRMED"
    else:
        payment.goods_order.status = "PAID"
        payment.goods_order.paid_at = now
    return payment


def approve_payment(payment_id, payment_key, order_id, returned_amount):
    payment = db.session.scalar(
        db.select(Payment).where(Payment.id == payment_id).with_for_update()
    )
    if payment is None:
        raise PaymentValidationError("결제 정보를 찾을 수 없습니다.")
    if not payment_key or len(payment_key) > 200:
        raise PaymentValidationError("결제키가 올바르지 않습니다.")
    try:
        amount = int(returned_amount)
    except (TypeError, ValueError) as error:
        raise PaymentValidationError("결제 금액 형식이 올바르지 않습니다.") from error
    if order_id != payment.merchant_order_id or amount != payment.amount:
        fail_pending_payment(
            payment,
            "PAYMENT_DATA_MISMATCH",
            "결제 요청값이 서버 주문 정보와 일치하지 않습니다.",
        )
        raise PaymentValidationError("결제 요청값이 서버에 저장된 주문 정보와 일치하지 않습니다.")
    if payment.payment_status == "APPROVED":
        if payment.payment_key == payment_key:
            return payment
        raise PaymentValidationError("이미 다른 결제키로 승인된 주문입니다.")
    if payment.payment_status != "READY":
        raise PaymentValidationError("승인할 수 없는 결제 상태입니다.")
    if expire_payment(payment):
        raise PaymentValidationError("결제 가능 시간이 만료되었습니다.")

    try:
        result = toss_client.confirm_payment(
            payment_key,
            payment.merchant_order_id,
            payment.amount,
            payment.idempotency_key,
        )
    except toss_client.TossPaymentError as error:
        try:
            result = toss_client.get_payment(payment_key)
        except toss_client.TossPaymentError:
            if not error.retryable:
                fail_pending_payment(payment, error.code, error.message)
            raise
    return _complete_payment(payment, result, payment_key)


def cancel_order_payment(payment, reason="고객 요청으로 결제 취소"):
    if payment.payment_status == "READY":
        fail_pending_payment(payment, "CUSTOMER_CANCEL", reason, "CANCELLED")
        return payment
    if payment.payment_status == "CANCELLED":
        return payment
    if payment.payment_status != "APPROVED" or not payment.payment_key:
        raise PaymentValidationError("취소할 수 없는 결제 상태입니다.")

    cancel_key = f"cancel-{payment.idempotency_key}"
    result = toss_client.cancel_payment(payment.payment_key, reason[:200], cancel_key)
    if result.get("status") not in ("CANCELED", "PARTIAL_CANCELED"):
        raise PaymentValidationError("토스 결제 취소가 완료되지 않았습니다.")

    now = utcnow()
    payment.payment_status = "CANCELLED"
    payment.cancelled_at = now
    if payment.reservation:
        payment.reservation.status = "CANCELLED"
    else:
        for item in payment.goods_order.items:
            product = db.session.scalar(
                db.select(Product).where(Product.id == item.product_id).with_for_update()
            )
            if product is not None:
                product.stock_quantity += item.quantity
        payment.goods_order.status = "CANCELLED"
        payment.goods_order.cancelled_at = now
    return payment
