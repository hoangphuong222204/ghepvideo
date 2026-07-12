"""Loader parsing dictionaries, JSON, and files into typed PromptTemplate configurations."""

import json
import os
from typing import Any, Dict, List, Optional
from src.prompt_engine.exceptions import ValidationError, SerializationError
from src.prompt_engine.models import PromptTemplate, TemplateVariable, VersionInfo


class TemplateLoader:
    """Helper class deserializing plain dictionary data into strict dataclass templates."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PromptTemplate:
        """Parses a dictionary into a typed PromptTemplate configuration."""
        try:
            name = data.get("name")
            category = data.get("category")
            provider = data.get("provider")

            if not name or not category or not provider:
                raise ValidationError("Template dictionary must declare 'name', 'category', and 'provider'.")

            # Parse variables metadata if present
            vars_raw = data.get("variables", [])
            variables_list = []
            for v in vars_raw:
                if isinstance(v, dict):
                    variables_list.append(
                        TemplateVariable(
                            name=v["name"],
                            description=v.get("description"),
                            default_value=v.get("default_value"),
                            is_required=v.get("is_required", True),
                            type_hint=v.get("type_hint", "str"),
                            fallback_env_var=v.get("fallback_env_var"),
                        )
                    )
                elif isinstance(v, str):
                    variables_list.append(TemplateVariable(name=v))

            # Parse version history if present
            history_raw = data.get("version_history", [])
            version_history_list = []
            for h in history_raw:
                if isinstance(h, dict):
                    import datetime
                    created_at_val = h.get("created_at")
                    if isinstance(created_at_val, str):
                        try:
                            created_at = datetime.datetime.fromisoformat(created_at_val)
                        except ValueError:
                            created_at = datetime.datetime.utcnow()
                    else:
                        created_at = datetime.datetime.utcnow()

                    version_history_list.append(
                        VersionInfo(
                            version=h.get("version", "1.0.0"),
                            author=h.get("author", "system"),
                            created_at=created_at,
                            description=h.get("description", ""),
                            stability=h.get("stability", "Draft"),
                            change_log=h.get("change_log"),
                        )
                    )

            # Metadata parsing
            metadata = data.get("metadata", {})

            return PromptTemplate(
                name=name,
                category=category,
                provider=provider,
                version=data.get("version", "1.0.0"),
                description=data.get("description", ""),
                system_prompt=data.get("system_prompt"),
                user_prompt=data.get("user_prompt", ""),
                developer_prompt=data.get("developer_prompt"),
                variables=variables_list,
                tags=data.get("tags", []),
                json_schema=data.get("json_schema"),
                version_history=version_history_list,
                is_locked=data.get("is_locked", False),
                metadata=metadata,
            )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise SerializationError(f"Failed to load PromptTemplate from dict payload: {e}") from e

    @classmethod
    def from_json_file(cls, filepath: str) -> PromptTemplate:
        """Reads a JSON file from disk and parses it into a PromptTemplate."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Template configuration file not found: '{filepath}'")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise SerializationError(f"Failed to read and compile template file at '{filepath}': {e}") from e

    @classmethod
    def to_dict(cls, template: PromptTemplate) -> Dict[str, Any]:
        """Serializes a PromptTemplate dataclass back into a JSON-compatible dictionary."""
        variables_serialized = [
            {
                "name": v.name,
                "description": v.description,
                "default_value": v.default_value,
                "is_required": v.is_required,
                "type_hint": v.type_hint,
                "fallback_env_var": v.fallback_env_var,
            }
            for v in template.variables
        ]

        history_serialized = [
            {
                "version": h.version,
                "author": h.author,
                "created_at": h.created_at.isoformat(),
                "description": h.description,
                "stability": h.stability,
                "change_log": h.change_log,
            }
            for h in template.version_history
        ]

        return {
            "name": template.name,
            "category": template.category,
            "provider": template.provider,
            "version": template.version,
            "description": template.description,
            "system_prompt": template.system_prompt,
            "user_prompt": template.user_prompt,
            "developer_prompt": template.developer_prompt,
            "variables": variables_serialized,
            "tags": template.tags,
            "json_schema": template.json_schema,
            "version_history": history_serialized,
            "is_locked": template.is_locked,
            "metadata": template.metadata,
        }
