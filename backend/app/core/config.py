from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database — defaults to SQLite for local dev (no Docker needed)
    DATABASE_URL: str = "sqlite+aiosqlite:///./smartstudy.db"
    REDIS_URL: str = "redis://localhost:6379"
    USE_MEMORY_CACHE: bool = True  # Use in-memory dict instead of Redis

    # OpenAI
    OPENAI_API_KEY: str = ""

    # JWT
    JWT_SECRET_KEY: str = "change-this-to-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_PDF_SIZE_MB: int = 10
    MAX_TEXT_FILE_SIZE_MB: int = 5

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
