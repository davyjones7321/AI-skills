from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./registry.db"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "super-secret-key-change-this-in-prod"
    
    # GitHub OAuth (mock values for now)
    github_client_id: str = "mock-client-id"
    github_client_secret: str = "mock-client-secret"

    class Config:
        env_file = ".env"

settings = Settings()
