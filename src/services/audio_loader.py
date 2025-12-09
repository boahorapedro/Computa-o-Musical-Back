# src/services/audio_loader.py
import librosa
import soundfile as sf
import numpy as np
from typing import Tuple


class AudioLoader:
    """Service for loading and saving audio files."""

    @staticmethod
    def load(file_path: str, sample_rate: int = 44100) -> Tuple[np.ndarray, int]:
        """
        Load audio file.

        Args:
            file_path: Path to audio file
            sample_rate: Target sample rate

        Returns:
            Tuple of (audio array, sample rate)
        """
        audio, sr = librosa.load(file_path, sr=sample_rate, mono=True)
        return audio, sr

    @staticmethod
    def save(audio: np.ndarray, file_path: str, sample_rate: int = 44100):
        """
        Save audio to file.

        Args:
            audio: Audio array
            file_path: Output file path
            sample_rate: Sample rate
        """
        sf.write(file_path, audio, sample_rate)

    @staticmethod
    def get_duration(audio: np.ndarray, sample_rate: int) -> float:
        """
        Get audio duration in seconds.

        Args:
            audio: Audio array
            sample_rate: Sample rate

        Returns:
            Duration in seconds
        """
        return len(audio) / sample_rate
