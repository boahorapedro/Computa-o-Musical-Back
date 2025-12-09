# src/api/v1/projects/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectResponse(BaseModel):
    id: str
    name: str
    status: str
    base_file_path: Optional[str]
    base_file_hash: Optional[str]
    duration_seconds: Optional[float]
    sample_rate: Optional[int]
    vocals_path: Optional[str]
    drums_path: Optional[str]
    bass_path: Optional[str]
    other_path: Optional[str]
    analysis_cache_key: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


class ProjectListResponse(BaseModel):
    projects: list[ProjectResponse]


class StemStatus(BaseModel):
    vocals: bool
    drums: bool
    bass: bool
    other: bool


class ProjectStatusResponse(BaseModel):
    project_id: str
    status: str
    stems: Optional[StemStatus] = None


class DeleteResponse(BaseModel):
    message: str
