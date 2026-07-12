"""Utility for cleansing, stripping markdown tags, and repairing/parsing AI response payloads."""

import json
import re
from typing import Any, Dict, List, Union
from src.ai.exceptions import ParseError

class ResponseParser:
    """Enterprise parser specialized in structural validation and JSON payload cleansing."""

    @staticmethod
    def strip_markdown(text: str) -> str:
        """Cleans and extracts core text out of markdown code fence wraps.

        Args:
            text: The raw generated output text from the AI model.

        Returns:
            The raw text stripped of ```json, ```xml or basic ``` blocks.
        """
        if not text:
            return ""
        
        # Remove markdown wrappers
        text = text.strip()
        if text.startswith("```"):
            # Matches ```<optional-lang-specifier>\n<content>``` or variations
            match = re.search(r"^```[a-zA-Z0-9]*\n?(.*?)\n?```$", text, re.DOTALL)
            if match:
                text = match.group(1).strip()
            else:
                # If no exact match, just strip leading/trailing ticks
                text = re.sub(r"^```[a-zA-Z0-9]*", "", text).strip()
                text = re.sub(r"```$", "", text).strip()
        return text

    @classmethod
    def parse_json(cls, text: str) -> Union[Dict[str, Any], List[Any]]:
        """Parses a response into a structured dictionary/list, with markdown cleaning.

        Args:
            text: Raw AI output content.

        Returns:
            Parsed JSON object (dict or list).

        Raises:
            ParseError: If JSON deserialization fails completely.
        """
        cleaned_text = cls.strip_markdown(text)
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as primary_err:
            # Fallback 1: Try to locate any embedded JSON array or object using regex
            match = re.search(r"({.*}|\[.*\])", cleaned_text, re.DOTALL)
            if match:
                extracted_json = match.group(1).strip()
                try:
                    return json.loads(extracted_json)
                except json.JSONDecodeError:
                    pass
            
            # Fallback 2: Common JSON formatting repairs (e.g., removing trailing commas)
            repaired_text = cls._attempt_json_repair(cleaned_text)
            try:
                return json.loads(repaired_text)
            except json.JSONDecodeError as repair_err:
                raise ParseError(
                    f"Failed to parse text as valid JSON. Raw string: {text[:200]}...",
                ) from repair_err

    @staticmethod
    def _attempt_json_repair(text: str) -> str:
        """Applies basic heuristic cleaning to correct minor JSON syntax errors."""
        # 1. Remove trailing commas before closing braces/brackets
        text = re.sub(r",\s*([}\]])", r"\1", text)
        # 2. Fix unescaped control characters
        text = re.sub(r"[\x00-\x1f]", "", text)
        return text
