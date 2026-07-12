"""Fluent builder for compiling structured prompts and system instructions."""

from typing import Dict, Any, Optional
from src.ai.prompt_templates import (
    VERTICAL_VIDEO_SCRIPT_TEMPLATE,
    PRODUCT_PITCH_COPY_TEMPLATE,
    VOICE_HOOK_GENERATOR_TEMPLATE,
)

class PromptBuilder:
    """Builder class for assembling dynamic, parameter-injected marketing prompts."""

    def __init__(self, base_template: Optional[str] = None) -> None:
        """Initializes the PromptBuilder with an optional template.

        Args:
            base_template: Standard template string.
        """
        self._template = base_template or ""
        self._variables: Dict[str, Any] = {}
        self._system_instruction: Optional[str] = None

    @classmethod
    def vertical_video_script(cls) -> "PromptBuilder":
        """Pre-loads the vertical video script template."""
        return cls(VERTICAL_VIDEO_SCRIPT_TEMPLATE)

    @classmethod
    def product_pitch_copy(cls) -> "PromptBuilder":
        """Pre-loads the product pitch copy template."""
        return cls(PRODUCT_PITCH_COPY_TEMPLATE)

    @classmethod
    def voice_hook_generator(cls) -> "PromptBuilder":
        """Pre-loads the voice hook generator template."""
        return cls(VOICE_HOOK_GENERATOR_TEMPLATE)

    def set_template(self, template: str) -> "PromptBuilder":
        """Sets or overwrites the base prompt template.

        Args:
            template: The template string with placeholder variables.
        """
        self._template = template
        return self

    def set_system_instruction(self, instruction: str) -> "PromptBuilder":
        """Sets the system instruction role."""
        self._system_instruction = instruction
        return self

    def bind(self, key: str, value: Any) -> "PromptBuilder":
        """Binds a variable placeholder to its concrete value.

        Args:
            key: Placeholder variable name inside curly braces (e.g., 'product_name').
            value: Concrete value to inject.
        """
        self._variables[key] = value
        return self

    def bind_dict(self, variables: Dict[str, Any]) -> "PromptBuilder":
        """Binds a dictionary of variable placeholders to their values."""
        self._variables.update(variables)
        return self

    def build_prompt(self) -> str:
        """Compiles and returns the finalized user prompt string."""
        if not self._template:
            return ""
        try:
            return self._template.format(**self._variables)
        except KeyError as e:
            # Fallback to simple replacement if string formatting complains about curly brackets in content
            missing_key = str(e).strip("'")
            raise ValueError(f"Missing required parameter '{missing_key}' to format the prompt template.") from e

    def build_system_instruction(self) -> Optional[str]:
        """Returns the compiled system instruction."""
        return self._system_instruction
