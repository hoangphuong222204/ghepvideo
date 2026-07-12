"""VariableResolver compiles, types, and defaults context variables before rendering prompts."""

import os
from typing import Any, Dict, List, Optional, Set, Tuple
from src.prompt_engine.exceptions import ResolveError
from src.prompt_engine.models import PromptTemplate, TemplateVariable
from src.logger.logger_manager import LoggerManager

logger = LoggerManager().get_logger("prompt_engine.variable_resolver")


class VariableResolver:
    """Consolidates values, environment variables, and type hints into a finalized context dictionary."""

    @classmethod
    def resolve(
        cls, template: PromptTemplate, user_variables: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Set[str]]:
        """Resolves inputs against a template's expected variables.

        Args:
            template: The PromptTemplate instance containing variable constraints.
            user_variables: Key-value values passed in by the caller.

        Returns:
            Tuple containing:
            - resolved_context (Dict[str, Any]): Clean, typed context ready for injection.
            - unresolved_names (Set[str]): Variables that were required but failed resolution.
        """
        resolved_context = {}
        unresolved_names = set()

        # Map declared variable metadata by name
        declared_map: Dict[str, TemplateVariable] = {v.name: v for v in template.variables}

        # First, copy user values and perform casting where declarations exist
        for name, value in user_variables.items():
            if name in declared_map:
                try:
                    resolved_context[name] = cls._cast_type(value, declared_map[name].type_hint)
                except Exception as e:
                    logger.warning(f"Type-casting variable '{name}' to '{declared_map[name].type_hint}' failed: {e}")
                    resolved_context[name] = value  # Keep original if casting fails
            else:
                resolved_context[name] = value  # Keep ad-hoc undeclared user-supplied variables

        # Second, look for missing declared variables and try to resolve via defaults or ENV
        for name, var_meta in declared_map.items():
            if name in resolved_context:
                continue

            resolved_val = None

            # 1. Attempt Environment Variable fallback
            if var_meta.fallback_env_var:
                resolved_val = os.getenv(var_meta.fallback_env_var)
                if resolved_val is not None:
                    try:
                        resolved_val = cls._cast_type(resolved_val, var_meta.type_hint)
                        resolved_context[name] = resolved_val
                        logger.debug(f"Resolved variable '{name}' from environment variable: {var_meta.fallback_env_var}")
                        continue
                    except Exception:
                        pass

            # 2. Attempt Default Value fallback
            if var_meta.default_value is not None:
                resolved_context[name] = var_meta.default_value
                continue

            # 3. Check if required
            if var_meta.is_required:
                unresolved_names.add(name)

        return resolved_context, unresolved_names

    @staticmethod
    def _cast_type(val: Any, type_hint: str) -> Any:
        """Helper performing clean conversions based on specified variable types."""
        if val is None:
            return None

        type_hint_clean = type_hint.strip().lower()

        if type_hint_clean == "str":
            return str(val)
        elif type_hint_clean == "int":
            return int(float(val))  # handle decimal strings like "10.0" -> 10
        elif type_hint_clean == "float":
            return float(val)
        elif type_hint_clean == "list":
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                # Simple comma separation fallback
                return [item.strip() for item in val.split(",") if item.strip()]
            return [val]
        elif type_hint_clean == "dict":
            if isinstance(val, dict):
                return val
            if isinstance(val, str):
                import json
                return json.loads(val)
            return {"value": val}

        return val
