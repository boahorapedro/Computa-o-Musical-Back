# src/services/granular_synth.py
import numpy as np
import random
from typing import List, Optional
from src.services.grain_builder import Grain
from src.services.onset_detector import OnsetDetector
from src.services.pitch_analyzer import PitchAnalyzer


class GranularSynthesizer:
    """
    Granular synthesis - extracted from processar_faixa() function in notebook.
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        grain_duration_ms: int = 120,
        use_pitch_mapping: bool = True,
        use_envelope: bool = True
    ):
        self.sample_rate = sample_rate
        self.grain_duration_ms = grain_duration_ms
        self.use_pitch_mapping = use_pitch_mapping
        self.use_envelope = use_envelope

        self.decay_samples = int(sample_rate * (grain_duration_ms / 1000))
        self.envelope = np.linspace(1.0, 0.0, num=self.decay_samples)

        self.onset_detector = OnsetDetector(sample_rate)
        self.pitch_analyzer = PitchAnalyzer(sample_rate)

    def synthesize(
        self,
        base_stem: np.ndarray,
        grain_library: List[Grain],
        instrument_type: str = "melodic"  # "melodic" or "drums"
    ) -> np.ndarray:
        """
        Synthesize track using grains.

        Args:
            base_stem: Original stem audio
            grain_library: List of available grains
            instrument_type: Type of instrument (affects pitch mapping)

        Returns:
            Synthesized audio array
        """
        if not grain_library:
            return np.zeros(len(base_stem))

        # Detect onsets in base stem
        onset_data = self.onset_detector.detect(base_stem)
        onset_samples = onset_data["samples"]

        # Output buffer
        output = np.zeros(len(base_stem))

        for onset in onset_samples:
            # Extract segment for analysis
            end = min(onset + self.decay_samples, len(base_stem))
            segment = base_stem[onset:end]

            if len(segment) == 0:
                continue

            peak_vol = float(np.max(np.abs(segment)))

            # Determine target pitch
            target_pitch = 0.0
            if self.use_pitch_mapping and instrument_type != "drums":
                target_pitch = self.pitch_analyzer.analyze_segment(segment)

            # Select grain
            grain = self._select_grain(grain_library, target_pitch)
            if grain is None:
                continue

            # Process and insert grain
            processed = self._process_grain(grain.audio, peak_vol)

            # Additive mixing
            end_pos = min(onset + len(processed), len(output))
            actual_len = end_pos - onset
            output[onset:end_pos] += processed[:actual_len]

        return output

    def _select_grain(
        self,
        library: List[Grain],
        target_pitch: float
    ) -> Optional[Grain]:
        """Select most suitable grain."""
        if target_pitch == 0:
            return random.choice(library)

        # Find grain with closest pitch
        return min(library, key=lambda g: abs(g.pitch - target_pitch))

    def _process_grain(self, grain_audio: np.ndarray, amplitude: float) -> np.ndarray:
        """Process grain applying envelope and amplitude."""
        # Adjust size
        if len(grain_audio) < self.decay_samples:
            repeats = int(np.ceil(self.decay_samples / len(grain_audio)))
            grain_ready = np.tile(grain_audio, repeats)[:self.decay_samples]
        else:
            grain_ready = grain_audio[:self.decay_samples]

        # Apply envelope and amplitude
        if self.use_envelope:
            return (grain_ready * self.envelope) * amplitude

        return grain_ready * amplitude
