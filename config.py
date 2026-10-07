import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL


load_dotenv()


def build_database_uri(database_url=None, environ=None):
    """Return a database URI without requiring manual password URL encoding."""
    environ = environ if environ is not None else os.environ
    database_url = str(
        database_url if database_url is not None else environ.get("DATABASE_URL", "")
    ).strip()
    if database_url:
        return database_url

    mysql_settings = {
        "host": str(environ.get("MYSQL_HOST", "")).strip(),
        "port": str(environ.get("MYSQL_PORT", "")).strip(),
        "database": str(environ.get("MYSQL_DATABASE", "")).strip(),
        "username": str(environ.get("MYSQL_USER", "")).strip(),
        "password": str(environ.get("MYSQL_PASSWORD", "")),
    }
    if not any(mysql_settings.values()):
        return None

    missing = [name for name, value in mysql_settings.items() if not value]
    if missing:
        raise RuntimeError(
            "MySQL 개별 환경변수가 완전하지 않습니다: " + ", ".join(missing)
        )

    try:
        port = int(mysql_settings["port"])
    except ValueError as error:
        raise RuntimeError("MYSQL_PORT는 숫자여야 합니다.") from error

    return URL.create(
        "mysql+pymysql",
        username=mysql_settings["username"],
        password=mysql_settings["password"],
        host=mysql_settings["host"],
        port=port,
        database=mysql_settings["database"],
        query={"charset": "utf8mb4"},
    )


def build_database_engine_options(database_url=None, mysql_ssl_ca=None):
    """Build SQLAlchemy pool and verified TLS options for MySQL.

    Aiven MySQL is reached over the public network.  Connections to an Aiven
    hostname must therefore provide the project CA and verify both the
    certificate chain and server hostname.
    """
    database_url = str(
        database_url if database_url is not None else os.environ.get("DATABASE_URL", "")
    ).strip()
    mysql_ssl_ca = str(
        mysql_ssl_ca if mysql_ssl_ca is not None else os.environ.get("MYSQL_SSL_CA", "")
    ).strip()

    options = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    is_mysql = database_url.lower().startswith("mysql")
    is_aiven_mysql = is_mysql and "aivencloud.com" in database_url.lower()

    if is_aiven_mysql and not mysql_ssl_ca:
        raise RuntimeError(
            "Aiven MySQL 연결에는 MYSQL_SSL_CA 인증서 경로가 필요합니다."
        )

    if mysql_ssl_ca:
        if not is_mysql:
            raise RuntimeError(
                "MYSQL_SSL_CA는 MySQL DATABASE_URL과 함께 사용해야 합니다."
            )

        ca_path = Path(mysql_ssl_ca).expanduser()
        if not ca_path.is_absolute():
            ca_path = Path(__file__).resolve().parent / ca_path
        ca_path = ca_path.resolve()

        if not ca_path.is_file():
            raise RuntimeError(f"MySQL CA 인증서 파일을 찾을 수 없습니다: {ca_path}")

        options["connect_args"] = {
            "ssl_ca": str(ca_path),
            "ssl_verify_cert": True,
            "ssl_verify_identity": True,
        }

    return options


def validate_toss_test_config(config):
    """토스페이먼츠 설정이 테스트 환경을 벗어나지 않도록 검증한다."""
    payment_mode = str(config.get("TOSS_PAYMENT_MODE", "test")).strip().lower()
    if payment_mode != "test":
        raise RuntimeError(
            "TripPalette에서는 토스페이먼츠 테스트 결제만 사용할 수 있습니다. "
            "TOSS_PAYMENT_MODE를 test로 설정해주세요."
        )

    client_key = str(config.get("TOSS_CLIENT_KEY") or "").strip()
    secret_key = str(config.get("TOSS_SECRET_KEY") or "").strip()

    if bool(client_key) != bool(secret_key):
        raise RuntimeError(
            "TOSS_CLIENT_KEY와 TOSS_SECRET_KEY는 함께 설정해야 합니다."
        )

    for setting_name, value in (
        ("TOSS_CLIENT_KEY", client_key),
        ("TOSS_SECRET_KEY", secret_key),
    ):
        if value and not value.startswith("test_"):
            raise RuntimeError(
                f"{setting_name}에는 test_로 시작하는 테스트 키만 사용할 수 "
                "있습니다. 라이브 결제 키는 허용되지 않습니다."
            )


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = build_database_engine_options(
        SQLALCHEMY_DATABASE_URI
    )
    TOSS_CLIENT_KEY = os.environ.get("TOSS_CLIENT_KEY", "")
    TOSS_SECRET_KEY = os.environ.get("TOSS_SECRET_KEY", "")
    TOSS_PAYMENT_MODE = os.environ.get("TOSS_PAYMENT_MODE", "test")
    TOSS_API_BASE_URL = "https://api.tosspayments.com"
    TOSS_API_TIMEOUT_SECONDS = 10
