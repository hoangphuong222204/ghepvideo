"""Speech duration estimation and word count validation engine."""

import re
from typing import Tuple
from src.script_engine.constants import VIETNAMESE_WPM


class DurationEstimator:
    """Estimates audio duration of spoken text and validates word boundaries."""

    @staticmethod
    def count_words(text: str) -> int:
        """Counts the number of words in a string, ignoring excessive formatting/whitespace."""
        if not text:
            return 0
        # For Vietnamese, words are typically space-separated syllables
        cleaned = re.sub(r"[^\w\s\d\-]", " ", text)
        words = cleaned.split()
        return len(words)

    @classmethod
    def estimate_duration(cls, text: str) -> float:
        """Estimates the spoken duration of a text snippet in seconds based on Vietnamese WPM."""
        word_count = cls.count_words(text)
        if word_count == 0:
            return 0.0
        # WPM / 60 gives words per second
        words_per_second = VIETNAMESE_WPM / 60.0
        return round(word_count / words_per_second, 2)

    @classmethod
    def validate_duration_fit(
        cls, word_count: int, target_duration_seconds: float, tolerance_pct: float = 20.0
    ) -> Tuple[bool, float, float]:
        """Validates if the word count is reasonable for the target duration.

        Args:
            word_count: Number of spoken words in the script.
            target_duration_seconds: Desired duration in seconds.
            tolerance_pct: Acceptable percentage deviation (default 20%).

        Returns:
            Tuple containing:
            - fits (bool): True if estimated duration falls within acceptable bounds
            - estimated_duration (float): Speech length in seconds
            - deviation_pct (float): Deviation percentage
        """
        words_per_second = VIETNAMESE_WPM / 60.0
        estimated = word_count / words_per_second
        
        if target_duration_seconds <= 0:
            return True, estimated, 0.0

        deviation = abs(estimated - target_duration_seconds)
        deviation_pct = (deviation / target_duration_seconds) * 100.0
        fits = deviation_pct <= tolerance_pct

        return fits, round(estimated, 2), round(deviation_pct, 2)
