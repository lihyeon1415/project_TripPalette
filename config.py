import os

from dotenv import load_dotenv


load_dotenv()


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
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
    TOSS_CLIENT_KEY = os.environ.get("TOSS_CLIENT_KEY", "")
    TOSS_SECRET_KEY = os.environ.get("TOSS_SECRET_KEY", "")
    TOSS_PAYMENT_MODE = os.environ.get("TOSS_PAYMENT_MODE", "test")
    TOSS_API_BASE_URL = "https://api.tosspayments.com"
    TOSS_API_TIMEOUT_SECONDS = 10
