import unittest
from contextlib import contextmanager

from flask import g, template_rendered
from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app, db
from app.auth_helpers import get_safe_next_url, login_required
from app.models import User


class TestConfig:
    TESTING = True
    SECRET_KEY = "phase3-test-key"
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


class AuthenticationHelperTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)

        @self.app.get("/_test/private")
        @login_required
        def private_page():
            return "private"

        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            email="leader@example.com",
            password_hash=generate_password_hash("password123"),
            name="팀장",
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

    def test_safe_next_url_accepts_only_internal_paths(self):
        valid_targets = (
            "/mypage",
            "/destinations/1?tab=reviews",
        )
        invalid_targets = (
            None,
            "",
            "mypage",
            "https://example.com",
            "//example.com/path",
            "///example.com/path",
            "/\\example.com/path",
            "javascript:alert(1)",
        )

        for target in valid_targets:
            with self.subTest(target=target):
                self.assertEqual(get_safe_next_url(target), target)

        for target in invalid_targets:
            with self.subTest(target=target):
                self.assertIsNone(get_safe_next_url(target))

    def test_request_loads_logged_in_user_into_g(self):
        with self.client:
            with self.client.session_transaction() as session:
                session["user_id"] = self.user_id

            response = self.client.get("/")

            self.assertEqual(response.status_code, 200)
            self.assertIsNotNone(g.user)
            self.assertEqual(g.user.id, self.user_id)

    def test_stale_session_user_is_removed(self):
        with self.client:
            with self.client.session_transaction() as session:
                session["user_id"] = 9999

            response = self.client.get("/")

            self.assertEqual(response.status_code, 200)
            self.assertIsNone(g.user)
            with self.client.session_transaction() as session:
                self.assertNotIn("user_id", session)

    def test_login_required_redirects_with_original_internal_path(self):
        response = self.client.get(
            "/_test/private?from=destination",
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/auth/login?next=/_test/private?from%3Ddestination",
        )

    def test_login_required_allows_authenticated_user(self):
        with self.client.session_transaction() as session:
            session["user_id"] = self.user_id

        response = self.client.get("/_test/private")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "private")


class AuthenticationRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            email="member@example.com",
            password_hash=generate_password_hash("old-password"),
            name="회원",
            phone="010-0000-0000",
        )
        db.session.add(self.user)
        db.session.commit()
        self.user_id = self.user.id
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup_normalizes_email_and_hashes_password(self):
        plain_password = "new-password"
        response = self.client.post(
            "/auth/signup",
            data={
                "email": "  NEW@Example.COM ",
                "password": plain_password,
                "password_confirm": plain_password,
                "name": " 신규 회원 ",
                "phone": " 010-1111-2222 ",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/auth/login")
        user = db.session.scalar(
            db.select(User).where(User.email == "new@example.com")
        )
        self.assertIsNotNone(user)
        self.assertNotEqual(user.password_hash, plain_password)
        self.assertTrue(check_password_hash(user.password_hash, plain_password))
        self.assertEqual(user.name, "신규 회원")
        self.assertEqual(user.phone, "010-1111-2222")

    def test_signup_rejects_duplicate_email(self):
        response = self.client.post(
            "/auth/signup",
            data={
                "email": " MEMBER@EXAMPLE.COM ",
                "password": "another-password",
                "password_confirm": "another-password",
                "name": "다른 회원",
                "phone": "010-9999-9999",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("이미 가입된 이메일입니다.", response.get_data(as_text=True))
        count = db.session.scalar(db.select(db.func.count(User.id)))
        self.assertEqual(count, 1)

    def test_login_success_and_logout(self):
        response = self.client.post(
            "/auth/login",
            data={"email": "MEMBER@EXAMPLE.COM", "password": "old-password"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_id"], self.user_id)

        self.assertEqual(self.client.get("/auth/logout").status_code, 405)
        response = self.client.post("/auth/logout", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as session:
            self.assertNotIn("user_id", session)

    def test_anonymous_logout_is_redirected_to_login(self):
        response = self.client.post("/auth/logout", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "/auth/login?next=/auth/logout",
        )

    def test_login_failure_does_not_reveal_account_existence(self):
        messages = []
        for email, password in (
            ("member@example.com", "wrong-password"),
            ("missing@example.com", "wrong-password"),
        ):
            response = self.client.post(
                "/auth/login",
                data={"email": email, "password": password},
            )
            page = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("이메일 또는 비밀번호가 올바르지 않습니다.", page)
            messages.append(page)

        self.assertEqual(
            ["이메일 또는 비밀번호가 올바르지 않습니다." in page for page in messages],
            [True, True],
        )

    def test_login_uses_only_safe_next_url(self):
        response = self.client.post(
            "/auth/login?next=/mypage",
            data={"email": "member@example.com", "password": "old-password"},
            follow_redirects=False,
        )
        self.assertEqual(response.headers["Location"], "/mypage")

        self.client.post("/auth/logout")
        response = self.client.post(
            "/auth/login?next=https://example.com",
            data={"email": "member@example.com", "password": "old-password"},
            follow_redirects=False,
        )
        self.assertEqual(response.headers["Location"], "/")

    def test_find_email(self):
        with captured_templates(self.app) as templates:
            response = self.client.post(
                "/auth/find-email",
                data={"name": "회원", "phone": "010-0000-0000"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(templates[-1][1]["found_email"], "member@example.com")

    def test_reset_password_replaces_hash_and_allows_new_login(self):
        previous_hash = self.user.password_hash
        response = self.client.post(
            "/auth/reset-password",
            data={
                "email": "MEMBER@EXAMPLE.COM",
                "name": "회원",
                "phone": "010-0000-0000",
                "password": "updated-password",
                "password_confirm": "updated-password",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        db.session.refresh(self.user)
        self.assertNotEqual(self.user.password_hash, previous_hash)
        self.assertTrue(
            check_password_hash(self.user.password_hash, "updated-password")
        )

        response = self.client.post(
            "/auth/login",
            data={
                "email": "member@example.com",
                "password": "updated-password",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)


if __name__ == "__main__":
    unittest.main()
