# src/cache/redis_client.py
import redis
import pickle
import json
from src.config.settings import get_settings

settings = get_settings()


class RedisCache:
    """Redis client for caching."""

    def __init__(self):
        self.client = redis.from_url(settings.REDIS_URL)

    def set_json(self, key: str, value: dict, ttl: int = 86400):
        """Store JSON."""
        self.client.setex(key, ttl, json.dumps(value))

    def get_json(self, key: str) -> dict | None:
        """Retrieve JSON."""
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None

    def set_grains(self, key: str, grains: list, ttl: int = 86400):
        """Store grain library (pickle)."""
        self.client.setex(key, ttl, pickle.dumps(grains))

    def get_grains(self, key: str) -> list | None:
        """Retrieve grain library."""
        data = self.client.get(key)
        if data:
            return pickle.loads(data)
        return None

    def delete(self, key: str):
        """Delete key."""
        self.client.delete(key)

    def publish(self, channel: str, message: dict):
        """Publish message to channel."""
        self.client.publish(channel, json.dumps(message))
