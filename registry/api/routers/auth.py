"""
MVP Auth — Simple token-based authentication.

Tokens are stored in the config as a JSON dict mapping tokens to usernames.
For production, replace with GitHub OAuth.

Usage:
    Authorization: Bearer <token>
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional

from registry.api.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_token_map() -> dict:
    """Parse token map from config."""
    try:
        return json.loads(settings.api_tokens)
    except (json.JSONDecodeError, TypeError):
        return {}


def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract and validate the auth token from the Authorization header.
    Returns the username associated with the token.
    Raises 401 if token is missing or invalid.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    # Expect "Bearer <token>"
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format. Use: Bearer <token>")

    token = parts[1].strip()
    token_map = _get_token_map()

    if token not in token_map:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return token_map[token]


@router.get("/me")
def get_me(username: str = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return {"username": username}


@router.get("/login")
def login():
    """Placeholder for future GitHub OAuth login flow."""
    return {
        "message": "For MVP, use token-based auth. Set Authorization: Bearer <token> header.",
        "hint": "Configure tokens via API_TOKENS env var or .env file."
    }
