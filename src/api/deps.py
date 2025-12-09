# src/api/deps.py
from src.db.database import get_db
from src.config.settings import get_settings

__all__ = ["get_db", "get_settings"]
