# src/api/v1/router.py
from fastapi import APIRouter

from src.api.v1.upload.router import router as upload_router
from src.api.v1.projects.router import router as projects_router
from src.api.v1.library.router import router as library_router
from src.api.v1.mix.router import router as mix_router

api_router = APIRouter()

api_router.include_router(upload_router)
api_router.include_router(projects_router)
api_router.include_router(library_router)
api_router.include_router(mix_router)
