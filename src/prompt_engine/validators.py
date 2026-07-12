"""Validation layer for prompts, variables, provider limits, and safety filters."""

import re
from typing import Any, Dict, List, Optional, Set
from src.prompt_engine.exceptions import ValidationError
from src.prompt_engine.constants import SUPPORTED_PROVIDERS, PROVIDER_LIMITS, SUPPORTED_CATEGORIES
from src.prompt_engine.models import PromptTemplate, TemplateVariable


class PromptValidator:
    """Validator class ensuring payload inputs, template design, and variables meet criteria."""

    VARIABLE_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    PROMPT_INJECTION_KEYWORDS = [
        "ignore previous instructions",
        "system override",
        "you are now a",
        "forget everything",
        "bypass safeguards",
        "ignore the guidelines",
    ]

    @classmethod
    def validate_variable_name(cls, name: str) -> None:
        """Validates that a variable name is a valid Python-like identifier."""
        if not name:
            raise ValidationError("Variable name cannot be empty.")
        if not cls.VARIABLE_PATTERN.match(name):
            raise ValidationError(
                f"Invalid variable name '{name}'. Must start with a letter or underscore "
                "and contain only letters, numbers, or underscores."
            )

    @classmethod
    def validate_variable_declarations(cls, variables: List[TemplateVariable]) -> None:
        """Validates all variables defined in a template."""
        seen_names = set()
        for var in variables:
            cls.validate_variable_name(var.name)
            if var.name in seen_names:
                raise ValidationError(f"Duplicate variable name declared: '{var.name}'")
            seen_names.add(var.name)

            # Validate type_hint
            valid_types = {"str", "int", "float", "list", "dict"}
            if var.type_hint not in valid_types:
                raise ValidationError(
                    f"Invalid type hint '{var.type_hint}' for variable '{var.name}'. "
                    f"Must be one of {valid_types}."
                )

    @classmethod
    def validate_template_metadata(cls, template: PromptTemplate) -> None:
        """Validates primary metadata fields of a PromptTemplate."""
        if not template.name or not template.name.strip():
            raise ValidationError("Template name is required and cannot be empty.")
        
        if template.category not in SUPPORTED_CATEGORIES:
            raise ValidationError(
                f"Unsupported category '{template.category}'. "
                f"Supported: {SUPPORTED_CATEGORIES}"
            )

        if template.provider not in SUPPORTED_PROVIDERS:
            raise ValidationError(
                f"Unsupported AI provider '{template.provider}'. "
                f"Supported: {SUPPORTED_PROVIDERS}"
            )

        if not template.user_prompt or not template.user_prompt.strip():
            raise ValidationError("User prompt is a required template field.")

        cls.validate_variable_declarations(template.variables)

    @classmethod
    def validate_rendered_limits(cls, text: str, provider: str) -> List[str]:
        """Checks if rendered text fits within a provider's boundaries.

        Returns:
            List of warning messages if limits are exceeded or recommendations are bypassed.
        """
        warnings = []
        char_len = len(text)
        
        limits = PROVIDER_LIMITS.get(provider)
        if not limits:
            return warnings

        max_chars = limits["max_characters"]
        rec_limit = limits["recommendation_limit"]

        if char_len > max_chars:
            raise ValidationError(
                f"Rendered prompt length ({char_len} chars) exceeds the absolute maximum "
                f"allowable limit of {max_chars} chars for provider '{provider}'."
            )
        elif char_len > rec_limit:
            warnings.append(
                f"Rendered prompt length ({char_len} chars) exceeds recommended limit "
                f"of {rec_limit} chars for provider '{provider}'. Expect slower response times."
            )

        return warnings

    @classmethod
    def detect_prompt_injection(cls, text: str) -> List[str]:
        """Scans rendered or input text for common prompt injection/override phrases.

        Returns:
            List of detected injection keywords/phrases found in the text.
        """
        if not text:
            return []
        
        found = []
        text_lower = text.lower()
        for kw in cls.PROMPT_INJECTION_KEYWORDS:
            if kw in text_lower:
                found.append(kw)
        return found
