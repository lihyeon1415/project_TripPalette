import unittest
from contextlib import contextmanager
from types import SimpleNamespace

from flask import template_rendered
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import Destination, User, UserPreference
from app.recommendation_service import recommend_destinations, score_destination


class TestConfig:
    TESTING = True
    SECRET_KEY = "phase4-recommendation-test-key"
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


class RecommendationServiceTestCase(unittest.TestCase):
    def test_score_contains_only_real_matches_and_three_reasons(self):
        destination = SimpleNamespace(
            id=1,
            season="가을",
            purpose="문화",
            atmosphere="전통적인",
            budget_level="보통",
            recommended_days=2,
        )
        preference = SimpleNamespace(
            season="가을",
            companion="가족",
            purpose="문화",
            atmosphere="전통적인",
            budget=300000,
            trip_duration=2,
        )

        score, reasons = score_destination(destination, preference)

        self.assertEqual(score, 13)
        self.assertEqual(len(reasons), 3)
        self.assertIn("가을", reasons[0])

    def test_recommendations_sort_by_score_then_id_and_support_fallback(self):
        preference = SimpleNamespace(
            season="봄",
            companion="혼자",
            purpose="자연",
            atmosphere="조용한",
            budget=150000,
            trip_duration=1,
        )
        destinations = [
            SimpleNamespace(id=2, season="겨울", purpose="문화", atmosphere="활기찬", budget_level=None, recommended_days=5),
            SimpleNamespace(id=1, season="봄", purpose="자연", atmosphere="조용한", budget_level="저렴", recommended_days=1),
        ]

        recommendations, fallback = recommend_destinations(destinations, preference)
        self.assertFalse(fallback)
        self.assertEqual(recommendations[0]["destination"].id, 1)

        fallback_items, fallback = recommend_destinations(destinations, None)
        self.assertTrue(fallback)
        self.assertEqual([item["destination"].id for item in fallback_items], [1, 2])


class RecommendationRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            email="traveler@example.com",
            password_hash=generate_password_hash("password123"),
            name="여행자",
            phone="010-1111-2222",
        )
        self.other_user = User(
            email="other@example.com",
            password_hash=generate_password_hash("password123"),
            name="다른 회원",
            phone="010-3333-4444",
        )
        self.andong = Destination(
            name="안동",
            region="경상북도",
            description="전통 문화 여행지",
            season="가을",
            purpose="문화",
            atmosphere="전통적인",
            budget_level="보통",
            recommended_days=2,
        )
        self.jeju = Destination(
            name="제주",
            region="제주특별자치도",
            description="사계절 자연 여행지",
            season="사계절",
            purpose="자연",
            atmosphere="낭만적인",
            budget_level="높음",
            recommended_days=3,
        )
        db.session.add_all((self.user, self.other_user, self.andong, self.jeju))
        db.session.commit()
        self.user_id = self.user.id
        self.other_user_id = self.other_user.id
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
        self.assertTrue(templates)
        return response, templates[-1][0].name, templates[-1][1]

    @staticmethod
    def preference_data(**overrides):
        data = {
            "season": "가을",
            "companion": "가족",
            "purpose": "문화",
            "atmosphere": "전통적인",
            "budget": "300000",
            "trip_duration": "2",
        }
        data.update(overrides)
        return data

    def test_anonymous_access_redirects_to_login_with_original_path(self):
        for path in ("/recommend/survey", "/recommend/result"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertIn("/auth/login?next=", response.headers["Location"])

    def test_first_submission_saves_preference_and_redirects(self):
        self.login_as(self.user_id)
        response = self.client.post("/recommend/survey", data=self.preference_data())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/recommend/result")
        preference = db.session.scalar(
            db.select(UserPreference).where(UserPreference.user_id == self.user_id)
        )
        self.assertEqual(preference.season, "가을")
        self.assertEqual(preference.budget, 300000)

    def test_resubmission_updates_single_row_and_restores_form(self):
        self.login_as(self.user_id)
        self.client.post("/recommend/survey", data=self.preference_data())
        self.client.post(
            "/recommend/survey",
            data=self.preference_data(season="겨울", budget="500000"),
        )

        preferences = list(
            db.session.execute(
                db.select(UserPreference).where(UserPreference.user_id == self.user_id)
            ).scalars()
        )
        self.assertEqual(len(preferences), 1)
        self.assertEqual(preferences[0].season, "겨울")

        response, template, context = self.get_context("/recommend/survey")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "recommendation/survey.html")
        self.assertTrue(context["has_preference"])
        self.assertEqual(context["form_data"]["budget"], "500000")

    def test_long_trip_accepts_over_500k_budget_and_returns_recommendations(self):
        self.login_as(self.user_id)
        response = self.client.post(
            "/recommend/survey",
            data=self.preference_data(budget="1000000", trip_duration="5"),
        )
        self.assertEqual(response.status_code, 302)

        preference = db.session.scalar(
            db.select(UserPreference).where(UserPreference.user_id == self.user_id)
        )
        self.assertEqual(preference.budget, 1000000)
        self.assertEqual(preference.trip_duration, 5)

        response, _, context = self.get_context("/recommend/result")
        self.assertTrue(context["recommendations"])
        self.assertIn("50만원 이상", response.get_data(as_text=True))

    def test_invalid_or_missing_values_do_not_save(self):
        self.login_as(self.user_id)
        response = self.client.post(
            "/recommend/survey",
            data=self.preference_data(season="장마", purpose=""),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(
            db.session.scalar(
                db.select(UserPreference).where(UserPreference.user_id == self.user_id)
            )
        )

    def test_preferences_are_isolated_by_user(self):
        self.login_as(self.user_id)
        self.client.post("/recommend/survey", data=self.preference_data())
        self.login_as(self.other_user_id)
        self.client.post(
            "/recommend/survey",
            data=self.preference_data(season="봄", companion="혼자"),
        )

        rows = list(db.session.execute(db.select(UserPreference)).scalars())
        self.assertEqual(len(rows), 2)
        self.assertEqual({row.user_id for row in rows}, {self.user_id, self.other_user_id})

    def test_result_contains_ranked_reasoned_destination_links(self):
        self.login_as(self.user_id)
        self.client.post("/recommend/survey", data=self.preference_data())
        response, template, context = self.get_context("/recommend/result")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "recommendation/result.html")
        self.assertFalse(context["fallback_mode"])
        self.assertEqual(context["recommendations"][0]["destination"].name, "안동")
        self.assertTrue(context["recommendations"][0]["reasons"])
        self.assertIn(f'/destinations/{self.andong.id}', response.get_data(as_text=True))

    def test_no_preference_and_empty_database_are_safe(self):
        self.login_as(self.user_id)
        _, _, context = self.get_context("/recommend/result")
        self.assertTrue(context["fallback_mode"])
        self.assertEqual(len(context["recommendations"]), 2)

        Destination.query.delete()
        db.session.commit()
        response, _, context = self.get_context("/recommend/result")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(context["recommendations"], [])

    def test_entry_links_exist_without_adding_primary_header_navigation(self):
        main_page = self.client.get("/").get_data(as_text=True)
        self.assertIn('href="/recommend/survey"', main_page)

        self.login_as(self.user_id)
        favorites_page = self.client.get("/mypage/favorites").get_data(as_text=True)
        self.assertIn("맞춤 여행 설정", favorites_page)
        self.assertNotIn("맞춤 추천</a>", favorites_page.split("<header", 1)[0])


if __name__ == "__main__":
    unittest.main()
