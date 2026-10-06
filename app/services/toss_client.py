import base64
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import current_app


class TossPaymentError(RuntimeError):
    def __init__(self, code, message, status_code=None, retryable=False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable


def _authorization_header():
    secret_key = current_app.config.get("TOSS_SECRET_KEY", "")
    if not secret_key:
        raise TossPaymentError("TOSS_NOT_CONFIGURED", "토스 테스트 시크릿 키가 설정되지 않았습니다.")
    token = base64.b64encode(f"{secret_key}:".encode()).decode()
    return f"Basic {token}"


def _request(method, path, payload=None, idempotency_key=None):
    base_url = current_app.config["TOSS_API_BASE_URL"].rstrip("/")
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {
        "Authorization": _authorization_header(),
        "Content-Type": "application/json",
    }
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key
    request = Request(base_url + path, data=data, headers=headers, method=method)
    try:
        with urlopen(
            request,
            timeout=current_app.config.get("TOSS_API_TIMEOUT_SECONDS", 10),
        ) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        try:
            body = json.loads(error.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            body = {}
        raise TossPaymentError(
            body.get("code", "TOSS_HTTP_ERROR"),
            body.get("message", "토스페이먼츠 요청을 처리하지 못했습니다."),
            status_code=error.code,
            retryable=error.code >= 500,
        ) from error
    except (URLError, TimeoutError) as error:
        raise TossPaymentError(
            "TOSS_NETWORK_ERROR",
            "토스페이먼츠 응답을 확인하지 못했습니다. 잠시 후 다시 시도해 주세요.",
            retryable=True,
        ) from error


def confirm_payment(payment_key, order_id, amount, idempotency_key):
    return _request(
        "POST",
        "/v1/payments/confirm",
        {"paymentKey": payment_key, "orderId": order_id, "amount": amount},
        idempotency_key,
    )


def get_payment(payment_key):
    return _request("GET", f"/v1/payments/{quote(payment_key, safe='')}")


def cancel_payment(payment_key, reason, idempotency_key):
    return _request(
        "POST",
        f"/v1/payments/{quote(payment_key, safe='')}/cancel",
        {"cancelReason": reason},
        idempotency_key,
    )
