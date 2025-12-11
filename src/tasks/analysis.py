# src/tasks/analysis.py - VERSÃO CORRIGIDA
from src.tasks.celery_app import celery_app
from src.services.onset_detector import OnsetDetector
from src.services.pitch_analyzer import PitchAnalyzer
from src.services.grain_builder import GrainBuilder
from src.storage.minio_client import MinIOClient
from src.cache.redis_client import RedisCache
from src.db.repositories import ProjectRepository, StyleSoundRepository
import librosa
import tempfile
import asyncio


async def _analyze_stems_async(project_id: str):
    """Async helper to analyze stems."""
    storage = MinIOClient()
    cache = RedisCache()
    repo = ProjectRepository()

    project = await repo.get_by_id(project_id)

    onset_detector = OnsetDetector()
    pitch_analyzer = PitchAnalyzer()

    analysis_results = {}

    for stem_name in ["drums", "bass", "other"]:
        stem_path = getattr(project, f"{stem_name}_path")
        if not stem_path:
            continue

        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            storage.download(stem_path, tmp.name)
            audio, sr = librosa.load(tmp.name, sr=44100)

        # Detect onsets
        onsets = onset_detector.detect(audio)

        # Analyze pitch at each onset
        pitch_data = pitch_analyzer.analyze_at_onsets(
            audio,
            onsets["samples"]
        )

        analysis_results[stem_name] = {
            "onsets": onsets,
            "pitch_data": pitch_data
        }

    # Cache result
    cache_key = f"analysis:{project_id}"
    cache.set_json(cache_key, analysis_results)

    await repo.update(project_id, {"analysis_cache_key": cache_key})

    return {"status": "success", "cache_key": cache_key}


@celery_app.task(name="tasks.analyze_stems")
def analyze_stems(project_id: str):
    """Analyze onsets and pitch of each stem."""
    # Run async code in a single event loop
    return asyncio.run(_analyze_stems_async(project_id))


async def _build_grain_library_async(style_sound_id: str):
    """Async helper to build grain library."""
    storage = MinIOClient()
    cache = RedisCache()
    repo = StyleSoundRepository()

    style = await repo.get_by_id(style_sound_id)

    builder = GrainBuilder()

    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        storage.download(style.file_path, tmp.name)
        audio, sr = librosa.load(tmp.name, sr=44100)

    # Build grain library
    grains = builder.build_library(audio)

    # Calculate duration
    duration = len(audio) / sr

    # Cache grains
    cache_key = f"grains:{style_sound_id}"
    cache.set_grains(cache_key, grains)

    # Update database
    await repo.update(style_sound_id, {
        "grain_cache_key": cache_key,
        "grain_count": len(grains),
        "duration_seconds": duration
    })

    return {
        "status": "success",
        "cache_key": cache_key,
        "grain_count": len(grains)
    }


@celery_app.task(name="tasks.build_grain_library")
def build_grain_library(style_sound_id: str):
    """Build grain library from style sound file."""
    # Run async code in a single event loop
    return asyncio.run(_build_grain_library_async(style_sound_id))
