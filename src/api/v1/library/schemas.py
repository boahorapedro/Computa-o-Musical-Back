# src/api/v1/library/schemas.py
from pydantic import BaseModel
from typing import Optional


class StyleSoundResponse(BaseModel):
    id: str
    name: str
    file_path: str
    file_hash: Optional[str]
    duration_seconds: Optional[float]
    grain_count: Optional[int]
    grain_cache_key: Optional[str]
    created_at: Optional[str]


class LibraryListResponse(BaseModel):
    sounds: list[StyleSoundResponse]


class DeleteResponse(BaseModel):
    message: str
