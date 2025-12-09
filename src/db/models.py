# src/db/models.py
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from src.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="created")  # created, separating, ready, error

    # Base file
    base_file_path = Column(String(500))
    base_file_hash = Column(String(64))
    duration_seconds = Column(Float)
    sample_rate = Column(Integer, default=44100)

    # Stems (filled after separation)
    vocals_path = Column(String(500))
    drums_path = Column(String(500))
    bass_path = Column(String(500))
    other_path = Column(String(500))

    # Cached analysis
    analysis_cache_key = Column(String(100))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    mixes = relationship("Mix", back_populates="project")

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "status": self.status,
            "base_file_path": self.base_file_path,
            "base_file_hash": self.base_file_hash,
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "vocals_path": self.vocals_path,
            "drums_path": self.drums_path,
            "bass_path": self.bass_path,
            "other_path": self.other_path,
            "analysis_cache_key": self.analysis_cache_key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StyleSound(Base):
    __tablename__ = "style_sounds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64))

    duration_seconds = Column(Float)
    grain_count = Column(Integer)
    grain_cache_key = Column(String(100))  # Key in Redis

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "duration_seconds": self.duration_seconds,
            "grain_count": self.grain_count,
            "grain_cache_key": self.grain_cache_key,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Mix(Base):
    __tablename__ = "mixes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    status = Column(String(50), default="queued")  # queued, processing, complete, error

    # Configuration
    config = Column(JSON)  # {drums: {style_id, volume}, bass: {...}, ...}
    settings = Column(JSON)  # {grain_duration_ms, use_pitch_mapping, ...}

    # Result
    output_path = Column(String(500))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    project = relationship("Project", back_populates="mixes")

    def to_dict(self):
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "status": self.status,
            "config": self.config,
            "settings": self.settings,
            "output_path": self.output_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
