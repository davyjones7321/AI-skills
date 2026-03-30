from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from registry.api.config import settings
from registry.api.categories import VALID_CATEGORIES

# TypeScript-style: const engine = createEngine(...)
# Check if using SQLite to add specific connect_args
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,        # tests connection before using it
    pool_recycle=300,          # recycle connections every 5 minutes
    pool_size=5,
    max_overflow=10,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def run_migrations() -> None:
    valid_category_list = ", ".join(f"'{category}'" for category in VALID_CATEGORIES)
    is_sqlite = "sqlite" in settings.database_url.lower()

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

        try:
            connection.exec_driver_sql(
                f"UPDATE skills SET category = NULL WHERE category IS NOT NULL AND category NOT IN ({valid_category_list})"
            )
        except Exception:
            pass

        if not is_sqlite:
            try:
                connection.exec_driver_sql(
                    f"""
                    ALTER TABLE skills
                    DROP CONSTRAINT IF EXISTS ck_skills_category_valid,
                    ADD CONSTRAINT ck_skills_category_valid
                    CHECK (category IS NULL OR category IN ({valid_category_list}))
                    """
                )
            except Exception:
                pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
