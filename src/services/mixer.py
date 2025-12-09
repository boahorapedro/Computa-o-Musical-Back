# src/services/mixer.py
import numpy as np
import soundfile as sf


class AudioMixer:
    """Final mixing of stems."""

    @staticmethod
    def mix(
        stems: dict[str, np.ndarray],
        volumes: dict[str, float] = None
    ) -> np.ndarray:
        """
        Combine multiple stems into single audio.

        Args:
            stems: Dict of stem name to audio array
            volumes: Optional volume levels for each stem

        Returns:
            Mixed audio array
        """
        volumes = volumes or {}

        # Find maximum length
        max_len = max(len(s) for s in stems.values())

        # Mix
        output = np.zeros(max_len)
        for name, audio in stems.items():
            vol = volumes.get(name, 1.0)
            padded = np.pad(audio, (0, max_len - len(audio)))
            output += padded * vol

        return output

    @staticmethod
    def normalize(audio: np.ndarray) -> np.ndarray:
        """Normalize audio to avoid clipping."""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio

    @staticmethod
    def export(audio: np.ndarray, path: str, sample_rate: int = 44100):
        """Export audio to file."""
        sf.write(path, audio, sample_rate)
