"""Formatting and configuration of safety filters for Gemini/AI API compliance."""

from typing import Dict, List, Any, Optional
from src.ai.constants import (
    SAFETY_HARM_CATEGORIES,
    SAFETY_THRESHOLD_BLOCK_NONE,
    SAFETY_THRESHOLD_BLOCK_MEDIUM_AND_ABOVE,
)

class SafetyConfig:
    """Configures and formats standard safety parameters for model queries."""

    @staticmethod
    def get_default_settings() -> List[Dict[str, str]]:
        """Returns standard enterprise safety blocks (BLOCK_MEDIUM_AND_ABOVE)."""
        return [
            {
                "category": cat,
                "threshold": SAFETY_THRESHOLD_BLOCK_MEDIUM_AND_ABOVE
            }
            for cat in SAFETY_HARM_CATEGORIES
        ]

    @staticmethod
    def get_relaxed_settings() -> List[Dict[str, str]]:
        """Returns completely relaxed safety boundaries for creative marketing copy (BLOCK_NONE)."""
        return [
            {
                "category": cat,
                "threshold": SAFETY_THRESHOLD_BLOCK_NONE
            }
            for cat in SAFETY_HARM_CATEGORIES
        ]

    @classmethod
    def format_for_api(cls, user_settings: Optional[Dict[str, str]] = None) -> List[Dict[str, str]]:
        """Compiles user safety dictionary into the final Google API compliant format.

        Args:
            user_settings: Dict mapping HARM_CATEGORY -> THRESHOLD. If omitted, uses default settings.
        """
        if not user_settings:
            return cls.get_default_settings()

        formatted_settings = []
        for category, threshold in user_settings.items():
            # Standardize category strings (e.g. support passing "harassment" or full "HARM_CATEGORY_HARASSMENT")
            standard_cat = category.upper()
            if not standard_cat.startswith("HARM_CATEGORY_"):
                standard_cat = f"HARM_CATEGORY_{standard_cat}"

            # Standardize threshold strings
            standard_threshold = threshold.upper()
            if standard_threshold in {"NONE", "BLOCK_NONE"}:
                standard_threshold = SAFETY_THRESHOLD_BLOCK_NONE
            elif standard_threshold in {"LOW", "BLOCK_LOW_AND_ABOVE"}:
                standard_threshold = "BLOCK_LOW_AND_ABOVE"
            elif standard_threshold in {"MEDIUM", "BLOCK_MEDIUM_AND_ABOVE"}:
                standard_threshold = SAFETY_THRESHOLD_BLOCK_MEDIUM_AND_ABOVE
            elif standard_threshold in {"HIGH", "BLOCK_LOW_AND_ABOVE", "BLOCK_NONE"}:
                pass  # Use exact standard values

            formatted_settings.append({
                "category": standard_cat,
                "threshold": standard_threshold
            })

        return formatted_settings
