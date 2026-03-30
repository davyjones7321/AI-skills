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
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib import error, request
from urllib.parse import parse_qs, urlencode, urlparse

DEFAULT_REGISTRY_URL = os.environ.get("AISKILLS_REGISTRY_URL", "https://ai-skills-sdk.onrender.com")
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

    def complete_oauth_login(self, timeout_seconds: int = 300) -> tuple[str, str]:
        """Complete browser-based GitHub OAuth without manual token paste."""
        token_holder: dict[str, str | None] = {"token": None}
        done = threading.Event()

        class OAuthCallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                params = parse_qs(parsed.query)
                token = params.get("token", [None])[0]

                if parsed.path != "/callback" or not token:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Authentication failed. You can close this window.")
                    done.set()
                    return

                token_holder["token"] = token
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"<html><body><h1>Login complete.</h1><p>You can close this window.</p></body></html>")
                done.set()

            def log_message(self, format, *args):  # noqa: A003
                return

        # Start server on fixed port 9876 as requested
        try:
            server = HTTPServer(("localhost", 9876), OAuthCallbackHandler)
        except OSError as e:
            raise RuntimeError(f"Could not start local server on port 9876: {e}")
        
        callback_url = "http://localhost:9876/callback"
        login_url = f"{self.registry_url.rstrip('/')}/auth/github?{urlencode({'cli': 'true', 'next': callback_url})}"

        server_thread = threading.Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        print("Opening browser to sign in with GitHub...")
        webbrowser.open(login_url)

        completed = done.wait(timeout_seconds)
        server.server_close()

        if not completed or not token_holder["token"]:
            raise RuntimeError("Timed out waiting for the OAuth callback")

        token = token_holder["token"]
        if token is None:
            raise RuntimeError("OAuth callback did not include a token")

        req = request.Request(
            f"{self.registry_url.rstrip('/')}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        try:
            with request.urlopen(req, timeout=10) as resp:
                user_data = json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            raise RuntimeError(f"Failed to verify token: {exc.code}") from exc

        username = user_data.get("username")
        if not isinstance(username, str) or not username:
            raise RuntimeError("Authenticated user response did not include a username")

        self.save_token(token, username)
        return token, username

    def clear_token(self):
        """Remove stored auth credentials."""
        self._data["auth_token"] = None
        self._data["username"] = None
        self._save()

    def is_authenticated(self) -> bool:
        """Check if a token is stored."""
        return bool(self._data.get("auth_token"))
