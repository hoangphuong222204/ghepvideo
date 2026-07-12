"""VersionManager for semantic version checking, incrementing, and template state transition mapping."""

import datetime
import re
from typing import List, Optional, Tuple
from src.prompt_engine.exceptions import VersionError
from src.prompt_engine.models import PromptTemplate, VersionInfo
from src.prompt_engine.constants import (
    VERSION_STABILITY_MODES,
    VERSION_STABILITY_ACTIVE,
    VERSION_STABILITY_DRAFT,
)
from src.logger.logger_manager import LoggerManager

logger = LoggerManager().get_logger("prompt_engine.version_manager")


class VersionManager:
    """Manages semantic version mutations, comparisons, and lifecycle state changes for prompt templates."""

    SEMVER_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([\w\.\-]+))?$")

    @classmethod
    def increment_version(cls, current_version: str, bump_type: str = "patch") -> str:
        """Increments a semver string.

        Args:
            current_version: Semantic version string (e.g. "1.4.2").
            bump_type: Increment type: "major", "minor", or "patch".

        Returns:
            The incremented semver string.
        """
        match = cls.SEMVER_PATTERN.match(current_version)
        if not match:
            # Fallback if invalid semver, start at 1.0.0
            logger.warning(f"Invalid semver string '{current_version}'. Resetting to '1.0.0'.")
            return "1.0.0"

        major, minor, patch, pre_release = match.groups()
        major_i, minor_i, patch_i = int(major), int(minor), int(patch)

        bump_type_clean = bump_type.strip().lower()

        if bump_type_clean == "major":
            major_i += 1
            minor_i = 0
            patch_i = 0
        elif bump_type_clean == "minor":
            minor_i += 1
            patch_i = 0
        elif bump_type_clean == "patch":
            patch_i += 1
        else:
            raise VersionError(
                f"Unsupported bump type '{bump_type}'. Supported are: 'major', 'minor', 'patch'."
            )

        new_version = f"{major_i}.{minor_i}.{patch_i}"
        if pre_release:
            new_version += f"-{pre_release}"

        return new_version

    @classmethod
    def create_new_version(
        cls,
        template: PromptTemplate,
        new_user_prompt: str,
        new_system_prompt: Optional[str] = None,
        new_developer_prompt: Optional[str] = None,
        author: str = "system",
        bump_type: str = "patch",
        change_description: str = "Updated template text",
    ) -> PromptTemplate:
        """Creates a new copy of a template, incrementing its version and logging the historical change."""
        if template.is_locked:
            raise VersionError(f"Cannot version-bump locked template '{template.name}'. Unlock it first.")

        # Compute next version string
        next_ver = cls.increment_version(template.version, bump_type)

        # Log current version in history record
        archive_info = VersionInfo(
            version=template.version,
            author=author,
            created_at=datetime.datetime.utcnow(),
            description=change_description,
            stability=template.metadata.get("stability", VERSION_STABILITY_DRAFT),
            change_log=f"Migrated from {template.version} to {next_ver}",
        )

        # Clone and update parameters
        import copy
        new_tpl = copy.deepcopy(template)
        new_tpl.version = next_ver
        new_tpl.user_prompt = new_user_prompt
        new_tpl.system_prompt = new_system_prompt
        new_tpl.developer_prompt = new_developer_prompt
        
        # Append to history stack
        new_tpl.version_history.append(archive_info)
        
        # New versions default to Draft
        new_tpl.metadata["stability"] = VERSION_STABILITY_DRAFT

        logger.info(f"Versioned template '{template.name}': {template.version} -> {next_ver}")
        return new_tpl

    @classmethod
    def set_stability(cls, template: PromptTemplate, stability: str) -> None:
        """Transitions template stability mode (Draft -> Candidate -> Active -> Deprecated)."""
        stability_clean = stability.strip().title()
        if stability_clean not in VERSION_STABILITY_MODES:
            raise VersionError(
                f"Invalid stability state '{stability}'. Must be one of {VERSION_STABILITY_MODES}"
            )

        template.metadata["stability"] = stability_clean
        logger.info(f"Set template '{template.name}' (v{template.version}) stability to: {stability_clean}")

    @classmethod
    def compare_versions(cls, ver_a: str, ver_b: str) -> int:
        """Compares two semver strings.

        Returns:
            -1 if ver_a < ver_b
             0 if ver_a == ver_b
             1 if ver_a > ver_b
        """
        match_a = cls.SEMVER_PATTERN.match(ver_a)
        match_b = cls.SEMVER_PATTERN.match(ver_b)

        if not match_a and not match_b:
            return 0
        if not match_a:
            return -1
        if not match_b:
            return 1

        parts_a = [int(x) for x in match_a.groups()[:3]]
        parts_b = [int(x) for x in match_b.groups()[:3]]

        for a, b in zip(parts_a, parts_b):
            if a < b:
                return -1
            elif a > b:
                return 1

        return 0
