import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from urllib.parse import urlencode
from uuid import uuid4

import httpx
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from registry.api.config import settings
from registry.api.database import get_db
from registry.api.models import User
from registry.api.schemas import AuthUserResponse, LogoutResponse

router = APIRouter(prefix="/auth", tags=["auth"])
oauth_states: Dict[str, Dict[str, object]] = {}
OAUTH_STATE_TTL_SECONDS = 300


def _cleanup_expired_oauth_states() -> None:
    now = time.time()
    expired = [
        state
        for state, payload in oauth_states.items()
        if now - float(payload["created_at"]) > OAUTH_STATE_TTL_SECONDS
    ]
    for state in expired:
        oauth_states.pop(state, None)


def _build_jwt(user: User) -> str:
    issued_at = datetime.now(timezone.utc)
    expires_at = issued_at + timedelta(hours=settings.jwt_expire_hours)
    payload = {
        "sub": str(user.github_id),
        "username": user.username,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def _parse_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format. Use: Bearer <token>")
    return parts[1].strip()


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    token = _parse_bearer_token(authorization)
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    github_id = payload.get("sub")
    if github_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        github_id_int = int(github_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc

    user = db.query(User).filter(User.github_id == github_id_int).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


async def _fetch_github_primary_email(client: httpx.AsyncClient, access_token: str) -> Optional[str]:
    email_res = await client.get(
        "https://api.github.com/user/emails",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
    )
    email_res.raise_for_status()
    email_data = email_res.json()
    if not isinstance(email_data, list):
        return None

    for entry in email_data:
        if (
            isinstance(entry, dict)
            and entry.get("primary") is True
            and entry.get("verified") is True
            and isinstance(entry.get("email"), str)
        ):
            return entry["email"]
    return None


def _serialize_user(user: User) -> AuthUserResponse:
    return AuthUserResponse(
        github_id=str(user.github_id),
        username=user.username,
        email=user.email,
        avatar_url=user.avatar_url,
    )


@router.get("/github")
@router.get("/login")
def login_with_github(
    cli: bool = Query(False),
    next: Optional[str] = Query(None),
):
    """Redirect the user to GitHub OAuth with a short-lived anti-CSRF state."""
    _cleanup_expired_oauth_states()
    state = str(uuid4())
    oauth_states[state] = {
        "created_at": time.time(),
        "cli": cli,
        "next": next,
    }
    params = urlencode(
        {
            "client_id": settings.GITHUB_CLIENT_ID,
            "scope": "read:user user:email",
            "redirect_uri": f"{settings.registry_url.rstrip('/')}/auth/github/callback",
            "state": state,
        }
    )
    return RedirectResponse(f"https://github.com/login/oauth/authorize?{params}")


@router.get("/github/callback")
@router.get("/callback")
async def callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    """Exchange the GitHub code for a JWT and return the appropriate client response."""
    _cleanup_expired_oauth_states()
    state_payload = oauth_states.pop(state, None)
    if not state_payload:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    created_at = float(state_payload["created_at"])
    if time.time() - created_at > OAUTH_STATE_TTL_SECONDS:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")

    cli = bool(state_payload.get("cli"))
    next_path = state_payload.get("next")

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": f"{settings.registry_url.rstrip('/')}/auth/github/callback",
            },
            headers={"Accept": "application/json"},
        )
        token_res.raise_for_status()
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")

        user_res = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
        )
        user_res.raise_for_status()
        user_data = user_res.json()
        github_id = user_data.get("id")
        username = user_data.get("login")
        avatar_url = user_data.get("avatar_url")
        email = await _fetch_github_primary_email(client, access_token)

        if not github_id or not username:
            raise HTTPException(status_code=400, detail="Failed to parse user data from GitHub")

        user = db.query(User).filter(User.github_id == github_id).first()
        if user:
            user.username = username
            user.avatar_url = avatar_url
            user.email = email
            user.last_login = datetime.now(timezone.utc).isoformat()
        else:
            user = User(
                github_id=github_id,
                username=username,
                avatar_url=avatar_url,
                email=email,
                last_login=datetime.now(timezone.utc).isoformat(),
            )
            db.add(user)

        db.commit()
        db.refresh(user)
        jwt_token = _build_jwt(user)

        if cli:
            next_url = str(next_path) if isinstance(next_path, str) else None
            if next_url and (next_url.startswith("http://127.0.0.1:") or next_url.startswith("http://localhost:")):
                separator = "&" if "?" in next_url else "?"
                return RedirectResponse(f"{next_url}{separator}{urlencode({'token': jwt_token})}")
            return {"token": jwt_token}

        callback_url = f"{settings.frontend_url.rstrip('/')}/auth/callback?{urlencode({'token': jwt_token})}"
        if isinstance(next_path, str) and next_path:
            callback_url = f"{callback_url}&{urlencode({'next': next_path})}"
        return RedirectResponse(callback_url)


@router.get("/me", response_model=AuthUserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return _serialize_user(current_user)


@router.post("/logout", response_model=LogoutResponse)
def logout():
    return LogoutResponse(ok=True)
