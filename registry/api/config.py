from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./registry.db"
    environment: str = "development"
    debug: bool = False
    secret_key: str

    base_url: str = "http://localhost:8000"

    # Registry
    registry_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    jwt_secret: str
    jwt_expire_hours: int = 720  # 30 days

    class Config:
        env_file = ".env"


settings = Settings()
