# src/services/onset_detector.py
import numpy as np
import librosa


class OnsetDetector:
    """Detection of rhythmic events using librosa."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def detect(self, audio: np.ndarray, delta: float = 0.06) -> dict:
        """
        Detect onsets in audio.

        Args:
            audio: Audio array
            delta: Threshold for peak picking

        Returns:
            Dict with onset frames and samples
        """
        onset_frames = librosa.onset.onset_detect(
            y=audio,
            sr=self.sample_rate,
            units='frames',
            wait=1,
            pre_avg=1,
            post_avg=1,
            post_max=1,
            delta=delta
        )

        onset_samples = librosa.frames_to_samples(onset_frames)

        return {
            "frames": onset_frames.tolist(),
            "samples": onset_samples.tolist(),
            "count": len(onset_frames)
        }
