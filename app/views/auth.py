from email_validator import EmailNotValidError, validate_email
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.account_deletion import format_deletion_date, purge_expired_accounts
from app.auth_helpers import get_safe_next_url, load_logged_in_user, login_required
from app.models import User


auth_bp = Blueprint("auth", __name__)
MIN_PASSWORD_LENGTH = 8


@auth_bp.before_app_request
def load_current_user():
    """모든 요청에서 Template과 View가 현재 사용자를 참조하게 한다."""
    purge_expired_accounts()
    load_logged_in_user()


def _normalize_email(value):
    return (value or "").strip().lower()


def _is_valid_email(value):
    try:
        validate_email(value, check_deliverability=False)
    except EmailNotValidError:
        return False
    return True


def _public_form_data(*field_names):
    """비밀번호를 제외한 입력값만 Template에 다시 전달한다."""
    return {name: (request.form.get(name) or "").strip() for name in field_names}


@auth_bp.route("/login", methods=("GET", "POST"))
def login():
    requested_next = request.form.get("next") or request.args.get("next")
    next_url = get_safe_next_url(requested_next)
    form_data = _public_form_data("email") if request.method == "POST" else {}

    if request.method == "POST":
        email = _normalize_email(request.form.get("email"))
        password = request.form.get("password") or ""
        user = db.session.scalar(db.select(User).where(User.email == email))

        if user is None or not check_password_hash(user.password_hash, password):
            flash("이메일 또는 비밀번호가 올바르지 않습니다.", "error")
        else:
            session.clear()
            session["user_id"] = user.id
            if user.scheduled_deletion_at is not None:
                deletion_date = format_deletion_date(user.scheduled_deletion_at)
                flash(
                    f"이 계정은 {deletion_date}에 탈퇴될 예정입니다. "
                    "마이페이지에서 탈퇴를 철회할 수 있습니다.",
                    "warning",
                )
            return redirect(next_url or url_for("main.index"))

    return render_template(
        "auth/login.html",
        next_url=next_url,
        form_data=form_data,
    )


@auth_bp.route("/signup", methods=("GET", "POST"))
def signup():
    form_data = (
        _public_form_data("email", "name", "phone")
        if request.method == "POST"
        else {}
    )

    if request.method == "POST":
        email = _normalize_email(request.form.get("email"))
        password = request.form.get("password") or ""
        password_confirm = (
            request.form.get("password_confirm")
            or request.form.get("password-confirm")
            or ""
        )
        name = form_data["name"]
        phone = form_data["phone"]

        error = None
        if not all((email, password, password_confirm, name, phone)):
            error = "모든 항목을 입력해 주세요."
        elif not _is_valid_email(email):
            error = "올바른 이메일 형식을 입력해 주세요."
        elif len(password) < MIN_PASSWORD_LENGTH:
            error = f"비밀번호는 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다."
        elif password != password_confirm:
            error = "비밀번호 확인이 일치하지 않습니다."
        elif db.session.scalar(db.select(User.id).where(User.email == email)):
            error = "이미 가입된 이메일입니다."

        if error is None:
            user = User(
                email=email,
                password_hash=generate_password_hash(password),
                name=name,
                phone=phone,
            )
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                error = "이미 가입된 이메일입니다."
            else:
                flash("회원가입이 완료되었습니다. 로그인해 주세요.", "success")
                return redirect(url_for("auth.login"))

        flash(error, "error")

    return render_template("auth/signup.html", form_data=form_data)


@auth_bp.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@auth_bp.route("/find-email", methods=("GET", "POST"))
def find_email():
    form_data = (
        _public_form_data("name", "phone") if request.method == "POST" else {}
    )
    found_email = None

    if request.method == "POST":
        name = form_data["name"]
        phone = form_data["phone"]
        if not name or not phone:
            flash("이름과 전화번호를 모두 입력해 주세요.", "error")
        else:
            user = db.session.scalar(
                db.select(User).where(User.name == name, User.phone == phone)
            )
            if user is None:
                flash("일치하는 회원 정보를 찾을 수 없습니다.", "error")
            else:
                found_email = user.email

    return render_template(
        "auth/find_email.html",
        found_email=found_email,
        form_data=form_data,
    )


@auth_bp.route("/reset-password", methods=("GET", "POST"))
def reset_password():
    form_data = (
        _public_form_data("email", "name", "phone")
        if request.method == "POST"
        else {}
    )

    if request.method == "POST":
        email = _normalize_email(request.form.get("email"))
        name = form_data["name"]
        phone = form_data["phone"]
        password = (
            request.form.get("password")
            or request.form.get("new_password")
            or ""
        )
        password_confirm = (
            request.form.get("password_confirm")
            or request.form.get("password-confirm")
            or request.form.get("new_password_confirm")
            or ""
        )

        error = None
        if not all((email, name, phone, password, password_confirm)):
            error = "모든 항목을 입력해 주세요."
        elif len(password) < MIN_PASSWORD_LENGTH:
            error = f"비밀번호는 {MIN_PASSWORD_LENGTH}자 이상이어야 합니다."
        elif password != password_confirm:
            error = "비밀번호 확인이 일치하지 않습니다."
        else:
            user = db.session.scalar(
                db.select(User).where(
                    User.email == email,
                    User.name == name,
                    User.phone == phone,
                )
            )
            if user is None:
                error = "일치하는 회원 정보를 찾을 수 없습니다."

        if error is None:
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            flash(
                "비밀번호가 변경되었습니다. 새 비밀번호로 로그인해 주세요.",
                "success",
            )
            return redirect(url_for("auth.login"))

        flash(error, "error")

    return render_template("auth/reset_password.html", form_data=form_data)
