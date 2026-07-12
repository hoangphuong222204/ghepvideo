"""Token count calculator with tiktoken optimization and safe character-based approximation fallback."""

import logging

logger = logging.getLogger("AIMSPro.AI")

# Try to import tiktoken for precise encoding-based token estimation
_has_tiktoken = False
_encoding = None

try:
    import tiktoken
    # Use standard cl100k_base (widely utilized by recent models)
    _encoding = tiktoken.get_encoding("cl100k_base")
    _has_tiktoken = True
    logger.info("Precise cl100k_base token counter initialized via tiktoken.")
except ImportError:
    logger.debug("tiktoken is not installed. Falling back to fast character-based approximation (1 token ~= 4 characters).")


class Tokenizer:
    """Enterprise Token counter supporting tiktoken precision or character-approximation fallback."""

    @staticmethod
    def count_tokens(text: str) -> int:
        """Estimates the total token count of a given text block.

        Args:
            text: Input string content.

        Returns:
            The exact or approximated token count (always at least 0).
        """
        if not text:
            return 0

        if _has_tiktoken and _encoding is not None:
            try:
                return len(_encoding.encode(text))
            except Exception as e:
                logger.warning(f"Error encoding text with tiktoken, falling back to approximation: {e}")

        # English-centric character fallback: on average 4 characters represent 1 token
        # Always return at least 1 token if the string is non-empty
        return max(1, int(len(text) / 4))
