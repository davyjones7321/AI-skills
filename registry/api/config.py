from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./registry.db"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "super-secret-key-change-this-in-prod"

    # Registry
    registry_url: str = "http://localhost:8000"

    # GitHub OAuth (for future full implementation)
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    BASE_URL: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_EXPIRE_HOURS: int = 168  # 7 days

    # MVP Auth — simple token-based auth
    # Format: JSON dict mapping tokens to usernames
    # Example: '{"token123": "ai-skills-team", "mytoken": "jane-doe"}'
    api_tokens: str = '{"dev-token-aiskills": "ai-skills-team"}'

    class Config:
        env_file = ".env"


settings = Settings()
