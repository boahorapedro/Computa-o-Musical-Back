# src/config/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API
    APP_NAME: str = "Audio Mixer API"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/audiomixer"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "audio-storage"
    MINIO_SECURE: bool = False

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Audio Processing
    DEFAULT_SAMPLE_RATE: int = 44100
    MAX_UPLOAD_SIZE_MB: int = 100
    GRAIN_DURATION_MS: int = 120
    USE_PITCH_MAPPING: bool = True
    USE_ENVELOPE: bool = True

    # Demucs
    DEMUCS_MODEL: str = "htdemucs_ft"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
