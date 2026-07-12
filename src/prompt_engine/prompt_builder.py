"""Fluent Builder pattern for programmatically constructing PromptTemplate configurations."""

from typing import Any, Dict, List, Optional
from src.prompt_engine.models import PromptTemplate, TemplateVariable, VersionInfo
from src.prompt_engine.constants import PROVIDER_GEMINI, CAT_MARKETING, VERSION_STABILITY_DRAFT


class PromptBuilder:
    """Fluent Builder facilitating programmatic compilation of PromptTemplate structures."""

    def __init__(self, name: str) -> None:
        """Initializes the builder with a required template name."""
        self._name = name
        self._category = CAT_MARKETING
        self._provider = PROVIDER_GEMINI
        self._version = "1.0.0"
        self._description = ""
        self._system_prompt: Optional[str] = None
        self._user_prompt = ""
        self._developer_prompt: Optional[str] = None
        self._variables: List[TemplateVariable] = []
        self._tags: List[str] = []
        self._json_schema: Optional[Dict[str, Any]] = None
        self._metadata: Dict[str, Any] = {"stability": VERSION_STABILITY_DRAFT}

    def set_category(self, category: str) -> "PromptBuilder":
        """Sets the template's functional category classification."""
        self._category = category
        return self

    def set_provider(self, provider: str) -> "PromptBuilder":
        """Sets the target LLM provider (e.g. Gemini, OpenAI, Claude)."""
        self._provider = provider
        return self

    def set_version(self, version: str) -> "PromptBuilder":
        """Sets the starting semantic version."""
        self._version = version
        return self

    def set_description(self, description: str) -> "PromptBuilder":
        """Sets the description."""
        self._description = description
        return self

    def set_system_prompt(self, system_prompt: str) -> "PromptBuilder":
        """Sets system-level instructions."""
        self._system_prompt = system_prompt
        return self

    def set_user_prompt(self, user_prompt: str) -> "PromptBuilder":
        """Sets user-level instructions template (supporting Jinja2 templates)."""
        self._user_prompt = user_prompt
        return self

    def set_developer_prompt(self, developer_prompt: str) -> "PromptBuilder":
        """Sets developer instructions."""
        self._developer_prompt = developer_prompt
        return self

    def add_variable(
        self,
        name: str,
        description: Optional[str] = None,
        default_value: Optional[Any] = None,
        is_required: bool = True,
        type_hint: str = "str",
        fallback_env_var: Optional[str] = None,
    ) -> "PromptBuilder":
        """Registers a expected input variable constraint to the template."""
        self._variables.append(
            TemplateVariable(
                name=name,
                description=description,
                default_value=default_value,
                is_required=is_required,
                type_hint=type_hint,
                fallback_env_var=fallback_env_var,
            )
        )
        return self

    def set_tags(self, tags: List[str]) -> "PromptBuilder":
        """Appends list of organizational tags."""
        self._tags = tags
        return self

    def set_json_schema(self, schema: Dict[str, Any]) -> "PromptBuilder":
        """Registers a target structured JSON Output schema."""
        self._json_schema = schema
        return self

    def add_metadata_field(self, key: str, value: Any) -> "PromptBuilder":
        """Injects custom operational parameters (e.g., temperature, max_tokens)."""
        self._metadata[key] = value
        return self

    def build(self) -> PromptTemplate:
        """Assembles and returns the fully configured, immutable PromptTemplate."""
        return PromptTemplate(
            name=self._name,
            category=self._category,
            provider=self._provider,
            version=self._version,
            description=self._description,
            system_prompt=self._system_prompt,
            user_prompt=self._user_prompt,
            developer_prompt=self._developer_prompt,
            variables=self._variables,
            tags=self._tags,
            json_schema=self._json_schema,
            metadata=self._metadata,
        )
