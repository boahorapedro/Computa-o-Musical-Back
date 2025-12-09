# src/api/v1/projects/router.py
from fastapi import APIRouter, HTTPException
from src.db.repositories import ProjectRepository
from src.storage.minio_client import MinIOClient
from src.api.v1.projects.schemas import (
    ProjectResponse,
    ProjectListResponse,
    ProjectStatusResponse,
    StemStatus,
    DeleteResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=ProjectListResponse)
async def list_projects():
    """List all projects."""
    repo = ProjectRepository()
    projects = await repo.get_all()
    return ProjectListResponse(
        projects=[ProjectResponse(**p.to_dict()) for p in projects]
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Project details."""
    repo = ProjectRepository()
    project = await repo.get_by_id(project_id)

    if not project:
        raise HTTPException(404, "Project not found")

    return ProjectResponse(**project.to_dict())


@router.get("/{project_id}/status", response_model=ProjectStatusResponse)
async def get_project_status(project_id: str):
    """Processing status of project."""
    repo = ProjectRepository()
    project = await repo.get_by_id(project_id)

    if not project:
        raise HTTPException(404, "Project not found")

    response = ProjectStatusResponse(
        project_id=project_id,
        status=project.status
    )

    if project.status == "ready":
        response.stems = StemStatus(
            vocals=project.vocals_path is not None,
            drums=project.drums_path is not None,
            bass=project.bass_path is not None,
            other=project.other_path is not None,
        )

    return response


@router.delete("/{project_id}", response_model=DeleteResponse)
async def delete_project(project_id: str):
    """Remove project and associated files."""
    repo = ProjectRepository()
    storage = MinIOClient()

    project = await repo.get_by_id(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    # Remove files
    storage.delete_prefix(f"uploads/base/{project_id}/")
    storage.delete_prefix(f"stems/{project_id}/")
    storage.delete_prefix(f"mixes/{project_id}/")

    # Remove from database
    await repo.delete(project_id)

    return DeleteResponse(message="Project removed")
