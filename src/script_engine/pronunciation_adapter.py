"""Utility to adapt English words and tech terminology to phonetic Vietnamese pronunciation."""

import re
from src.script_engine.constants import ENGLISH_PRONUNCIATION_MAP


class PronunciationAdapter:
    """Adapts English terminology inside Vietnamese scripts to assist TTS engines and voiceovers."""

    @classmethod
    def adapt_text(cls, text: str) -> str:
        """Translates registered English words in the text to phonetic Vietnamese.

        E.g., "Review sản phẩm dưỡng da này cực hot trên TikTok"
        -> "ri-viu sản phẩm dưỡng da này cực hót trên tíc-tóc".
        """
        if not text:
            return ""

        adapted_text = text
        # Perform case-insensitive matching for each word
        for eng_word, phonetic in ENGLISH_PRONUNCIATION_MAP.items():
            # Use word boundaries to prevent matching fragments (e.g., "sales" matched inside a larger word)
            pattern = re.compile(rf"\b{re.escape(eng_word)}\b", re.IGNORECASE)
            
            def replace_match(match: re.Match) -> str:
                original = match.group(0)
                # Keep capitalization style if possible
                if original.isupper():
                    return phonetic.upper()
                if any(c.isupper() for c in original):
                    return phonetic.capitalize()
                return phonetic

            adapted_text = pattern.sub(replace_match, adapted_text)

        return adapted_text
