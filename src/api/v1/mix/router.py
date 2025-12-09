# src/api/v1/mix/router.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from src.db.repositories import MixRepository, ProjectRepository
from src.tasks.synthesis import create_mix
from src.storage.minio_client import MinIOClient
from src.api.v1.mix.schemas import (
    CreateMixRequest,
    CreateMixResponse,
    MixStatusResponse
)
import uuid

router = APIRouter(prefix="/mix", tags=["mix"])


@router.post("", response_model=CreateMixResponse)
async def create_mix_endpoint(request: CreateMixRequest):
    """Create new mix."""

    project_repo = ProjectRepository()
    mix_repo = MixRepository()

    # Check project
    project = await project_repo.get_by_id(request.project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    if project.status != "ready":
        raise HTTPException(400, f"Project not ready (status: {project.status})")

    # Create mix
    mix_id = str(uuid.uuid4())
    mix = await mix_repo.create({
        "id": mix_id,
        "project_id": request.project_id,
        "config": request.config.dict(),
        "settings": request.settings.dict(),
        "status": "queued"
    })

    # Dispatch task
    create_mix.delay(mix_id)

    return CreateMixResponse(
        mix_id=mix_id,
        status="queued",
        message="Mix started"
    )


@router.get("/{mix_id}", response_model=MixStatusResponse)
async def get_mix_status(mix_id: str):
    """Mix status."""

    repo = MixRepository()
    mix = await repo.get_by_id(mix_id)

    if not mix:
        raise HTTPException(404, "Mix not found")

    response = MixStatusResponse(
        mix_id=mix_id,
        status=mix.status,
        config=mix.config,
        created_at=mix.created_at.isoformat()
    )

    if mix.status == "complete" and mix.output_path:
        storage = MinIOClient()
        response.download_url = storage.get_presigned_url(mix.output_path)

    return response


@router.get("/{mix_id}/download")
async def download_mix(mix_id: str):
    """Redirect to download URL."""

    repo = MixRepository()
    mix = await repo.get_by_id(mix_id)

    if not mix:
        raise HTTPException(404, "Mix not found")

    if mix.status != "complete":
        raise HTTPException(400, "Mix not yet complete")

    storage = MinIOClient()
    url = storage.get_presigned_url(mix.output_path, expires=3600)

    return RedirectResponse(url=url)
