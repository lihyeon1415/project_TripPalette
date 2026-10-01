from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 기존 확장 기능 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Migrate가 SQLAlchemy 모델을 인식하도록 등록
    from app import models  # noqa: F401

    # Blueprint import
    from app.views.accommodation import accommodation_bp
    from app.views.auth import auth_bp
    from app.views.destination import destination_bp
    from app.views.main import main_bp
    from app.views.mypage import mypage_bp
    from app.views.recommendation import recommendation_bp
    from app.views.reservation import reservation_bp

    # Blueprint 등록
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(destination_bp, url_prefix="/destinations")
    app.register_blueprint(accommodation_bp, url_prefix="/accommodations")
    app.register_blueprint(recommendation_bp, url_prefix="/recommend")
    app.register_blueprint(reservation_bp, url_prefix="/reservations")
    app.register_blueprint(mypage_bp, url_prefix="/mypage")

    from app.destination_media import DESTINATION_MEDIA

    @app.context_processor
    def inject_destination_media():
        return {"destination_media": DESTINATION_MEDIA}

    @app.cli.command("purge-withdrawn-users")
    def purge_withdrawn_users():
        """탈퇴 유예기간이 지난 회원 계정을 영구 삭제한다."""
        from app.account_deletion import purge_expired_accounts

        deleted_count = purge_expired_accounts()
        print(f"Purged {deleted_count} withdrawn user(s).")

    return app
