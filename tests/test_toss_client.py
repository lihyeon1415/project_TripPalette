import base64
import json
import unittest
from unittest.mock import patch

from app import create_app
from app.services.toss_client import confirm_payment


class TestConfig:
    TESTING = True
    SECRET_KEY = "toss-client-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOSS_CLIENT_KEY = "test_ck_browser"
    TOSS_SECRET_KEY = "test_sk_server"
    TOSS_PAYMENT_MODE = "test"
    TOSS_API_BASE_URL = "https://api.tosspayments.com"
    TOSS_API_TIMEOUT_SECONDS = 1


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return b'{"status":"DONE"}'


class TossClientTestCase(unittest.TestCase):
    def test_confirm_uses_server_secret_colon_and_idempotency_header(self):
        app = create_app(TestConfig)
        with app.app_context(), patch(
            "app.services.toss_client.urlopen",
            return_value=FakeResponse(),
        ) as mocked_urlopen:
            result = confirm_payment("payment-key", "ORDER-123456", 12000, "idem-key")

        request = mocked_urlopen.call_args.args[0]
        headers = {key.lower(): value for key, value in request.header_items()}
        expected_token = base64.b64encode(b"test_sk_server:").decode()
        self.assertEqual(request.full_url, "https://api.tosspayments.com/v1/payments/confirm")
        self.assertEqual(headers["authorization"], f"Basic {expected_token}")
        self.assertEqual(headers["idempotency-key"], "idem-key")
        self.assertEqual(
            json.loads(request.data.decode()),
            {"paymentKey": "payment-key", "orderId": "ORDER-123456", "amount": 12000},
        )
        self.assertEqual(result["status"], "DONE")


if __name__ == "__main__":
    unittest.main()
