"""Platform policy checking and sensitive claim remediation layer (e.g., TikTok policy constraints)."""

import re
from typing import Dict, List, Tuple
from src.script_engine.constants import SENSITIVE_WORDS_MAP


class PolicyChecker:
    """Detects claims violating TikTok/social guidelines and performs safe rewrites."""

    @classmethod
    def analyze_text(cls, text: str) -> Tuple[bool, List[str], str, float]:
        """Analyzes a text segment for sensitive words or claims.

        Returns:
            Tuple containing:
            - is_violating (bool): True if sensitive words are detected
            - violated_terms (List[str]): List of terms triggered
            - sanitized_text (str): Softer, platform-compliant rewrite of the text
            - score (float): Compliance score from 0.0 to 100.0
        """
        if not text:
            return False, [], "", 100.0

        violated_terms = []
        sanitized_text = text
        score = 100.0

        # Scan and substitute
        for sensitive, safe_sub in SENSITIVE_WORDS_MAP.items():
            # Only add \b if boundary char is alphanumeric to avoid matching failures on non-word chars like '%'
            start_boundary = r"\b" if re.match(r"^\w", sensitive) else ""
            end_boundary = r"\b" if re.search(r"\w$", sensitive) else ""
            pattern = re.compile(f"{start_boundary}{re.escape(sensitive)}{end_boundary}", re.IGNORECASE)
            matches = pattern.findall(sanitized_text)
            if matches:
                violated_terms.append(sensitive)
                # Deduct 25 points per unique violation type, down to 0
                score = max(0.0, score - 25.0)
                
                # Perform the rewrite keeping appropriate case
                def replace_case(match: re.Match) -> str:
                    matched_str = match.group(0)
                    if matched_str.isupper():
                        return safe_sub.upper()
                    if matched_str[0].isupper():
                        return safe_sub.capitalize()
                    return safe_sub

                sanitized_text = pattern.sub(replace_case, sanitized_text)

        is_violating = len(violated_terms) > 0
        return is_violating, violated_terms, sanitized_text, score

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Helper to return only the policy-sanitized version of a text string."""
        _, _, sanitized, _ = cls.analyze_text(text)
        return sanitized
