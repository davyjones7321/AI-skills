import json
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import httpx
from jose import jwt

from registry.api.config import settings
from registry.api.database import get_db
from registry.api.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

def _get_token_map() -> dict:
    try:
        return json.loads(settings.api_tokens)
    except (json.JSONDecodeError, TypeError):
        return {}

def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> str:
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

    # Look up Bearer token in users table
    user = db.query(User).filter(User.token == token).first()
    if user:
        return user.username

    # Fallback to API_TOKENS env var
    token_map = _get_token_map()
    if token in token_map:
        return token_map[token]

    raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.get("/login")
def login():
    """Redirects user to GitHub OAuth URL."""
    url = f"https://github.com/login/oauth/authorize?client_id={settings.GITHUB_CLIENT_ID}&scope=read:user&redirect_uri={settings.BASE_URL}/auth/callback"
    return RedirectResponse(url)


@router.get("/callback")
async def callback(code: str, db: Session = Depends(get_db)):
    """Exchanges code for access token and creates/updates User."""
    async with httpx.AsyncClient() as client:
        # Swap code for access token
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code
            },
            headers={"Accept": "application/json"}
        )
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")

        # Get user info
        user_res = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json"
            }
        )
        user_data = user_res.json()
        github_id = user_data.get("id")
        username = user_data.get("login")
        avatar_url = user_data.get("avatar_url")
        
        if not github_id or not username:
            raise HTTPException(status_code=400, detail="Failed to parse user data from GitHub")

        # Create or update user
        user = db.query(User).filter(User.github_id == github_id).first()
        
        # Generate JWT
        jwt_payload = {"sub": username, "github_id": github_id}
        new_token = jwt.encode(jwt_payload, settings.JWT_SECRET_KEY, algorithm="HS256")
        
        if user:
            user.username = username
            user.avatar_url = avatar_url
            user.token = new_token
        else:
            user = User(
                github_id=github_id,
                username=username,
                avatar_url=avatar_url,
                token=new_token
            )
            db.add(user)
            
        db.commit()

        return {"token": new_token, "username": username, "avatar_url": avatar_url}


@router.get("/me")
def get_me(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Returns the currently authenticated user's details."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization format. Use: Bearer <token>")

    token = parts[1].strip()

    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Token not found in database")

    return {
        "username": user.username,
        "github_id": str(user.github_id),
        "avatar_url": user.avatar_url
    }
