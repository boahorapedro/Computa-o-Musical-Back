# src/db/repositories.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import AsyncSessionLocal
from src.db.models import Project, StyleSound, Mix
from typing import List, Optional, Dict, Any
import uuid


class ProjectRepository:
    """Repository for Project CRUD operations."""

    def __init__(self):
        self.session_factory = AsyncSessionLocal

    async def create(self, data: Dict[str, Any]) -> Project:
        """Create new project."""
        async with self.session_factory() as session:
            project = Project(**data)
            session.add(project)
            await session.commit()
            await session.refresh(project)
            return project

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Project).where(Project.id == uuid.UUID(project_id))
            )
            return result.scalar_one_or_none()

    async def get_all(self) -> List[Project]:
        """Get all projects."""
        async with self.session_factory() as session:
            result = await session.execute(select(Project))
            return result.scalars().all()

    async def update(self, project_id: str, data: Dict[str, Any]) -> Optional[Project]:
        """Update project."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Project).where(Project.id == uuid.UUID(project_id))
            )
            project = result.scalar_one_or_none()
            if project:
                for key, value in data.items():
                    setattr(project, key, value)
                await session.commit()
                await session.refresh(project)
            return project

    async def update_status(self, project_id: str, status: str) -> Optional[Project]:
        """Update project status."""
        return await self.update(project_id, {"status": status})

    async def update_stems(self, project_id: str, stem_paths: Dict[str, str]) -> Optional[Project]:
        """Update stem paths."""
        data = {
            "vocals_path": stem_paths.get("vocals"),
            "drums_path": stem_paths.get("drums"),
            "bass_path": stem_paths.get("bass"),
            "other_path": stem_paths.get("other"),
        }
        return await self.update(project_id, data)

    async def delete(self, project_id: str):
        """Delete project."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Project).where(Project.id == uuid.UUID(project_id))
            )
            project = result.scalar_one_or_none()
            if project:
                await session.delete(project)
                await session.commit()


class StyleSoundRepository:
    """Repository for StyleSound CRUD operations."""

    def __init__(self):
        self.session_factory = AsyncSessionLocal

    async def create(self, data: Dict[str, Any]) -> StyleSound:
        """Create new style sound."""
        async with self.session_factory() as session:
            sound = StyleSound(**data)
            session.add(sound)
            await session.commit()
            await session.refresh(sound)
            return sound

    async def get_by_id(self, sound_id: str) -> Optional[StyleSound]:
        """Get style sound by ID."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(StyleSound).where(StyleSound.id == uuid.UUID(sound_id))
            )
            return result.scalar_one_or_none()

    async def get_by_hash(self, file_hash: str) -> Optional[StyleSound]:
        """Get style sound by file hash."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(StyleSound).where(StyleSound.file_hash == file_hash)
            )
            return result.scalar_one_or_none()

    async def get_all(self) -> List[StyleSound]:
        """Get all style sounds."""
        async with self.session_factory() as session:
            result = await session.execute(select(StyleSound))
            return result.scalars().all()

    async def update(self, sound_id: str, data: Dict[str, Any]) -> Optional[StyleSound]:
        """Update style sound."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(StyleSound).where(StyleSound.id == uuid.UUID(sound_id))
            )
            sound = result.scalar_one_or_none()
            if sound:
                for key, value in data.items():
                    setattr(sound, key, value)
                await session.commit()
                await session.refresh(sound)
            return sound

    async def delete(self, sound_id: str):
        """Delete style sound."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(StyleSound).where(StyleSound.id == uuid.UUID(sound_id))
            )
            sound = result.scalar_one_or_none()
            if sound:
                await session.delete(sound)
                await session.commit()


class MixRepository:
    """Repository for Mix CRUD operations."""

    def __init__(self):
        self.session_factory = AsyncSessionLocal

    async def create(self, data: Dict[str, Any]) -> Mix:
        """Create new mix."""
        async with self.session_factory() as session:
            mix = Mix(**data)
            session.add(mix)
            await session.commit()
            await session.refresh(mix)
            return mix

    async def get_by_id(self, mix_id: str) -> Optional[Mix]:
        """Get mix by ID."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Mix).where(Mix.id == uuid.UUID(mix_id))
            )
            return result.scalar_one_or_none()

    async def update(self, mix_id: str, data: Dict[str, Any]) -> Optional[Mix]:
        """Update mix."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Mix).where(Mix.id == uuid.UUID(mix_id))
            )
            mix = result.scalar_one_or_none()
            if mix:
                for key, value in data.items():
                    setattr(mix, key, value)
                await session.commit()
                await session.refresh(mix)
            return mix

    async def update_status(self, mix_id: str, status: str) -> Optional[Mix]:
        """Update mix status."""
        return await self.update(mix_id, {"status": status})

    async def delete(self, mix_id: str):
        """Delete mix."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(Mix).where(Mix.id == uuid.UUID(mix_id))
            )
            mix = result.scalar_one_or_none()
            if mix:
                await session.delete(mix)
                await session.commit()
