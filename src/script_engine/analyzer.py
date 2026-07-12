"""Supplementary analysis module checking text metrics, brand keywords, and engagement factors."""

import re
from typing import Dict, Any, List


class TextAnalyzer:
    """Helper class containing static methods for linguistic and engagement metric extraction on scripts."""

    @staticmethod
    def extract_metrics(text: str) -> Dict[str, Any]:
        """Calculates linguistic statistics like character counts, word counts, and sentence lengths.

        Args:
            text: Input plain text to analyze.

        Returns:
            Dictionary containing:
            - character_count (int)
            - word_count (int)
            - sentence_count (int)
            - avg_words_per_sentence (float)
        """
        if not text:
            return {
                "character_count": 0,
                "word_count": 0,
                "sentence_count": 0,
                "avg_words_per_sentence": 0.0,
            }

        char_cnt = len(text)
        
        # Word count
        words = re.sub(r"[^\w\s\d\-]", " ", text).split()
        word_cnt = len(words)

        # Sentence count (splitting on standard sentence ends)
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        sentence_cnt = len(sentences) or 1

        avg_words_per_sentence = round(word_cnt / sentence_cnt, 1)

        return {
            "character_count": char_cnt,
            "word_count": word_cnt,
            "sentence_count": sentence_cnt,
            "avg_words_per_sentence": avg_words_per_sentence,
        }

    @staticmethod
    def detect_keywords(text: str, keywords: List[str]) -> List[str]:
        """Finds which of the specified keywords exist in the text (case-insensitive)."""
        if not text or not keywords:
            return []

        found = []
        text_lower = text.lower()
        for kw in keywords:
            kw_cleaned = kw.strip().lower()
            if not kw_cleaned:
                continue
            # Regex with word boundaries
            pattern = re.compile(rf"\b{re.escape(kw_cleaned)}\b")
            if pattern.search(text_lower):
                found.append(kw)
        return found
