"""Exporter saving prompt configurations into JSON, YAML, or TXT formats."""

import json
from typing import Any, Dict
from src.prompt_engine.exceptions import SerializationError
from src.prompt_engine.models import PromptTemplate
from src.prompt_engine.template_loader import TemplateLoader

try:
    import yaml
    _has_yaml = True
except ImportError:
    _has_yaml = False


class PromptExporter:
    """Exports structured PromptTemplate objects into standardized data interchange formats."""

    @classmethod
    def export_to_json(cls, template: PromptTemplate, indent: int = 2) -> str:
        """Converts a template into a structured JSON string."""
        try:
            data = TemplateLoader.to_dict(template)
            return json.dumps(data, ensure_ascii=False, indent=indent)
        except Exception as e:
            raise SerializationError(f"Failed to export template '{template.name}' to JSON: {e}") from e

    @classmethod
    def export_to_yaml(cls, template: PromptTemplate) -> str:
        """Converts a template into a clean YAML string.

        Falls back to JSON serialization if PyYAML is not installed.
        """
        data = TemplateLoader.to_dict(template)
        
        if not _has_yaml:
            # Fallback to JSON if PyYAML is not in the environment
            return cls.export_to_json(template)

        try:
            return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
        except Exception as e:
            raise SerializationError(f"Failed to export template '{template.name}' to YAML: {e}") from e

    @classmethod
    def export_to_text(cls, template: PromptTemplate) -> str:
        """Compiles a template into a clean, human-readable instructions prompt file block."""
        lines = [
            f"=== PROMPT TEMPLATE: {template.name} (v{template.version}) ===",
            f"Category: {template.category}",
            f"Provider: {template.provider}",
            f"Description: {template.description}",
            "==================================================",
        ]

        if template.system_prompt:
            lines.append("--- SYSTEM INSTRUCTIONS ---")
            lines.append(template.system_prompt.strip())
            lines.append("---------------------------")

        if template.developer_prompt:
            lines.append("--- DEVELOPER INSTRUCTIONS ---")
            lines.append(template.developer_prompt.strip())
            lines.append("------------------------------")

        lines.append("--- USER PROMPT TEMPLATE ---")
        lines.append(template.user_prompt.strip())
        lines.append("----------------------------")

        if template.variables:
            lines.append("--- EXPECTED VARIABLES ---")
            for var in template.variables:
                req_str = "Required" if var.is_required else "Optional"
                def_str = f" (Default: {var.default_value})" if var.default_value is not None else ""
                lines.append(f"- {var.name} [{var.type_hint}] ({req_str}){def_str}: {var.description or ''}")
            lines.append("--------------------------")

        return "\n\n".join(lines)
