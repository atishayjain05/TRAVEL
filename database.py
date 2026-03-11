"""
FoodScout AI — Database Connection & Session Management
SQLAlchemy async-compatible setup with connection pooling.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
from loguru import logger
from backend.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency — yields a DB session and closes it after request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables by executing schema.sql."""
    import os

    schema_path = os.path.join(
        os.path.dirname(__file__), "..", "database", "schema.sql"
    )
    try:
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        with engine.connect() as conn:
            # Execute each statement separately
            for statement in schema_sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    conn.execute(text(stmt))
            conn.commit()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize DB schema: {e}")
        raise


def check_db_connection() -> bool:
    """Verify the database is reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB connection check failed: {e}")
        return False
