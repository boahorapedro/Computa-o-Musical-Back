#!/usr/bin/env python3
"""
Exemplo de cliente Python para a Audio Mixer API.

Este script demonstra o fluxo completo:
1. Upload de música base
2. Upload de sons de estilo
3. Aguardar separação de stems
4. Criar mixagem
5. Aguardar processamento
6. Download do resultado
"""
import requests
import time
from pathlib import Path


class AudioMixerClient:
    """Cliente para interagir com a Audio Mixer API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"

    def upload_base_track(self, file_path: str, project_name: str) -> dict:
        """Upload de música base."""
        print(f"📤 Uploading base track: {file_path}")

        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"project_name": project_name}

            response = requests.post(
                f"{self.api_url}/upload/base-track",
                files=files,
                data=data
            )
            response.raise_for_status()

        result = response.json()
        print(f"✅ Project created: {result['project_id']}")
        return result

    def get_project_status(self, project_id: str) -> dict:
        """Verificar status do projeto."""
        response = requests.get(f"{self.api_url}/projects/{project_id}/status")
        response.raise_for_status()
        return response.json()

    def wait_for_separation(self, project_id: str, timeout: int = 600) -> bool:
        """Aguardar separação de stems."""
        print(f"⏳ Waiting for stem separation...")

        start = time.time()
        while time.time() - start < timeout:
            status = self.get_project_status(project_id)

            if status["status"] == "ready":
                print(f"✅ Stems separated successfully!")
                return True
            elif status["status"] == "error":
                print(f"❌ Separation failed!")
                return False

            print(f"   Status: {status['status']} (elapsed: {int(time.time() - start)}s)")
            time.sleep(10)

        print(f"⏰ Timeout waiting for separation!")
        return False

    def upload_style_sounds(self, file_paths: list[str]) -> list[dict]:
        """Upload de sons de estilo."""
        print(f"📤 Uploading {len(file_paths)} style sounds...")

        files = [("files", open(path, "rb")) for path in file_paths]

        try:
            response = requests.post(
                f"{self.api_url}/upload/style-sound",
                files=files
            )
            response.raise_for_status()
        finally:
            for _, f in files:
                f.close()

        result = response.json()
        print(f"✅ Uploaded {len(result['uploaded'])} sounds")
        return result["uploaded"]

    def create_mix(self, project_id: str, config: dict, settings: dict = None) -> dict:
        """Criar mixagem."""
        print(f"🎛️  Creating mix...")

        payload = {
            "project_id": project_id,
            "config": config,
            "settings": settings or {
                "grain_duration_ms": 120,
                "use_pitch_mapping": True,
                "use_envelope": True
            }
        }

        response = requests.post(f"{self.api_url}/mix", json=payload)
        response.raise_for_status()

        result = response.json()
        print(f"✅ Mix created: {result['mix_id']}")
        return result

    def get_mix_status(self, mix_id: str) -> dict:
        """Verificar status da mixagem."""
        response = requests.get(f"{self.api_url}/mix/{mix_id}")
        response.raise_for_status()
        return response.json()

    def wait_for_mix(self, mix_id: str, timeout: int = 600) -> dict | None:
        """Aguardar processamento da mixagem."""
        print(f"⏳ Waiting for mix processing...")

        start = time.time()
        while time.time() - start < timeout:
            status = self.get_mix_status(mix_id)

            if status["status"] == "complete":
                print(f"✅ Mix completed!")
                return status
            elif status["status"] == "error":
                print(f"❌ Mix failed!")
                return None

            print(f"   Status: {status['status']} (elapsed: {int(time.time() - start)}s)")
            time.sleep(10)

        print(f"⏰ Timeout waiting for mix!")
        return None

    def download_mix(self, mix_id: str, output_path: str):
        """Download da mixagem."""
        print(f"📥 Downloading mix to: {output_path}")

        response = requests.get(
            f"{self.api_url}/mix/{mix_id}/download",
            allow_redirects=True
        )
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        print(f"✅ Downloaded: {output_path}")


def main():
    """Exemplo de uso completo."""
    client = AudioMixerClient()

    # 1. Upload música base
    project = client.upload_base_track(
        file_path="path/to/your/music.mp3",
        project_name="Meu Remix Trap"
    )
    project_id = project["project_id"]

    # 2. Aguardar separação
    if not client.wait_for_separation(project_id):
        return

    # 3. Upload sons de estilo
    sounds = client.upload_style_sounds([
        "path/to/trap_drums.wav",
        "path/to/funk_bass.wav"
    ])

    drums_id = sounds[0]["id"]
    bass_id = sounds[1]["id"]

    # 4. Criar mixagem
    mix = client.create_mix(
        project_id=project_id,
        config={
            "drums": {
                "enabled": True,
                "style_sound_id": drums_id,
                "volume": 1.0
            },
            "bass": {
                "enabled": True,
                "style_sound_id": bass_id,
                "volume": 0.8
            },
            "other": {
                "enabled": False
            },
            "vocals": {
                "enabled": True,
                "volume": 1.2
            }
        }
    )
    mix_id = mix["mix_id"]

    # 5. Aguardar processamento
    result = client.wait_for_mix(mix_id)
    if not result:
        return

    # 6. Download
    client.download_mix(mix_id, "output_remix.wav")

    print("\n🎉 Processo completo!")
    print(f"   Project: {project_id}")
    print(f"   Mix: {mix_id}")
    print(f"   Output: output_remix.wav")


if __name__ == "__main__":
    main()
