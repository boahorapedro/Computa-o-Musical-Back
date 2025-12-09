# src/api/v1/upload/schemas.py
from pydantic import BaseModel
from typing import Optional


class UploadBaseTrackResponse(BaseModel):
    project_id: str
    status: str
    message: str


class UploadedSound(BaseModel):
    id: str
    name: str
    duplicate: bool


class UploadStyleSoundsResponse(BaseModel):
    uploaded: list[UploadedSound]
