import unittest
from datetime import UTC, date, datetime, timedelta
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Accommodation, Destination, Payment, Reservation, User
from app.services.payment_service import expire_pending_payments


class TestConfig:
    TESTING = True
    SECRET_KEY = "toss-payment-flow-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOSS_CLIENT_KEY = "test_ck_test-client"
    TOSS_SECRET_KEY = "test_sk_test-secret"
    TOSS_PAYMENT_MODE = "test"
    TOSS_API_BASE_URL = "https://api.tosspayments.com"
    TOSS_API_TIMEOUT_SECONDS = 1


class TossPaymentFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.destination = Destination(name="결제 여행지", region="테스트")
        self.user = User(
            email="pay@example.com",
            password_hash=generate_password_hash("password123"),
            name="결제 사용자",
            phone="010-1234-5678",
        )
        db.session.add_all((self.destination, self.user))
        db.session.flush()
        self.accommodation = Accommodation(
            destination_id=self.destination.id,
            name="결제 테스트 숙소",
            address="테스트 주소",
            price_per_night=100000,
            capacity=2,
        )
        db.session.add(self.accommodation)
        db.session.commit()
        self.user_id = self.user.id
        self.accommodation_id = self.accommodation.id
        self.client = self.app.test_client()
        with self.client.session_transaction() as session:
            session["user_id"] = self.user_id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def create_pending_reservation(self):
        check_in = date.today() + timedelta(days=5)
        response = self.client.post(
            f"/reservations/new/{self.accommodation_id}",
            data={
                "check_in": check_in.isoformat(),
                "check_out": (check_in + timedelta(days=2)).isoformat(),
                "people_count": "2",
            },
        )
        payment = db.session.scalar(db.select(Payment))
        return response, payment

    @staticmethod
    def approved_result(payment, payment_key="test-payment-key"):
        return {
            "paymentKey": payment_key,
            "orderId": payment.merchant_order_id,
            "totalAmount": payment.amount,
            "status": "DONE",
            "method": "카드",
        }

    def test_reservation_opens_v2_payment_modal_on_booking_page(self):
        response, payment = self.create_pending_reservation()
        page = self.client.get(response.location).get_data(as_text=True)
        self.assertIn("https://js.tosspayments.com/v2/standard", page)
        self.assertIn("test_ck_test-client", page)
        self.assertNotIn("test_sk_test-secret", page)
        self.assertIn(payment.merchant_order_id, page)
        self.assertIn('data-amount="200000"', page)
        self.assertIn('data-stay-payment-modal', page)
        self.assertIn('class="stay-payment-layer"', page)
        self.assertNotIn('<dialog class="stay-payment-modal"', page)
        self.assertIn("결제 방법", page)
        self.assertNotIn("테스트 결제", page)
        self.assertIn('id="stay-payment-method"', page)
        self.assertIn('id="stay-payment-agreement"', page)
        self.assertIn("/static/js/payment/payment-widget.js", page)

    def test_success_approves_once_and_confirms_reservation(self):
        _, payment = self.create_pending_reservation()
        success_url = (
            f"/payments/{payment.id}/success?paymentKey=test-payment-key"
            f"&orderId={payment.merchant_order_id}&amount={payment.amount}"
        )
        with patch(
            "app.services.payment_service.toss_client.confirm_payment",
            return_value=self.approved_result(payment),
        ) as confirm:
            first = self.client.get(success_url)
            second = self.client.get(success_url)

        db.session.refresh(payment)
        db.session.refresh(payment.reservation)
        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(confirm.call_count, 1)
        self.assertEqual(payment.payment_status, "APPROVED")
        self.assertEqual(payment.reservation.status, "CONFIRMED")

    def test_amount_mismatch_fails_and_releases_dates(self):
        _, payment = self.create_pending_reservation()
        response = self.client.get(
            f"/payments/{payment.id}/success?paymentKey=test-payment-key"
            f"&orderId={payment.merchant_order_id}&amount=1"
        )
        db.session.refresh(payment)
        db.session.refresh(payment.reservation)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(payment.payment_status, "FAILED")
        self.assertEqual(payment.reservation.status, "FAILED")

        retry = self.client.post(
            f"/reservations/new/{self.accommodation_id}",
            data={
                "check_in": payment.reservation.check_in.isoformat(),
                "check_out": payment.reservation.check_out.isoformat(),
                "people_count": "1",
            },
        )
        self.assertEqual(retry.status_code, 302)

    def test_fail_url_without_order_id_releases_dates(self):
        _, payment = self.create_pending_reservation()
        response = self.client.get(
            f"/payments/{payment.id}/fail?code=PAY_PROCESS_CANCELED&message=cancelled"
        )
        db.session.refresh(payment)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(payment.payment_status, "FAILED")
        self.assertEqual(payment.reservation.status, "FAILED")

    def test_expiration_releases_pending_reservation(self):
        _, payment = self.create_pending_reservation()
        payment.reservation.expires_at = datetime.now(UTC).replace(tzinfo=None) - timedelta(seconds=1)
        db.session.commit()
        self.assertEqual(expire_pending_payments(), 1)
        db.session.refresh(payment)
        self.assertEqual(payment.payment_status, "FAILED")
        self.assertEqual(payment.reservation.status, "EXPIRED")

    def test_confirmed_reservation_uses_toss_cancel_api(self):
        _, payment = self.create_pending_reservation()
        with patch(
            "app.services.payment_service.toss_client.confirm_payment",
            return_value=self.approved_result(payment),
        ):
            self.client.get(
                f"/payments/{payment.id}/success?paymentKey=test-payment-key"
                f"&orderId={payment.merchant_order_id}&amount={payment.amount}"
            )
        with patch(
            "app.services.payment_service.toss_client.cancel_payment",
            return_value={"status": "CANCELED"},
        ) as cancel:
            response = self.client.post(f"/reservations/{payment.reservation_id}/cancel")
        db.session.refresh(payment)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(cancel.call_count, 1)
        self.assertEqual(payment.payment_status, "CANCELLED")
        self.assertEqual(payment.reservation.status, "CANCELLED")


if __name__ == "__main__":
    unittest.main()
