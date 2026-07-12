"""Unified facade for Module 06: Prompt Engine, orchestrating sub-components in a simple API."""

from typing import Any, Dict, List, Optional, Tuple
from src.prompt_engine.models import (
    PromptTemplate,
    RenderedPrompt,
    OptimizationResult,
    PromptCompareResult,
    PromptHistoryRecord,
    ABTestConfig,
)
from src.prompt_engine.prompt_manager import PromptManager
from src.prompt_engine.prompt_exporter import PromptExporter
from src.prompt_engine.prompt_importer import PromptImporter
from src.prompt_engine.prompt_templates import PromptTemplates
from src.logger.logger_manager import LoggerManager

logger = LoggerManager().get_logger("prompt_engine")


class PromptEngine:
    """Unified Facade for AI Marketing Studio PRO's Enterprise Prompt Engine (Module 06).

    Coordinates version control, testing, compression, import/export, variable resolution, and history
    auditing.
    """

    def __init__(
        self,
        storage_dir: str = "./assets/prompts",
        history_filepath: str = "./assets/prompt_history.jsonl",
        cache_max_size: int = 1000,
        cache_ttl_seconds: int = 300,
    ) -> None:
        """Initializes the Prompt Engine Facade.

        Args:
            storage_dir: Base directory path to persist JSON template configurations.
            history_filepath: Path to append rendered prompt invocation histories.
            cache_max_size: Maximum compiled templates stored in memory.
            cache_ttl_seconds: Cache duration (seconds) before reloading from disk.
        """
        self._manager = PromptManager(
            storage_dir=storage_dir,
            history_filepath=history_filepath,
            cache_max_size=cache_max_size,
            cache_ttl_seconds=cache_ttl_seconds,
        )
        logger.info("Successfully booted Enterprise Prompt Engine Module (Module 06).")

    # --- Core Template Management ---

    def get_template(self, name: str, version: Optional[str] = None, use_cache: bool = True) -> PromptTemplate:
        """Loads a specific template. If no version is supplied, resolves the highest semantic version."""
        return self._manager.get_template(name=name, version=version, use_cache=use_cache)

    def create_template(self, template: PromptTemplate) -> None:
        """Validates structure, locks versioning parameters, and saves template to disk storage."""
        self._manager.create_template(template)

    def update_template(self, template: PromptTemplate) -> None:
        """Saves template to disk, checking if the template is locked or version-conflicted."""
        self._manager.update_template(template)

    def delete_template(self, name: str, version: Optional[str] = None) -> bool:
        """Deletes a template variant from disk and removes it from cache."""
        return self._manager.delete_template(name=name, version=version)

    def list_templates(self, category: Optional[str] = None, provider: Optional[str] = None) -> List[PromptTemplate]:
        """Scans disk storage and returns all parsed template configurations, optionally filtered."""
        return self._manager.repository.list_templates(category=category, provider=provider)

    # --- Variables & Rendering Pipeline ---

    def render_prompt(
        self,
        template_name: str,
        user_variables: Dict[str, Any],
        version: Optional[str] = None,
        use_cache: bool = True,
        log_invocation: bool = True,
    ) -> RenderedPrompt:
        """Standard compilation interface. Loads template, resolves variables/defaults, renders, and logs."""
        return self._manager.render_prompt(
            template_name=template_name,
            user_variables=user_variables,
            version=version,
            use_cache=use_cache,
            log_invocation=log_invocation,
        )

    # --- Versioning & Comparative Diffs ---

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
        """Increments a template's semantic version, archving the prior code in version history."""
        return self._manager.version_bump(
            template_name=template_name,
            new_user_prompt=new_user_prompt,
            new_system_prompt=new_system_prompt,
            new_developer_prompt=new_developer_prompt,
            author=author,
            bump_type=bump_type,
            change_description=change_description,
        )

    def compare_templates(self, template_name: str, version_a: str, version_b: str) -> PromptCompareResult:
        """Generates line-by-line visual differences and tracks variable shifts between two versions."""
        return self._manager.compare_templates(
            template_name=template_name,
            version_a=version_a,
            version_b=version_b,
        )

    # --- Token Optimization & Compression ---

    def optimize_prompt(
        self,
        text: str,
        compress_whitespace: bool = True,
        remove_fillers: bool = False,
        uppercase_keywords: bool = False,
    ) -> OptimizationResult:
        """Applies whitespace compression and conversational filler strips to reduce prompt length."""
        return self._manager.optimize_prompt(
            text=text,
            compress_whitespace=compress_whitespace,
            remove_fillers=remove_fillers,
            uppercase_keywords=uppercase_keywords,
        )

    # --- A/B Testing & Conversions ---

    def create_ab_test(
        self,
        test_id: str,
        name: str,
        template_name: str,
        version_a: str,
        version_b: str,
        allocation_ratio_a: float = 0.5,
    ) -> ABTestConfig:
        """Registers a new A/B split traffic testing experiment configuration."""
        return self._manager.ab_testing.create_test(
            test_id=test_id,
            name=name,
            template_name=template_name,
            version_a=version_a,
            version_b=version_b,
            allocation_ratio_a=allocation_ratio_a,
        )

    def select_test_version(self, config: ABTestConfig) -> Tuple[str, str]:
        """Routes execution traffic to variant A or B based on allocation factor percentages."""
        return self._manager.ab_testing.select_version(config)

    def record_test_conversion(self, config: ABTestConfig, variant: str) -> None:
        """Logs a business conversion event for variant 'A' or 'B'."""
        self._manager.ab_testing.record_conversion(config, variant)

    def get_test_stats(self, config: ABTestConfig) -> Dict[str, Any]:
        """Generates performance conversion ratios and determines leading A/B variant."""
        return self._manager.ab_testing.get_test_stats(config)

    # --- Serialization Exporters ---

    def export_to_json(self, template: PromptTemplate, indent: int = 2) -> str:
        """Serializes a PromptTemplate dataclass into a structured JSON string."""
        return PromptExporter.export_to_json(template, indent=indent)

    def export_to_yaml(self, template: PromptTemplate) -> str:
        """Serializes a PromptTemplate dataclass into a clean YAML string."""
        return PromptExporter.export_to_yaml(template)

    def export_to_text(self, template: PromptTemplate) -> str:
        """Serializes a PromptTemplate dataclass into a plain text instruction block."""
        return PromptExporter.export_to_text(template)

    def import_from_json(self, json_str: str) -> PromptTemplate:
        """Parses a structured JSON string back into an active PromptTemplate configuration."""
        return PromptImporter.import_from_json(json_str)

    def import_from_yaml(self, yaml_str: str) -> PromptTemplate:
        """Parses a YAML string configuration back into an active PromptTemplate configuration."""
        return PromptImporter.import_from_yaml(yaml_str)

    # --- Telemetry & Diagnostics ---

    def get_history(self, template_name: Optional[str] = None) -> List[PromptHistoryRecord]:
        """Retrieves list of past prompt rendering executions, optionally filtered by template name."""
        return self._manager.history.get_history(template_name)

    def mark_conversion(self, record_id: str) -> bool:
        """Marks a historical invocation record as having successfully achieved its conversion goal."""
        return self._manager.history.mark_conversion(record_id)

    def get_default_templates(self) -> List[PromptTemplate]:
        """Returns list of pre-packaged, out-of-the-box system template blueprints."""
        return PromptTemplates.get_all_defaults()
