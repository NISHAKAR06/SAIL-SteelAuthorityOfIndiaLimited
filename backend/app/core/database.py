from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# SQLite-specific options
connect_args = {}
if settings.SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
    connect_args = {"check_same_thread": False}
    
# Create SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args=connect_args,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for ORM models
Base = declarative_base()

# Function to create all tables
def init_db():
    try:
        # Import all models to ensure they're registered with Base
        # This must be imported here to avoid circular imports
        # Import in dependency order to avoid relationship issues
        from app.models import cost_parameters, route_transport
        from app.models import rake
        from app.models import order, inventory, optimization

        # Check if tables exist before creating them
        inspector = inspect(engine)

        existing_tables = inspector.get_table_names()
        logger.info(f"Existing tables: {existing_tables}")

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
