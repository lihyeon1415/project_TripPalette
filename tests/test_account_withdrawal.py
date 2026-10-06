import unittest
from datetime import timedelta

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.account_deletion import utcnow
from app.models import (
    Accommodation,
    AccommodationReview,
    Destination,
    Favorite,
    GoodsOrder,
    GoodsOrderItem,
    Payment,
    Product,
    Reservation,
    Review,
    User,
    UserPreference,
)


class TestConfig:
    TESTING = True
    SECRET_KEY = "account-withdrawal-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class AccountWithdrawalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            email="withdrawal@example.com",
            password_hash=generate_password_hash("password123"),
            name="탈퇴 테스트",
            phone="010-1234-5678",
        )
        db.session.add(self.user)
        db.session.commit()
        self.user_id = self.user.id
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_as_user(self):
        with self.client.session_transaction() as session:
            session["user_id"] = self.user_id

    def test_withdrawal_requires_current_password(self):
        self.login_as_user()

        response = self.client.post(
            "/mypage/profile/withdrawal",
            data={"password": "wrong", "confirm_withdrawal": "yes"},
        )

        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.user)
        self.assertIsNone(self.user.scheduled_deletion_at)

    def test_user_can_schedule_login_and_cancel_withdrawal(self):
        self.login_as_user()
        before_request = utcnow()

        response = self.client.post(
            "/mypage/profile/withdrawal",
            data={"password": "password123", "confirm_withdrawal": "yes"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/auth/login")
        db.session.refresh(self.user)
        self.assertIsNotNone(self.user.withdrawal_requested_at)
        self.assertGreaterEqual(
            self.user.scheduled_deletion_at,
            before_request + timedelta(days=30),
        )
        with self.client.session_transaction() as session:
            self.assertNotIn("user_id", session)

        response = self.client.post(
            "/auth/login",
            data={"email": self.user.email, "password": "password123"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            "/mypage/profile/withdrawal/cancel",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.user)
        self.assertIsNone(self.user.withdrawal_requested_at)
        self.assertIsNone(self.user.scheduled_deletion_at)

    def test_expired_withdrawal_is_purged_and_session_is_cleared(self):
        destination = Destination(
            name="테스트 여행지",
            region="테스트 지역",
        )
        db.session.add(destination)
        db.session.flush()
        accommodation = Accommodation(
            destination_id=destination.id,
            name="테스트 숙소",
            address="테스트 주소",
            price_per_night=100000,
            capacity=2,
        )
        db.session.add(accommodation)
        db.session.flush()
        reservation = Reservation(
            user_id=self.user_id,
            accommodation_id=accommodation.id,
            check_in=utcnow().date() + timedelta(days=10),
            check_out=utcnow().date() + timedelta(days=11),
            people_count=2,
            total_price=100000,
        )
        db.session.add_all(
            (
                UserPreference(user_id=self.user_id, season="가을"),
                Favorite(user_id=self.user_id, destination_id=destination.id),
                Review(
                    user_id=self.user_id,
                    destination_id=destination.id,
                    rating=5,
                    content="좋아요",
                ),
                AccommodationReview(
                    user_id=self.user_id,
                    accommodation_id=accommodation.id,
                    rating=5,
                    content="숙소도 좋아요",
                ),
                reservation,
            )
        )
        db.session.flush()
        db.session.add(
            Payment(
                reservation_id=reservation.id,
                amount=100000,
                payment_method="CARD",
            )
        )
        self.user.withdrawal_requested_at = utcnow() - timedelta(days=31)
        self.user.scheduled_deletion_at = utcnow() - timedelta(days=1)
        db.session.commit()
        self.login_as_user()

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(db.session.get(User, self.user_id))
        for model in (
            UserPreference,
            Favorite,
            Review,
            AccommodationReview,
            Reservation,
            Payment,
        ):
            self.assertEqual(
                db.session.scalar(db.select(db.func.count(model.id))),
                0,
            )
        with self.client.session_transaction() as session:
            self.assertNotIn("user_id", session)

    def make_goods_order(self, status):
        product = Product(
            sku=f"WITHDRAWAL-{status}",
            name="탈퇴 테스트 굿즈",
            price=10000,
            stock_quantity=10,
        )
        db.session.add(product)
        db.session.flush()
        order = GoodsOrder(
            order_number=f"GOODS-WITHDRAWAL-{status}",
            user_id=self.user_id,
            recipient_name="탈퇴 수령인",
            recipient_phone="010-1111-2222",
            postal_code="12345",
            address="삭제되어야 할 주소",
            address_detail="101호",
            delivery_request="문 앞",
            items_amount=10000,
            shipping_fee=3000,
            total_amount=13000,
            status=status,
            expires_at=utcnow() + timedelta(minutes=10),
        )
        order.items.append(
            GoodsOrderItem(
                product=product,
                product_name=product.name,
                sku=product.sku,
                unit_price=10000,
                quantity=1,
                subtotal=10000,
            )
        )
        order.payment = Payment(
            merchant_order_id=f"PAY-WITHDRAWAL-{status}",
            amount=13000,
            payment_status="CANCELLED" if status == "CANCELLED" else "APPROVED",
        )
        db.session.add(order)
        return order

    def test_terminal_goods_order_is_preserved_and_anonymized(self):
        order = self.make_goods_order("CANCELLED")
        self.user.withdrawal_requested_at = utcnow() - timedelta(days=31)
        self.user.scheduled_deletion_at = utcnow() - timedelta(days=1)
        db.session.commit()
        order_id = order.id
        payment_id = order.payment.id

        self.assertEqual(self.app.test_cli_runner().invoke(args=["purge-withdrawn-users"]).exit_code, 0)
        db.session.expire_all()
        preserved = db.session.get(GoodsOrder, order_id)
        self.assertIsNone(db.session.get(User, self.user_id))
        self.assertIsNotNone(preserved)
        self.assertIsNone(preserved.user_id)
        self.assertEqual(preserved.recipient_name, "탈퇴 회원")
        self.assertEqual(preserved.recipient_phone, "")
        self.assertEqual(preserved.address, "삭제된 배송지")
        self.assertIsNotNone(db.session.get(Payment, payment_id))

    def test_active_goods_order_delays_permanent_account_deletion(self):
        order = self.make_goods_order("PAID")
        self.user.withdrawal_requested_at = utcnow() - timedelta(days=31)
        self.user.scheduled_deletion_at = utcnow() - timedelta(days=1)
        db.session.commit()

        result = self.app.test_cli_runner().invoke(args=["purge-withdrawn-users"])
        db.session.expire_all()
        self.assertEqual(result.exit_code, 0)
        self.assertIsNotNone(db.session.get(User, self.user_id))
        self.assertEqual(db.session.get(GoodsOrder, order.id).user_id, self.user_id)


if __name__ == "__main__":
    unittest.main()
