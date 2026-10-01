from functools import wraps
from urllib.parse import urlsplit

from flask import g, redirect, request, session, url_for

from app import db
from app.models import User


def load_logged_in_user():
    """세션의 사용자 ID를 현재 요청의 ``g.user``로 불러온다."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
        return

    g.user = db.session.get(User, user_id)
    if g.user is None:
        session.pop("user_id", None)


def get_safe_next_url(target):
    """서비스 내부의 절대 경로인 경우에만 이동 경로를 반환한다."""
    if not target or not isinstance(target, str):
        return None

    target = target.strip()
    if not target or "\\" in target or any(ord(char) < 32 for char in target):
        return None
    if not target.startswith("/") or target.startswith("//"):
        return None

    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return None

    return target


def login_required(view):
    """로그인하지 않은 사용자를 로그인 화면으로 보내는 Decorator."""

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            next_url = request.full_path.rstrip("?")
            return redirect(url_for("auth.login", next=next_url))
        return view(*args, **kwargs)

    return wrapped_view
