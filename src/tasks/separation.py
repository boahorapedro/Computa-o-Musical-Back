# src/tasks/separation.py
from src.tasks.celery_app import celery_app
from src.services.stem_separator import StemSeparator
from src.storage.minio_client import MinIOClient
from src.db.repositories import ProjectRepository
import tempfile
import os
import asyncio


@celery_app.task(bind=True, name="tasks.separate_stems")
def separate_stems(self, project_id: str):
    """Task to separate stems from a music file."""

    storage = MinIOClient()
    repo = ProjectRepository()
    separator = StemSeparator()

    # Update status
    asyncio.run(repo.update_status(project_id, "separating"))

    try:
        # Fetch project
        project = asyncio.run(repo.get_by_id(project_id))

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
            asyncio.run(repo.update_stems(project_id, stem_paths))
            asyncio.run(repo.update_status(project_id, "ready"))

        return {"status": "success", "project_id": project_id}

    except Exception as e:
        asyncio.run(repo.update_status(project_id, "error"))
        raise e
