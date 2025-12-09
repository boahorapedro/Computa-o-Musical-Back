# src/services/pitch_analyzer.py
import numpy as np
import librosa


class PitchAnalyzer:
    """Pitch analysis using pYIN."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.fmin = librosa.note_to_hz('C1')
        self.fmax = librosa.note_to_hz('C7')

    def analyze_segment(self, audio: np.ndarray) -> float:
        """
        Analyze pitch of an audio segment.

        Args:
            audio: Audio segment

        Returns:
            Average pitch in Hz (0 if silent)
        """
        if len(audio) < 1024:
            return 0.0

        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                audio,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=self.sample_rate,
                frame_length=min(len(audio), 2048),
                fill_na=0
            )

            non_zero = f0[f0 > 0]
            if len(non_zero) > 0:
                return float(np.mean(non_zero))
        except Exception:
            pass

        return 0.0

    def analyze_at_onsets(
        self,
        audio: np.ndarray,
        onset_samples: list[int],
        window_ms: int = 120
    ) -> list[dict]:
        """
        Analyze pitch at each onset position.

        Args:
            audio: Full audio array
            onset_samples: List of onset positions in samples
            window_ms: Analysis window in milliseconds

        Returns:
            List of dicts with onset analysis
        """
        window_samples = int(self.sample_rate * (window_ms / 1000))
        results = []

        for onset in onset_samples:
            end = min(onset + window_samples, len(audio))
            segment = audio[onset:end]

            if len(segment) == 0:
                continue

            pitch = self.analyze_segment(segment)
            peak = float(np.max(np.abs(segment)))

            results.append({
                "start": onset,
                "pitch": pitch,
                "peak": peak
            })

        return results
