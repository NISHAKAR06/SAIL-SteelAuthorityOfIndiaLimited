import os
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
import pathlib

# Get the root directory
ROOT_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "SAIL DSS"

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

    # Database settings
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_GvKS6HItr2Oa@ep-orange-base-adjy5moj-pooler.c-2.us-east-1.aws.neon.tech/ALL_DATABASE?sslmode=require&channel_binding=require")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "postgres")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "all_database")
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: str = os.getenv("DATABASE_PORT", "5432")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # ML settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "app/ml/models/")

    def __init__(self, **values: Any):
        super().__init__(**values)

        # Use DATABASE_URL for production (Neon PostgreSQL)
        if self.DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
        else:
            # Use SQLite as fallback for development
            sqlite_db_path = os.path.join(ROOT_DIR, "database.db")
            self.SQLALCHEMY_DATABASE_URI = f"sqlite:///{sqlite_db_path}"

settings = Settings()
