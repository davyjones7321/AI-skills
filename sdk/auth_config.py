"""
Auth config management for the ai-skills CLI.

Manages ~/.aiskills/config.json which stores:
- registry_url: URL of the registry API
- auth_token: Bearer token for authenticated requests
- username: The authenticated username

Usage:
    from sdk.auth_config import AuthConfig
    config = AuthConfig()
    config.save_token("my-token", "my-username")
    token = config.get_token()
"""

import json
import os
from pathlib import Path

DEFAULT_REGISTRY_URL = os.environ.get("AISKILLS_REGISTRY_URL", "https://ai-skills-production-f4f0.up.railway.app")
CONFIG_DIR = Path.home() / ".aiskills"
CONFIG_FILE = CONFIG_DIR / "config.json"


class AuthConfig:
    """Manages the ~/.aiskills/config.json file."""

    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        """Load config from disk, or return defaults."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return self._defaults()
        return self._defaults()

    def _defaults(self) -> dict:
        return {
            "registry_url": DEFAULT_REGISTRY_URL,
            "auth_token": None,
            "username": None,
        }

    def _save(self):
        """Write config to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2)

    @property
    def registry_url(self) -> str:
        return self._data.get("registry_url", DEFAULT_REGISTRY_URL)

    @registry_url.setter
    def registry_url(self, url: str):
        self._data["registry_url"] = url.rstrip("/")
        self._save()

    def get_token(self) -> str | None:
        """Get the stored auth token, or None if not logged in."""
        return self._data.get("auth_token")

    def get_username(self) -> str | None:
        """Get the stored username."""
        return self._data.get("username")

    def save_token(self, token: str, username: str):
        """Save auth token and username."""
        self._data["auth_token"] = token
        self._data["username"] = username
        self._save()

    def clear_token(self):
        """Remove stored auth credentials."""
        self._data["auth_token"] = None
        self._data["username"] = None
        self._save()

    def is_authenticated(self) -> bool:
        """Check if a token is stored."""
        return bool(self._data.get("auth_token"))
