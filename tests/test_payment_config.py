import unittest

from app import create_app


class BaseTestConfig:
    TESTING = True
    SECRET_KEY = "payment-config-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class PaymentConfigTestCase(unittest.TestCase):
    def test_app_runs_without_payment_keys_before_payment_is_configured(self):
        app = create_app(BaseTestConfig)

        self.assertTrue(app.testing)

    def test_test_keys_are_accepted(self):
        class TestPaymentConfig(BaseTestConfig):
            TOSS_CLIENT_KEY = "test_client_key"
            TOSS_SECRET_KEY = "test_secret_key"
            TOSS_PAYMENT_MODE = "test"

        app = create_app(TestPaymentConfig)

        self.assertEqual(app.config["TOSS_PAYMENT_MODE"], "test")

    def test_live_client_key_is_rejected(self):
        class LiveClientConfig(BaseTestConfig):
            TOSS_CLIENT_KEY = "live_client_key"
            TOSS_SECRET_KEY = "test_secret_key"
            TOSS_PAYMENT_MODE = "test"

        with self.assertRaisesRegex(RuntimeError, "테스트 키만"):
            create_app(LiveClientConfig)

    def test_live_secret_key_is_rejected(self):
        class LiveSecretConfig(BaseTestConfig):
            TOSS_CLIENT_KEY = "test_client_key"
            TOSS_SECRET_KEY = "live_secret_key"
            TOSS_PAYMENT_MODE = "test"

        with self.assertRaisesRegex(RuntimeError, "테스트 키만"):
            create_app(LiveSecretConfig)

    def test_incomplete_key_pair_is_rejected(self):
        class IncompleteConfig(BaseTestConfig):
            TOSS_CLIENT_KEY = "test_client_key"
            TOSS_SECRET_KEY = ""
            TOSS_PAYMENT_MODE = "test"

        with self.assertRaisesRegex(RuntimeError, "함께 설정"):
            create_app(IncompleteConfig)

    def test_non_test_payment_mode_is_rejected(self):
        class LiveModeConfig(BaseTestConfig):
            TOSS_CLIENT_KEY = "test_client_key"
            TOSS_SECRET_KEY = "test_secret_key"
            TOSS_PAYMENT_MODE = "live"

        with self.assertRaisesRegex(RuntimeError, "테스트 결제만"):
            create_app(LiveModeConfig)


if __name__ == "__main__":
    unittest.main()
