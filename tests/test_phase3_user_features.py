import unittest
from contextlib import contextmanager

from flask import template_rendered
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Destination, Favorite, Review, User


class TestConfig:
    TESTING = True
    SECRET_KEY = "phase3-user-feature-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class Phase3UserFeatureTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            email="first@example.com",
            password_hash=generate_password_hash("password123"),
            name="첫 번째 회원",
            phone="010-1111-1111",
        )
        self.other_user = User(
            email="second@example.com",
            password_hash=generate_password_hash("password123"),
            name="두 번째 회원",
            phone="010-2222-2222",
        )
        self.destination = Destination(
            name="제주",
            region="제주특별자치도",
            description="테스트 여행지",
        )
        self.other_destination = Destination(
            name="강릉",
            region="강원특별자치도",
            description="다른 테스트 여행지",
        )
        db.session.add_all(
            (self.user, self.other_user, self.destination, self.other_destination)
        )
        db.session.commit()
        self.user_id = self.user.id
        self.other_user_id = self.other_user.id
        self.destination_id = self.destination.id
        self.other_destination_id = self.other_destination.id
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_as(self, user_id):
        with self.client.session_transaction() as session:
            session["user_id"] = user_id

    def get_context(self, path):
        with captured_templates(self.app) as templates:
            response = self.client.get(path)
        self.assertTrue(templates, f"Template이 렌더링되지 않았습니다: {path}")
        return response, templates[-1][1]

    def test_anonymous_user_is_redirected_from_every_mypage_route(self):
        for path in (
            "/mypage",
            "/mypage/favorites",
            "/mypage/reviews",
            "/mypage/profile",
            "/mypage/reservations",
        ):
            with self.subTest(path=path):
                response = self.client.get(path, follow_redirects=False)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response.headers["Location"].startswith("/auth/login"))

    def test_favorite_toggle_and_detail_context(self):
        self.login_as(self.user_id)

        response = self.client.post(
            f"/destinations/{self.destination_id}/favorite",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn("_flashes", session)
        favorite = db.session.scalar(
            db.select(Favorite).where(Favorite.user_id == self.user_id)
        )
        self.assertIsNotNone(favorite)

        _, context = self.get_context(f"/destinations/{self.destination_id}")
        self.assertTrue(context["is_favorite"])

        self.client.post(f"/destinations/{self.destination_id}/favorite")
        favorite = db.session.scalar(
            db.select(Favorite).where(Favorite.user_id == self.user_id)
        )
        self.assertIsNone(favorite)

    def test_favorites_are_isolated_by_user(self):
        db.session.add_all(
            (
                Favorite(
                    user_id=self.user_id,
                    destination_id=self.destination_id,
                ),
                Favorite(
                    user_id=self.other_user_id,
                    destination_id=self.other_destination_id,
                ),
            )
        )
        db.session.commit()
        self.login_as(self.user_id)

        _, context = self.get_context("/mypage/favorites")

        self.assertEqual(len(context["favorites"]), 1)
        self.assertEqual(context["favorites"][0].destination.name, "제주")

    def test_review_validation_duplicate_prevention_and_detail_context(self):
        self.login_as(self.user_id)
        review_url = f"/destinations/{self.destination_id}/reviews"

        for data in (
            {"rating": "0", "content": "평점 오류"},
            {"rating": "6", "content": "평점 오류"},
            {"rating": "not-number", "content": "평점 오류"},
            {"rating": "5", "content": "   "},
        ):
            with self.subTest(data=data):
                response = self.client.post(review_url, data=data)
                self.assertEqual(response.status_code, 302)

        self.assertEqual(
            db.session.scalar(db.select(db.func.count(Review.id))),
            0,
        )

        self.client.post(review_url, data={"rating": "5", "content": " 최고예요 "})
        review = db.session.scalar(db.select(Review))
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.content, "최고예요")

        self.client.post(review_url, data={"rating": "4", "content": "두 번째"})
        self.assertEqual(
            db.session.scalar(db.select(db.func.count(Review.id))),
            1,
        )

        _, context = self.get_context(f"/destinations/{self.destination_id}")
        self.assertFalse(context["can_review"])

    def test_reviews_are_isolated_by_user(self):
        db.session.add_all(
            (
                Review(
                    user_id=self.user_id,
                    destination_id=self.destination_id,
                    rating=5,
                    content="내 리뷰",
                ),
                Review(
                    user_id=self.other_user_id,
                    destination_id=self.other_destination_id,
                    rating=4,
                    content="다른 회원 리뷰",
                ),
            )
        )
        db.session.commit()
        self.login_as(self.user_id)

        response, context = self.get_context("/mypage/reviews")

        self.assertEqual(len(context["reviews"]), 1)
        self.assertEqual(context["reviews"][0].content, "내 리뷰")
        page = response.get_data(as_text=True)
        self.assertIn("내 리뷰", page)
        self.assertNotIn("다른 회원 리뷰", page)

    def test_user_can_delete_only_own_destination_review(self):
        own_review = Review(
            user_id=self.user_id,
            destination_id=self.destination_id,
            rating=5,
            content="삭제할 여행지 리뷰",
        )
        other_review = Review(
            user_id=self.other_user_id,
            destination_id=self.other_destination_id,
            rating=4,
            content="남겨둘 여행지 리뷰",
        )
        db.session.add_all((own_review, other_review))
        db.session.commit()
        own_review_id = own_review.id
        other_review_id = other_review.id
        self.login_as(self.user_id)

        self.assertEqual(
            self.client.post(
                f"/mypage/reviews/destination/{other_review_id}/delete"
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                f"/mypage/reviews/destination/{own_review_id}/delete"
            ).status_code,
            405,
        )
        response = self.client.post(
            f"/mypage/reviews/destination/{own_review_id}/delete",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/mypage/reviews")
        self.assertIsNone(db.session.get(Review, own_review_id))
        self.assertIsNotNone(db.session.get(Review, other_review_id))
        with self.client.session_transaction() as session:
            self.assertNotIn("_flashes", session)

    def test_mypage_index_redirects_to_favorites(self):
        self.login_as(self.user_id)

        response = self.client.get("/mypage", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/mypage/favorites")

    def test_profile_updates_only_name_and_phone(self):
        original_email = self.user.email
        other_name = self.other_user.name
        self.login_as(self.user_id)

        response = self.client.post(
            "/mypage/profile",
            data={
                "name": " 수정된 이름 ",
                "phone": " 010-9999-9999 ",
                "email": "attacker@example.com",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.user)
        db.session.refresh(self.other_user)
        self.assertEqual(self.user.name, "수정된 이름")
        self.assertEqual(self.user.phone, "010-9999-9999")
        self.assertEqual(self.user.email, original_email)
        self.assertEqual(self.other_user.name, other_name)

    def test_missing_destination_returns_404_for_user_actions(self):
        self.login_as(self.user_id)

        self.assertEqual(
            self.client.post("/destinations/9999/favorite").status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                "/destinations/9999/reviews",
                data={"rating": "5", "content": "없는 여행지"},
            ).status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()
