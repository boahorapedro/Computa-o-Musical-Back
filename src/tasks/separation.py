# src/tasks/separation.py - VERSÃO CORRIGIDA
from src.tasks.celery_app import celery_app
from src.services.stem_separator import StemSeparator
from src.storage.minio_client import MinIOClient
from src.db.repositories import ProjectRepository
import tempfile
import os
import asyncio


async def _separate_stems_async(project_id: str):
    """Async helper to separate stems."""
    storage = MinIOClient()
    repo = ProjectRepository()
    separator = StemSeparator()

    # Update status
    await repo.update_status(project_id, "separating")

    try:
        # Fetch project
        project = await repo.get_by_id(project_id)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Download base file
            local_input = os.path.join(tmpdir, "input.wav")
            storage.download(project.base_file_path, local_input)

            # Separate stems
            stems = separator.separate(local_input, tmpdir)

            # Upload stems
            stem_paths = {}
            for stem_name, local_path in stems.items():
                remote_path = f"stems/{project_id}/{stem_name}.wav"
                storage.upload(local_path, remote_path)
                stem_paths[stem_name] = remote_path

            # Update project
            await repo.update_stems(project_id, stem_paths)
            await repo.update_status(project_id, "ready")

        return {"status": "success", "project_id": project_id}

    except Exception as e:
        await repo.update_status(project_id, "error")
        raise e


@celery_app.task(bind=True, name="tasks.separate_stems")
def separate_stems(self, project_id: str):
    """Task to separate stems from a music file."""
    # Run async code in a single event loop
    return asyncio.run(_separate_stems_async(project_id))
