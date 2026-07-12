"""Jinja2 rendering engine compiling system, user, and developer instructions with full variables mapping."""

from typing import Any, Dict, Optional, Tuple
from src.prompt_engine.exceptions import RenderError
from src.prompt_engine.models import PromptTemplate, RenderedPrompt
from src.logger.logger_manager import LoggerManager

# Lazy-load jinja2 for optimized performance and memory safety
try:
    import jinja2
    _has_jinja = True
except ImportError:
    _has_jinja = False

logger = LoggerManager().get_logger("prompt_engine.prompt_renderer")


class PromptRenderer:
    """Compiles and renders Jinja2 strings using resolved variable context structures."""

    def __init__(self) -> None:
        """Initializes the renderer.

        Sets up custom Jinja2 environments if available.
        """
        self._env: Optional[Any] = None
        if _has_jinja:
            # Set up a sandbox-like environment with custom filters
            self._env = jinja2.Environment(
                loader=jinja2.BaseLoader(),
                autoescape=False,
                trim_blocks=True,
                lstrip_blocks=True,
            )
            self._register_custom_filters()

    def render(
        self, template: PromptTemplate, resolved_context: Dict[str, Any]
    ) -> RenderedPrompt:
        """Renders system, user, and developer prompts in the template using the variable context.

        Args:
            template: PromptTemplate being compiled.
            resolved_context: Dictionary containing the already resolved variables.

        Returns:
            RenderedPrompt: Fully compiled ready-to-run container.
        """
        logger.info(f"Rendering prompt template: {template.name} (v{template.version})")

        rendered_system = None
        rendered_user = ""
        rendered_developer = None

        try:
            # 1. Render system prompt if present
            if template.system_prompt:
                rendered_system = self._render_string(template.system_prompt, resolved_context)

            # 2. Render user prompt (always required)
            rendered_user = self._render_string(template.user_prompt, resolved_context)

            # 3. Render developer prompt if present
            if template.developer_prompt:
                rendered_developer = self._render_string(template.developer_prompt, resolved_context)

        except Exception as e:
            raise RenderError(f"Failed to render template '{template.name}': {e}") from e

        # Detect remaining/unresolved curly-brace strings that indicate rendering gaps
        import re
        unresolved_vars = set()
        for field_text in [rendered_system, rendered_user, rendered_developer]:
            if field_text:
                # Matches standard Jinja {{ variable }}
                matches = re.findall(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*.*?\}\}", field_text)
                unresolved_vars.update(matches)

        # Build final config settings
        meta_config = {
            "temperature": template.metadata.get("temperature", 0.7),
            "max_tokens": template.metadata.get("max_tokens", 2048),
            "top_p": template.metadata.get("top_p", 1.0),
            "frequency_penalty": template.metadata.get("frequency_penalty", 0.0),
            "presence_penalty": template.metadata.get("presence_penalty", 0.0),
        }

        return RenderedPrompt(
            template_name=template.name,
            version=template.version,
            provider=template.provider,
            system_prompt=rendered_system,
            user_prompt=rendered_user,
            developer_prompt=rendered_developer,
            json_schema=template.json_schema,
            resolved_variables=resolved_context,
            unresolved_variables=unresolved_vars,
            meta_config=meta_config,
        )

    def _render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """Renders an individual template string with variables."""
        if not template_str:
            return ""

        if not _has_jinja:
            # Basic fallback if Jinja2 is somehow missing
            logger.warning("Jinja2 is not installed! Running basic format fallback rendering.")
            result = template_str
            for key, val in context.items():
                placeholder = f"{{{{ {key} }}}}"
                result = result.replace(placeholder, str(val))
                # Also support simple formatting
                placeholder_simple = f"{{{{{key}}}}}"
                result = result.replace(placeholder_simple, str(val))
            return result

        try:
            assert self._env is not None
            tpl = self._env.from_string(template_str)
            return tpl.render(**context)
        except Exception as jinja_err:
            raise RenderError(f"Jinja2 compiler error: {jinja_err}") from jinja_err

    def _register_custom_filters(self) -> None:
        """Registers custom domain-specific template filters (e.g. trimming, list formats)."""
        if not self._env:
            return

        def wrap_list(val: Any) -> str:
            """Formats a Python list into formatted bullet lines."""
            if not val:
                return ""
            if isinstance(val, list):
                return "\n".join(f"- {item}" for item in val)
            return f"- {val}"

        def char_count(val: Any) -> int:
            """Counts length of string."""
            return len(str(val)) if val else 0

        self._env.filters["bullet_list"] = wrap_list
        self._env.filters["char_count"] = char_count
