import tempfile
import unittest
from pathlib import Path

from config import build_database_engine_options, build_database_uri


class DatabaseConfigTestCase(unittest.TestCase):
    def test_individual_mysql_settings_preserve_special_password(self):
        uri = build_database_uri(
            "",
            {
                "MYSQL_HOST": "example.aivencloud.com",
                "MYSQL_PORT": "12345",
                "MYSQL_DATABASE": "trippalette",
                "MYSQL_USER": "trippalette_app",
                "MYSQL_PASSWORD": "special:@/password",
            },
        )

        self.assertEqual(uri.host, "example.aivencloud.com")
        self.assertEqual(uri.port, 12345)
        self.assertEqual(uri.database, "trippalette")
        self.assertEqual(uri.username, "trippalette_app")
        self.assertEqual(uri.password, "special:@/password")

    def test_partial_individual_mysql_settings_are_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "완전하지 않습니다"):
            build_database_uri("", {"MYSQL_HOST": "example.aivencloud.com"})

    def test_mysql_port_must_be_numeric(self):
        with self.assertRaisesRegex(RuntimeError, "MYSQL_PORT는 숫자"):
            build_database_uri(
                "",
                {
                    "MYSQL_HOST": "example.aivencloud.com",
                    "MYSQL_PORT": "not-a-number",
                    "MYSQL_DATABASE": "trippalette",
                    "MYSQL_USER": "trippalette_app",
                    "MYSQL_PASSWORD": "password",
                },
            )

    def test_default_options_keep_connection_pool_healthy(self):
        options = build_database_engine_options("sqlite://", "")

        self.assertIs(options["pool_pre_ping"], True)
        self.assertEqual(options["pool_recycle"], 280)
        self.assertNotIn("connect_args", options)

    def test_aiven_mysql_requires_ca_certificate(self):
        with self.assertRaisesRegex(RuntimeError, "MYSQL_SSL_CA"):
            build_database_engine_options(
                "mysql+pymysql://user:password@example.aivencloud.com:12345/db",
                "",
            )

    def test_missing_ca_file_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "찾을 수 없습니다"):
            build_database_engine_options(
                "mysql+pymysql://user:password@example.aivencloud.com:12345/db",
                "instance/missing-aiven-ca.pem",
            )

    def test_aiven_mysql_verifies_ca_and_hostname(self):
        with tempfile.TemporaryDirectory() as directory:
            ca_path = Path(directory) / "aiven-ca.pem"
            ca_path.write_text(
                "-----BEGIN CERTIFICATE-----\nplaceholder\n-----END CERTIFICATE-----\n",
                encoding="utf-8",
            )

            options = build_database_engine_options(
                "mysql+pymysql://user:password@example.aivencloud.com:12345/db",
                str(ca_path),
            )

        self.assertEqual(options["connect_args"]["ssl_ca"], str(ca_path.resolve()))
        self.assertIs(options["connect_args"]["ssl_verify_cert"], True)
        self.assertIs(options["connect_args"]["ssl_verify_identity"], True)


if __name__ == "__main__":
    unittest.main()
