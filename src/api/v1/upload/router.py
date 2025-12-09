# src/api/v1/upload/router.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.storage.minio_client import MinIOClient
from src.db.repositories import ProjectRepository, StyleSoundRepository
from src.tasks.separation import separate_stems
from src.tasks.analysis import build_grain_library
from src.api.v1.upload.schemas import UploadBaseTrackResponse, UploadStyleSoundsResponse, UploadedSound
import hashlib
import uuid

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/base-track", response_model=UploadBaseTrackResponse)
async def upload_base_track(
    file: UploadFile = File(...),
    project_name: str = None
):
    """Upload base music for stem separation."""

    # Validate format
    if not file.filename.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):
        raise HTTPException(400, "Unsupported format")

    content = await file.read()

    # Check size (100MB max)
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 100MB)")

    # Hash for deduplication
    file_hash = hashlib.sha256(content).hexdigest()

    # Generate IDs
    project_id = str(uuid.uuid4())
    storage_path = f"uploads/base/{project_id}/{file.filename}"

    # Upload to MinIO
    storage = MinIOClient()
    storage.upload_bytes(content, storage_path)

    # Create project in database
    repo = ProjectRepository()
    project = await repo.create({
        "id": project_id,
        "name": project_name or file.filename,
        "base_file_path": storage_path,
        "base_file_hash": file_hash,
        "status": "created"
    })

    # Dispatch separation task
    separate_stems.delay(project_id)

    return UploadBaseTrackResponse(
        project_id=project_id,
        status="queued",
        message="Stem separation started"
    )


@router.post("/style-sound", response_model=UploadStyleSoundsResponse)
async def upload_style_sound(
    files: list[UploadFile] = File(...)
):
    """Upload style sounds for library."""

    storage = MinIOClient()
    repo = StyleSoundRepository()

    uploaded = []

    for file in files:
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()

        # Check duplicate
        existing = await repo.get_by_hash(file_hash)
        if existing:
            uploaded.append(UploadedSound(
                id=str(existing.id),
                name=existing.name,
                duplicate=True
            ))
            continue

        style_id = str(uuid.uuid4())
        storage_path = f"uploads/styles/{style_id}/{file.filename}"

        storage.upload_bytes(content, storage_path)

        style = await repo.create({
            "id": style_id,
            "name": file.filename,
            "file_path": storage_path,
            "file_hash": file_hash
        })

        # Dispatch grain library building
        build_grain_library.delay(style_id)

        uploaded.append(UploadedSound(
            id=style_id,
            name=file.filename,
            duplicate=False
        ))

    return UploadStyleSoundsResponse(uploaded=uploaded)
