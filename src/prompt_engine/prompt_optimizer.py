"""Optimizer reducing prompt length (and token usage) while preserving core semantic instructions."""

import re
from typing import List
from src.prompt_engine.exceptions import OptimizerError
from src.prompt_engine.models import OptimizationResult


class PromptOptimizer:
    """Optimizes and compresses prompts to save tokens and improve execution latency."""

    FILLER_WORDS = [
        r"\bplease\b",
        r"\bcan you\b",
        r"\bcould you\b",
        r"\bthank you\b",
        r"\bi would like you to\b",
        r"\bkindly\b",
        r"\bi'd appreciate it if you could\b",
    ]

    @classmethod
    def optimize(
        cls,
        text: str,
        compress_whitespace: bool = True,
        remove_fillers: bool = False,
        uppercase_keywords: bool = False,
    ) -> OptimizationResult:
        """Applies sequence of token-saving algorithms to a target prompt string.

        Args:
            text: Raw prompt string.
            compress_whitespace: Collapses blank lines and redundant spaces.
            remove_fillers: Strips polite or redundant phrases (e.g. "please").
            uppercase_keywords: Capitalizes primary instruction markers (e.g., MUST, NEVER).

        Returns:
            OptimizationResult containing optimized prompt copy and statistics.
        """
        if not text:
            return OptimizationResult(
                original_text="",
                optimized_text="",
                original_characters=0,
                optimized_characters=0,
                compression_ratio=1.0,
                tokens_saved_estimate=0,
            )

        original_chars = len(text)
        optimized_text = text
        applied_rules: List[str] = []

        try:
            # 1. Strip polite/conversational filler phrases
            if remove_fillers:
                original_before_filler = len(optimized_text)
                for pattern in cls.FILLER_WORDS:
                    optimized_text = re.sub(pattern, "", optimized_text, flags=re.IGNORECASE)
                # Cleanup potential double spaces left behind by removal
                optimized_text = re.sub(r" +", " ", optimized_text)
                if len(optimized_text) < original_before_filler:
                    applied_rules.append("Filler Words Strip")

            # 2. Compress Whitespace
            if compress_whitespace:
                original_before_ws = len(optimized_text)
                # Trim spaces from start and end of every line
                lines = [line.strip() for line in optimized_text.splitlines()]
                # Filter out consecutive empty lines (allow maximum of 1 empty separator line)
                cleaned_lines = []
                last_was_empty = False
                for line in lines:
                    if not line:
                        if not last_was_empty:
                            cleaned_lines.append("")
                            last_was_empty = True
                    else:
                        cleaned_lines.append(line)
                        last_was_empty = False

                # Reassemble text
                optimized_text = "\n".join(cleaned_lines)
                # Also strip trailing spaces on line ends
                optimized_text = re.sub(r" +", " ", optimized_text)
                if len(optimized_text) < original_before_ws:
                    applied_rules.append("Whitespace Compression")

            # 3. Capitalize Action Instructions (MUST, NEVER, ONLY, NOT)
            if uppercase_keywords:
                keywords = ["must", "never", "only", "not", "always", "do not", "should not"]
                for kw in keywords:
                    # Replace only isolated lowercase occurrences with capitalized
                    pattern = rf"\b{kw}\b"
                    optimized_text = re.sub(
                        pattern, kw.upper(), optimized_text, flags=re.IGNORECASE
                    )
                applied_rules.append("Instruction Key Capitalization")

            optimized_chars = len(optimized_text)
            
            # Simple heuristic: 1 token is roughly 4 characters in English
            chars_saved = original_chars - optimized_chars
            tokens_saved = max(0, int(chars_saved / 4))

            compression_ratio = (
                (optimized_chars / original_chars) if original_chars > 0 else 1.0
            )

            return OptimizationResult(
                original_text=text,
                optimized_text=optimized_text,
                original_characters=original_chars,
                optimized_characters=optimized_chars,
                compression_ratio=round(compression_ratio, 2),
                tokens_saved_estimate=tokens_saved,
                optimizations_applied=applied_rules,
            )

        except Exception as e:
            raise OptimizerError(f"Failed to optimize prompt text: {e}") from e
