from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import logging
from app.config import settings
from app.database.models import Base

logger = logging.getLogger(__name__)

# Create engine with connection pooling disabled for serverless
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=NullPool,  # Recommended for serverless/Neon
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with tables"""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")

async def check_db_connection():
    """Check if database connection works"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection OK")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
