"""Importer parsing JSON and YAML strings back into structured PromptTemplate instances."""

import json
from typing import Any, Dict
from src.prompt_engine.exceptions import ValidationError, SerializationError
from src.prompt_engine.models import PromptTemplate
from src.prompt_engine.template_loader import TemplateLoader

try:
    import yaml
    _has_yaml = True
except ImportError:
    _has_yaml = False


class PromptImporter:
    """Parses text payloads representing serialization objects into active PromptTemplate instances."""

    @classmethod
    def import_from_json(cls, json_str: str) -> PromptTemplate:
        """Parses a structured JSON string into a verified PromptTemplate instance."""
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise ValidationError("JSON payload must resolve to a dictionary object.")
            return TemplateLoader.from_dict(data)
        except Exception as e:
            if isinstance(e, (ValidationError, SerializationError)):
                raise e
            raise SerializationError(f"Failed to parse and import JSON string: {e}") from e

    @classmethod
    def import_from_yaml(cls, yaml_str: str) -> PromptTemplate:
        """Parses a YAML configuration string.

        Falls back to JSON decoding if PyYAML is unavailable.
        """
        if not _has_yaml:
            # Fallback attempt via JSON parser if PyYAML is missing
            try:
                return cls.import_from_json(yaml_str)
            except Exception:
                raise SerializationError(
                    "YAML library (PyYAML) is not installed, and fallback JSON parsing "
                    "failed. Please install 'pyyaml' to import standard YAML files."
                )

        try:
            data = yaml.safe_load(yaml_str)
            if not isinstance(data, dict):
                raise ValidationError("YAML payload must resolve to a dictionary object.")
            return TemplateLoader.from_dict(data)
        except Exception as e:
            if isinstance(e, (ValidationError, SerializationError)):
                raise e
            raise SerializationError(f"Failed to parse and import YAML string: {e}") from e
