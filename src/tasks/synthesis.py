# src/tasks/synthesis.py
from src.tasks.celery_app import celery_app
from src.services.granular_synth import GranularSynthesizer
from src.services.mixer import AudioMixer
from src.storage.minio_client import MinIOClient
from src.cache.redis_client import RedisCache
from src.db.repositories import ProjectRepository, MixRepository, StyleSoundRepository
from src.tasks.analysis import build_grain_library
import librosa
import tempfile
import os
import asyncio


@celery_app.task(name="tasks.create_mix")
def create_mix(mix_id: str):
    """Create complete mix."""

    storage = MinIOClient()
    cache = RedisCache()
    mix_repo = MixRepository()
    project_repo = ProjectRepository()
    style_repo = StyleSoundRepository()

    synth = GranularSynthesizer()
    mixer = AudioMixer()

    # Fetch data
    mix = asyncio.run(mix_repo.get_by_id(mix_id))
    project = asyncio.run(project_repo.get_by_id(mix.project_id))
    config = mix.config

    asyncio.run(mix_repo.update_status(mix_id, "processing"))

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            stems_output = {}

            # Load vocals (not processed)
            if config.get("vocals", {}).get("enabled", True):
                vocals_local = os.path.join(tmpdir, "vocals.wav")
                storage.download(project.vocals_path, vocals_local)
                vocals, _ = librosa.load(vocals_local, sr=44100)
                stems_output["vocals"] = vocals * config["vocals"].get("volume", 1.0)

            # Process each stem with granular synthesis
            for stem_name in ["drums", "bass", "other"]:
                stem_config = config.get(stem_name, {})

                if not stem_config.get("enabled", False):
                    continue

                style_id = stem_config.get("style_sound_id")
                if not style_id:
                    continue

                # Load base stem
                stem_path = getattr(project, f"{stem_name}_path")
                stem_local = os.path.join(tmpdir, f"{stem_name}.wav")
                storage.download(stem_path, stem_local)
                stem_audio, _ = librosa.load(stem_local, sr=44100)

                # Load grain library from cache
                style = asyncio.run(style_repo.get_by_id(style_id))
                grain_library = cache.get_grains(style.grain_cache_key)

                if not grain_library:
                    # Rebuild if not in cache
                    build_grain_library(style_id)
                    grain_library = cache.get_grains(style.grain_cache_key)

                # Synthesize
                instrument_type = "drums" if stem_name == "drums" else "melodic"
                synthesized = synth.synthesize(
                    stem_audio,
                    grain_library,
                    instrument_type=instrument_type
                )

                volume = stem_config.get("volume", 1.0)
                stems_output[stem_name] = synthesized * volume

            # Mix everything
            final_mix = mixer.mix(stems_output)
            final_mix = mixer.normalize(final_mix)

            # Export
            output_local = os.path.join(tmpdir, "mix_output.wav")
            mixer.export(final_mix, output_local)

            # Upload
            output_path = f"mixes/{mix_id}/output.wav"
            storage.upload(output_local, output_path)

            # Update
            asyncio.run(mix_repo.update(mix_id, {
                "status": "complete",
                "output_path": output_path
            }))

        return {"status": "success", "mix_id": mix_id, "output_path": output_path}

    except Exception as e:
        asyncio.run(mix_repo.update_status(mix_id, "error"))
        raise e
