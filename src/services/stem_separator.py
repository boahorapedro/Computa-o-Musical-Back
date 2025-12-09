# src/services/stem_separator.py
import subprocess
import os
from pathlib import Path
from src.config.settings import get_settings

settings = get_settings()


class StemSeparator:
    """Wrapper for stem separation using Demucs."""

    def __init__(self, model: str = None):
        self.model = model or settings.DEMUCS_MODEL

    def separate(self, input_path: str, output_dir: str) -> dict[str, str]:
        """
        Separate audio file into 4 stems.

        Args:
            input_path: Path to input audio file
            output_dir: Directory for output stems

        Returns:
            Dict with stem paths: {vocals, drums, bass, other}
        """
        # Execute Demucs
        cmd = [
            "python", "-m", "demucs",
            "-n", self.model,
            "-o", output_dir,
            input_path
        ]

        subprocess.run(cmd, check=True, capture_output=True)

        # Build output paths
        input_name = Path(input_path).stem
        stems_dir = Path(output_dir) / self.model / input_name

        return {
            "vocals": str(stems_dir / "vocals.wav"),
            "drums": str(stems_dir / "drums.wav"),
            "bass": str(stems_dir / "bass.wav"),
            "other": str(stems_dir / "other.wav"),
        }
