import os, secrets, urllib.parse, requests
from flask import Blueprint, redirect, request, session, url_for, jsonify

bp = Blueprint("auth", __name__)

AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
TOKEN_URL = "https://kauth.kakao.com/oauth/token"
ME_URL = "https://kapi.kakao.com/v2/user/me"

def _require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(f"Missing environment variable: {key}")
    return val

@bp.get("/kakao")
def oauth_authorize():
    client_id = _require_env("KAKAO_CLIENT_ID")
    redirect_uri = _require_env("KAKAO_REDIRECT_URI")
    scope = os.getenv("KAKAO_SCOPE", "account_email profile_nickname")

    state = secrets.token_urlsafe(24)
    session["oauth_state"] = state

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": scope,
    }
    return redirect(f"{AUTH_URL}?{urllib.parse.urlencode(params)}")

@bp.get("/kakao/callback")
def oauth_callback():
    state_sent = request.args.get("state")
    state_saved = session.get("oauth_state")
    if not state_sent or state_sent != state_saved:
        return jsonify({"error": "Invalid state"}), 400

    code = request.args.get("code")
    client_id = _require_env("KAKAO_CLIENT_ID")
    redirect_uri = _require_env("KAKAO_REDIRECT_URI")
    client_secret = os.getenv("KAKAO_CLIENT_SECRET")

    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    if client_secret:
        data["client_secret"] = client_secret

    token_resp = requests.post(TOKEN_URL, data=data, timeout=10)
    tokens = token_resp.json()
    access_token = tokens.get("access_token")

    me_resp = requests.get(
        ME_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    me = me_resp.json()

    kakao_id = me.get("id")
    kakao_account = me.get("kakao_account", {}) or {}
    profile = kakao_account.get("profile", {}) or {}

    user = {
        "provider": "kakao",
        "provider_id": kakao_id,
        "nickname": profile.get("nickname"),
        "email": kakao_account.get("email"),
    }

    session.pop("oauth_state", None)
    session["user"] = user
    return redirect(url_for("auth.login_success"))

@bp.get("/login/success")
def login_success():
    return jsonify({"message": "kakao login success", "user": session.get("user")})

@bp.post("/logout")
def logout():
    session.clear()
    return jsonify({"message": "logged out"})




