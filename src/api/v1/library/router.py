# src/api/v1/library/router.py
from fastapi import APIRouter, HTTPException
from src.db.repositories import StyleSoundRepository
from src.storage.minio_client import MinIOClient
from src.cache.redis_client import RedisCache
from src.api.v1.library.schemas import (
    StyleSoundResponse,
    LibraryListResponse,
    DeleteResponse
)

router = APIRouter(prefix="/library", tags=["library"])


@router.get("", response_model=LibraryListResponse)
async def list_sounds():
    """List style sounds library."""
    repo = StyleSoundRepository()
    sounds = await repo.get_all()
    return LibraryListResponse(
        sounds=[StyleSoundResponse(**s.to_dict()) for s in sounds]
    )


@router.get("/{sound_id}", response_model=StyleSoundResponse)
async def get_sound(sound_id: str):
    """Style sound details."""
    repo = StyleSoundRepository()
    sound = await repo.get_by_id(sound_id)

    if not sound:
        raise HTTPException(404, "Sound not found")

    return StyleSoundResponse(**sound.to_dict())


@router.delete("/{sound_id}", response_model=DeleteResponse)
async def delete_sound(sound_id: str):
    """Remove sound from library."""
    repo = StyleSoundRepository()
    storage = MinIOClient()
    cache = RedisCache()

    sound = await repo.get_by_id(sound_id)
    if not sound:
        raise HTTPException(404, "Sound not found")

    # Remove file
    storage.delete(sound.file_path)

    # Remove grain cache
    if sound.grain_cache_key:
        cache.delete(sound.grain_cache_key)

    # Remove from database
    await repo.delete(sound_id)

    return DeleteResponse(message="Sound removed")
