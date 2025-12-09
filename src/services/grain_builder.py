# src/services/grain_builder.py
import numpy as np
import librosa
from dataclasses import dataclass
from typing import List
from src.services.pitch_analyzer import PitchAnalyzer


@dataclass
class Grain:
    audio: np.ndarray
    pitch: float
    rms: float


class GrainBuilder:
    """Build grain library from style audio file."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.pitch_analyzer = PitchAnalyzer(sample_rate)

    def build_library(self, audio: np.ndarray, top_db: int = 20) -> List[Grain]:
        """
        Slice audio by silence and analyze each grain.

        Args:
            audio: Input audio array
            top_db: Threshold for silence detection

        Returns:
            List of Grain objects
        """
        # Detect non-silent regions
        intervals = librosa.effects.split(audio, top_db=top_db)

        grains = []
        for start, end in intervals:
            grain_audio = audio[start:end]

            if len(grain_audio) < 512:  # Ignore very short grains
                continue

            # Pitch analysis
            pitch = self.pitch_analyzer.analyze_segment(grain_audio)

            # RMS for intensity
            rms = float(np.sqrt(np.mean(grain_audio ** 2)))

            grains.append(Grain(
                audio=grain_audio,
                pitch=pitch,
                rms=rms
            ))

        return grains
