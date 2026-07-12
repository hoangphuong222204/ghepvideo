"""PromptManager coordinates repository, caching, rendering, validation, and history tracking."""

import difflib
from typing import Any, Dict, List, Optional, Set, Tuple
from src.prompt_engine.exceptions import ValidationError, TemplateNotFoundError, RenderError
from src.prompt_engine.models import (
    PromptTemplate,
    RenderedPrompt,
    OptimizationResult,
    PromptCompareResult,
    PromptDiffLine,
    ABTestConfig,
)
from src.prompt_engine.constants import DEFAULT_CACHE_TTL_SECONDS
from src.prompt_engine.template_repository import TemplateRepository
from src.prompt_engine.template_cache import TemplateCache
from src.prompt_engine.variable_resolver import VariableResolver
from src.prompt_engine.prompt_renderer import PromptRenderer
from src.prompt_engine.validators import PromptValidator
from src.prompt_engine.prompt_optimizer import PromptOptimizer
from src.prompt_engine.version_manager import VersionManager
from src.prompt_engine.ab_testing import ABTestingManager
from src.prompt_engine.prompt_history import PromptHistoryManager
from src.logger.logger_manager import LoggerManager

logger = LoggerManager().get_logger("prompt_engine.prompt_manager")


class PromptManager:
    """Central manager coordinating all services for templates, rendering, verification, and instrumentation."""

    def __init__(
        self,
        storage_dir: str = "./assets/prompts",
        history_filepath: str = "./assets/prompt_history.jsonl",
        cache_max_size: int = 1000,
        cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    ) -> None:
        """Initializes PromptManager with target paths and size defaults."""
        self.repository = TemplateRepository(storage_dir=storage_dir)
        self.cache = TemplateCache(max_size=cache_max_size, default_ttl_seconds=cache_ttl_seconds)
        self.renderer = PromptRenderer()
        self.history = PromptHistoryManager(history_filepath=history_filepath)
        self.ab_testing = ABTestingManager()

    def get_template(self, name: str, version: Optional[str] = None, use_cache: bool = True) -> PromptTemplate:
        """Loads a specific template. Resolves highest version if None specified."""
        cache_key = f"{name}::v{version or 'latest'}"
        
        if use_cache:
            cached_tpl = self.cache.get(cache_key)
            if cached_tpl:
                logger.debug(f"Cache HIT for template key: {cache_key}")
                return cached_tpl

        # Retrieve from physical disk store
        template = self.repository.get_template(name=name, version=version)
        
        if use_cache:
            self.cache.set(cache_key, template)
            # If loaded latest, also cache under specific version to speed up future lookups
            if not version:
                specific_key = f"{name}::v{template.version}"
                self.cache.set(specific_key, template)

        return template

    def create_template(self, template: PromptTemplate) -> None:
        """Validates, locks configuration, saves to repository, and populates caches."""
        PromptValidator.validate_template_metadata(template)
        
        # Save to disk
        self.repository.save_template(template)
        
        # Clear caches to enforce fresh loads
        self.cache.delete(f"{template.name}::v{template.version}")
        self.cache.delete(f"{template.name}::vlatest")

    def update_template(self, template: PromptTemplate) -> None:
        """Overwrites an existing template version on disk, checking locking parameters."""
        # Load existing first to check if locked
        try:
            existing = self.repository.get_template(template.name, template.version)
            if existing.is_locked:
                raise ValidationError(
                    f"Cannot overwrite locked template '{template.name}' (v{template.version}). "
                    "Create a new version bump instead."
                )
        except TemplateNotFoundError:
            pass  # New version is fine

        self.create_template(template)

    def delete_template(self, name: str, version: Optional[str] = None) -> bool:
        """Deletes a template variant from disk and removes it from memory cache."""
        deleted = self.repository.delete_template(name, version)
        if deleted:
            if version:
                self.cache.delete(f"{name}::v{version}")
            else:
                self.cache.clear()  # Clear all to avoid legacy version references
        return deleted

    def render_prompt(
        self,
        template_name: str,
        user_variables: Dict[str, Any],
        version: Optional[str] = None,
        use_cache: bool = True,
        log_invocation: bool = True,
    ) -> RenderedPrompt:
        """Full execution pipeline: loads template, resolves variables, compiles strings, and runs audit logs."""
        import time
        start_time = time.perf_counter()

        # 1. Fetch template
        template = self.get_template(template_name, version=version, use_cache=use_cache)

        try:
            # 2. Resolve missing fields and cast type hints
            resolved_context, unresolved_names = VariableResolver.resolve(template, user_variables)

            # 3. Compile strings with template engine
            rendered = self.renderer.render(template, resolved_context)

            # 4. Exceeds provider limits validation
            warnings = PromptValidator.validate_rendered_limits(rendered.user_prompt, rendered.provider)
            if warnings:
                rendered.meta_config["warnings"] = warnings

            # 5. Injection safety scanner
            injection_flags = PromptValidator.detect_prompt_injection(rendered.user_prompt)
            if injection_flags:
                rendered.meta_config["injection_warnings"] = injection_flags
                logger.warning(
                    f"POTENTIAL PROMPT INJECTION DETECTED in rendered prompt '{template_name}': "
                    f"Flags: {injection_flags}"
                )

            # 6. Instrument execution
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            if log_invocation:
                self.history.add_record(
                    template_name=template.name,
                    version=template.version,
                    provider=template.provider,
                    user_prompt=rendered.user_prompt,
                    variables_used=resolved_context,
                    system_prompt=rendered.system_prompt,
                    developer_prompt=rendered.developer_prompt,
                    is_success=True,
                    response_latency_ms=round(latency_ms, 2),
                )

            return rendered

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            if log_invocation:
                self.history.add_record(
                    template_name=template.name,
                    version=version or "unknown",
                    provider=template.provider if "template" in locals() else "unknown",
                    user_prompt="",
                    variables_used=user_variables,
                    is_success=False,
                    error_message=str(e),
                    response_latency_ms=round(latency_ms, 2),
                )
            raise e

    def version_bump(
        self,
        template_name: str,
        new_user_prompt: str,
        new_system_prompt: Optional[str] = None,
        new_developer_prompt: Optional[str] = None,
        author: str = "system",
        bump_type: str = "patch",
        change_description: str = "Updated template text",
    ) -> PromptTemplate:
        """Performs semantic version incrementation on a template configuration, validating and storing the result."""
        # Always fetch latest to perform bump
        latest_tpl = self.get_template(template_name, version=None, use_cache=False)
        
        new_tpl = VersionManager.create_new_version(
            template=latest_tpl,
            new_user_prompt=new_user_prompt,
            new_system_prompt=new_system_prompt,
            new_developer_prompt=new_developer_prompt,
            author=author,
            bump_type=bump_type,
            change_description=change_description,
        )

        self.create_template(new_tpl)
        return new_tpl

    def optimize_prompt(
        self,
        text: str,
        compress_whitespace: bool = True,
        remove_fillers: bool = False,
        uppercase_keywords: bool = False,
    ) -> OptimizationResult:
        """Utility method exposing PromptOptimizer logic directly."""
        return PromptOptimizer.optimize(
            text=text,
            compress_whitespace=compress_whitespace,
            remove_fillers=remove_fillers,
            uppercase_keywords=uppercase_keywords,
        )

    def compare_templates(self, template_name: str, version_a: str, version_b: str) -> PromptCompareResult:
        """Performs visual and metadata diff alignment comparison between two template versions."""
        tpl_a = self.get_template(template_name, version=version_a, use_cache=False)
        tpl_b = self.get_template(template_name, version=version_b, use_cache=False)

        # 1. Diff User Prompt
        user_diff = self._generate_text_diff(tpl_a.user_prompt, tpl_b.user_prompt)

        # 2. Diff System Prompt
        sys_a = tpl_a.system_prompt or ""
        sys_b = tpl_b.system_prompt or ""
        sys_diff = self._generate_text_diff(sys_a, sys_b)

        # 3. Diff Variables
        vars_a = {v.name for v in tpl_a.variables}
        vars_b = {v.name for v in tpl_b.variables}

        added_vars = list(vars_b - vars_a)
        removed_vars = list(vars_a - vars_b)

        return PromptCompareResult(
            template_name=template_name,
            version_a=version_a,
            version_b=version_b,
            system_prompt_diff=sys_diff,
            user_prompt_diff=user_diff,
            added_variables=added_vars,
            removed_variables=removed_vars,
        )

    def _generate_text_diff(self, text_a: str, text_b: str) -> List[PromptDiffLine]:
        """Aligns lines and labels them as equal, inserted, or deleted."""
        lines_a = text_a.splitlines()
        lines_b = text_b.splitlines()

        matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
        diff_lines = []

        line_num_a = 1
        line_num_b = 1

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                for idx in range(i1, i2):
                    diff_lines.append(
                        PromptDiffLine(
                            type="equal",
                            line_number_a=line_num_a,
                            line_number_b=line_num_b,
                            content=lines_a[idx],
                        )
                    )
                    line_num_a += 1
                    line_num_b += 1
            elif tag == "delete":
                for idx in range(i1, i2):
                    diff_lines.append(
                        PromptDiffLine(
                            type="delete",
                            line_number_a=line_num_a,
                            line_number_b=None,
                            content=lines_a[idx],
                        )
                    )
                    line_num_a += 1
            elif tag == "insert":
                for idx in range(j1, j2):
                    diff_lines.append(
                        PromptDiffLine(
                            type="insert",
                            line_number_a=None,
                            line_number_b=line_num_b,
                            content=lines_b[idx],
                        )
                    )
                    line_num_b += 1
            elif tag == "replace":
                # Represent as sequence of deletions then insertions
                for idx in range(i1, i2):
                    diff_lines.append(
                        PromptDiffLine(
                            type="delete",
                            line_number_a=line_num_a,
                            line_number_b=None,
                            content=lines_a[idx],
                        )
                    )
                    line_num_a += 1
                for idx in range(j1, j2):
                    diff_lines.append(
                        PromptDiffLine(
                            type="insert",
                            line_number_a=None,
                            line_number_b=line_num_b,
                            content=lines_b[idx],
                        )
                    )
                    line_num_b += 1

        return diff_lines
