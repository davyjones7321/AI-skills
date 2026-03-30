from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from registry.api.config import settings

# TypeScript-style: const engine = createEngine(...)
# Check if using SQLite to add specific connect_args
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(
    settings.database_url, 
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def run_migrations() -> None:
    with engine.begin() as connection:
        try:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN email TEXT")
        except Exception:
            pass

        try:
            connection.exec_driver_sql("ALTER TABLE users ADD COLUMN last_login TEXT")
        except Exception:
            pass

        try:
            connection.exec_driver_sql("ALTER TABLE skills ADD COLUMN category TEXT")
        except Exception:
            pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
