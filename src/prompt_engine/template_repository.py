"""Repository managing template file I/O, listing, sorting, and default template seeding."""

import os
import re
from typing import List, Optional, Dict, Any
from src.prompt_engine.exceptions import TemplateNotFoundError, StorageError
from src.prompt_engine.models import PromptTemplate
from src.prompt_engine.constants import DEFAULT_TEMPLATES
from src.prompt_engine.template_loader import TemplateLoader
from src.logger.logger_manager import LoggerManager

logger = LoggerManager().get_logger("prompt_engine.template_repository")


class TemplateRepository:
    """Manages physical JSON storage, retrieval, deletion, and search queries for prompt templates."""

    def __init__(self, storage_dir: str = "./assets/prompts") -> None:
        """Initializes the repository with a targeted storage path.

        Creates directory structures if they do not exist.
        """
        self._storage_dir = os.path.abspath(storage_dir)
        os.makedirs(self._storage_dir, exist_ok=True)
        logger.info(f"Initialized Prompt Template Repository at: {self._storage_dir}")
        self.seed_default_templates()

    def save_template(self, template: PromptTemplate) -> None:
        """Saves a prompt template to a JSON file named after its name and version."""
        # Sanitize name and version to avoid directory traversal
        safe_name = self._sanitize_filename(template.name)
        safe_version = self._sanitize_filename(template.version)
        
        filename = f"{safe_name}_v{safe_version}.json"
        filepath = os.path.join(self._storage_dir, filename)

        try:
            serialized_data = TemplateLoader.to_dict(template)
            import json
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(serialized_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved template: {template.name} (v{template.version}) to {filename}")
        except Exception as e:
            raise StorageError(f"Failed to save template '{template.name}' to disk: {e}") from e

    def get_template(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        """Loads a specific template. If no version is supplied, resolves the highest semantic version."""
        safe_name = self._sanitize_filename(name)
        
        if version:
            safe_version = self._sanitize_filename(version)
            filename = f"{safe_name}_v{safe_version}.json"
            filepath = os.path.join(self._storage_dir, filename)
            if not os.path.exists(filepath):
                raise TemplateNotFoundError(f"Template '{name}' with version '{version}' not found.")
            return TemplateLoader.from_json_file(filepath)

        # No version specified, load highest semantic version matching the name
        matching_files = self._get_matching_template_files(safe_name)
        if not matching_files:
            raise TemplateNotFoundError(f"Template with name '{name}' not found.")

        # Sort matching files by semver extracted from names
        # Filename pattern: {name}_v{version}.json
        latest_file = self._resolve_latest_semver_file(matching_files)
        filepath = os.path.join(self._storage_dir, latest_file)
        return TemplateLoader.from_json_file(filepath)

    def list_templates(self, category: Optional[str] = None, provider: Optional[str] = None) -> List[PromptTemplate]:
        """Scans the repository folder and returns all parsed templates, optionally filtered."""
        templates = []
        try:
            for file in os.listdir(self._storage_dir):
                if file.endswith(".json"):
                    filepath = os.path.join(self._storage_dir, file)
                    try:
                        tpl = TemplateLoader.from_json_file(filepath)
                        # Check filters
                        if category and tpl.category != category:
                            continue
                        if provider and tpl.provider != provider:
                            continue
                        templates.append(tpl)
                    except Exception as parse_err:
                        logger.warning(f"Skipping corrupt template file '{file}': {parse_err}")
        except Exception as e:
            raise StorageError(f"Failed to list templates in directory: {e}") from e

        return templates

    def delete_template(self, name: str, version: Optional[str] = None) -> bool:
        """Deletes a specific template file or all version files associated with the template name."""
        safe_name = self._sanitize_filename(name)
        
        if version:
            safe_version = self._sanitize_filename(version)
            filename = f"{safe_name}_v{safe_version}.json"
            filepath = os.path.join(self._storage_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted template: {name} (v{version})")
                return True
            return False

        # If no version specified, wipe all versions
        matching_files = self._get_matching_template_files(safe_name)
        if not matching_files:
            return False

        for file in matching_files:
            filepath = os.path.join(self._storage_dir, file)
            os.remove(filepath)
        logger.info(f"Wiped all versions ({len(matching_files)}) for template: {name}")
        return True

    def seed_default_templates(self) -> None:
        """Populates default templates if the repository folder contains zero .json configurations."""
        existing_jsons = [f for f in os.listdir(self._storage_dir) if f.endswith(".json")]
        if existing_jsons:
            return

        logger.info("No templates found on disk. Seeding default configurations...")
        for default_dict in DEFAULT_TEMPLATES:
            try:
                tpl = TemplateLoader.from_dict(default_dict)
                self.save_template(tpl)
            except Exception as e:
                logger.error(f"Failed to seed default template '{default_dict.get('name')}': {e}")

    def _sanitize_filename(self, text: str) -> str:
        """Secures a string so it does not contain system separator keywords or path navigation markers."""
        return re.sub(r"[^a-zA-Z0-9_\-\.]", "_", text)

    def _get_matching_template_files(self, sanitized_name: str) -> List[str]:
        """Returns all JSON files starting with {sanitized_name}_v."""
        try:
            files = os.listdir(self._storage_dir)
            # Match specifically: sanitized_name_v{version}.json
            pattern = re.compile(rf"^{re.escape(sanitized_name)}_v[\d\.\-_]+\.json$")
            return [f for f in files if pattern.match(f)]
        except Exception:
            return []

    def _resolve_latest_semver_file(self, file_list: List[str]) -> str:
        """Sorts filenames based on parsed semantic version strings and returns the highest."""
        def parse_version(filename: str) -> List[int]:
            # Extract portion between "_v" and ".json"
            match = re.search(r"_v([\d\.]+.*?)\.json$", filename)
            if not match:
                return [0, 0, 0]
            version_str = match.group(1)
            # Extract digits as list of ints for proper semver sorting (e.g. 1.10 > 1.2)
            digits = [int(x) for x in re.findall(r"\d+", version_str)]
            return digits if digits else [0, 0, 0]

        return max(file_list, key=parse_version)
