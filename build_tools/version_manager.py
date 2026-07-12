"""Version manager for Module 15 release engineering.

This module provides semantic version parsing, validation, comparison, Windows version
string generation, and metadata output for AI Marketing Studio PRO release pipeline.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

from build_tools.build_models import ReleaseChannel, VersionInformation
from build_tools.exceptions import InvalidVersionError, VersionFileError


class VersionManager:
    """Manages application semantic versioning and release channel checks.

    This class serves as the single source of truth for loading, parsing, validating,
    comparing, and formatting product versions. It also supports exporting metadata
    necessary for Windows executable properties.
    """

    # Strict Semantic Versioning 2.0.0 Regex
    SEMVER_REGEX = re.compile(
        r"^(?P<major>0|[1-9]\d*)\."
        r"(?P<minor>0|[1-9]\d*)\."
        r"(?P<patch>0|[1-9]\d*)"
        r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
        r"(?:\+(?P<build_metadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )

    def __init__(self, version_file_path: Optional[Path] = None) -> None:
        """Initializes the VersionManager.

        Args:
            version_file_path: Optional custom path to the master version source file (e.g. VERSION).
                               Defaults to a "VERSION" file in the project root if not specified.
        """
        if version_file_path is None:
            # Fallback to standard VERSION file in current directory or project root
            self.version_file_path = Path("VERSION")
        else:
            self.version_file_path = Path(version_file_path)

    def parse_version_string(self, version_str: str) -> VersionInformation:
        """Parses a raw semantic version string into a VersionInformation dataclass.

        Args:
            version_str: Raw version string (e.g. '1.3.0-beta.2+build.45').

        Returns:
            A populated VersionInformation object.

        Raises:
            InvalidVersionError: If the version string fails semver pattern validation.
        """
        match = self.SEMVER_REGEX.match(version_str.strip())
        if not match:
            raise InvalidVersionError(
                f"Version string '{version_str}' is not a valid Semantic Version 2.0.0."
            )

        group_dict = match.groupdict()
        try:
            return VersionInformation(
                major=int(group_dict["major"]),
                minor=int(group_dict["minor"]),
                patch=int(group_dict["patch"]),
                prerelease=group_dict.get("prerelease"),
                build_metadata=group_dict.get("build_metadata"),
            )
        except Exception as err:
            raise InvalidVersionError(f"Failed parsing version components: {err}") from err

    def read_version_from_file(self) -> VersionInformation:
        """Reads and parses the version string from the master version file.

        Returns:
            The parsed VersionInformation.

        Raises:
            VersionFileError: If reading the version file fails.
            InvalidVersionError: If the file contains an invalid version string.
        """
        if not self.version_file_path.exists():
            # If it doesn't exist, we default to 1.0.0-dev for safety and local testing
            try:
                self.write_version_to_file(self.parse_version_string("1.0.0-dev"))
            except Exception as err:
                raise VersionFileError(f"Master version file not found at {self.version_file_path} and failed to create default: {err}") from err

        try:
            content = self.version_file_path.read_text(encoding="utf-8").strip()
        except OSError as err:
            raise VersionFileError(f"Failed reading master version file at {self.version_file_path}: {err}") from err

        # Extract only the first non-empty line
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]
        if not lines:
            raise InvalidVersionError(f"Master version file {self.version_file_path} is empty.")

        return self.parse_version_string(lines[0])

    def write_version_to_file(self, version: Union[str, VersionInformation]) -> None:
        """Writes/updates the master version file with the specified version.

        Args:
            version: Either a VersionInformation object or a semver string.

        Raises:
            VersionFileError: If updating the file fails.
        """
        version_str = str(version)
        try:
            self.version_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.version_file_path.write_text(f"{version_str}\n", encoding="utf-8")
        except OSError as err:
            raise VersionFileError(f"Failed writing version '{version_str}' to file {self.version_file_path}: {err}") from err

    def get_current_version(self) -> VersionInformation:
        """Implements the VersionProvider protocol requirement.

        Returns:
            The current active product VersionInformation.
        """
        return self.read_version_from_file()

    def validate_channel_compatibility(
        self, version: VersionInformation, channel: ReleaseChannel
    ) -> None:
        """Ensures the version tags correspond correctly with the selected ReleaseChannel.

        Rules:
            - Stable channel releases must NOT contain pre-release identifiers (e.g. no -beta, -rc, -dev).
            - Beta channel releases must have a pre-release identifier containing 'beta' or 'rc'.
            - Development channel releases typically contain 'dev', 'alpha', or 'build'.

        Args:
            version: The VersionInformation to evaluate.
            channel: Target release channel.

        Raises:
            InvalidVersionError: If the version tag mismatch violates release rules.
        """
        pre = version.prerelease
        if channel == ReleaseChannel.STABLE:
            if pre is not None:
                raise InvalidVersionError(
                    f"Stable channel releases cannot contain a pre-release label: '{pre}'"
                )
        elif channel == ReleaseChannel.BETA:
            if pre is None:
                raise InvalidVersionError(
                    "Beta release channel requires a pre-release identifier (e.g. -beta.1)."
                )
            if not any(token in pre.lower() for token in ["beta", "rc"]):
                raise InvalidVersionError(
                    f"Beta channel releases must have 'beta' or 'rc' in pre-release tag, got: '{pre}'"
                )
        elif channel == ReleaseChannel.DEVELOPMENT:
            if pre is None:
                raise InvalidVersionError(
                    "Development release channel requires a pre-release identifier (e.g. -dev)."
                )

    def generate_windows_file_version(self, version: VersionInformation) -> str:
        """Generates a strictly numeric four-part version string for Windows file property resources.

        Windows demands versioning in the format: Major.Minor.Patch.Build (e.g. 1.2.3.0).

        Args:
            version: The VersionInformation source.

        Returns:
            A strictly formatted 'A.B.C.D' numeric string.
        """
        # Parse build number if embedded in build metadata or pre-release, default to 0
        build_val = 0
        if version.build_metadata:
            # Try to extract the first numeric component found in metadata
            nums = re.findall(r"\d+", version.build_metadata)
            if nums:
                build_val = int(nums[0])
        elif version.prerelease:
            # Try to extract numbers from prerelease labels (e.g. rc1 -> 1)
            nums = re.findall(r"\d+", version.prerelease)
            if nums:
                build_val = int(nums[0])

        return f"{version.major}.{version.minor}.{version.patch}.{build_val}"

    def generate_windows_product_version(self, version: VersionInformation) -> str:
        """Generates the Windows Product Version.

        This is usually the full canonical string including prerelease labels.

        Args:
            version: The VersionInformation source.

        Returns:
            String representation of the full version.
        """
        return str(version)

    def generate_windows_display_version(self, version: VersionInformation) -> str:
        """Generates a user-friendly product version string with clean formatting.

        Args:
            version: The VersionInformation source.

        Returns:
            User friendly display string (e.g. '1.3.0 (Beta 2)').
        """
        display = f"{version.major}.{version.minor}.{version.patch}"
        if version.prerelease:
            # Capitalize common pre-releases (e.g. rc1 -> RC1, beta.2 -> Beta 2)
            label = version.prerelease.replace(".", " ").title()
            display += f" ({label})"
        return display

    def generate_build_number(self, version: VersionInformation) -> int:
        """Generates a numeric build integer representing current iteration.

        Args:
            version: The VersionInformation source.

        Returns:
            The build number.
        """
        # Look for numbers in build metadata, fallback to prerelease numbers, fallback to 0
        if version.build_metadata:
            nums = re.findall(r"\d+", version.build_metadata)
            if nums:
                return int(nums[0])
        if version.prerelease:
            nums = re.findall(r"\d+", version.prerelease)
            if nums:
                return int(nums[0])
        return 0

    def generate_metadata_file(
        self,
        version: VersionInformation,
        channel: ReleaseChannel,
        output_path: Path,
        builder_name: str = "local_builder",
    ) -> Path:
        """Generates a complete version metadata JSON file for diagnostic logging and installer packaging.

        Args:
            version: Target version.
            channel: Target release channel.
            output_path: Destination path for writing the JSON.
            builder_name: Compilation operator identifier.

        Returns:
            Path to the written metadata file.

        Raises:
            VersionFileError: If writing to the destination path fails.
        """
        metadata = {
            "application": "AI Marketing Studio PRO",
            "version_string": str(version),
            "major": version.major,
            "minor": version.minor,
            "patch": version.patch,
            "prerelease": version.prerelease,
            "build_metadata": version.build_metadata,
            "release_channel": channel.value,
            "windows_file_version": self.generate_windows_file_version(version),
            "windows_product_version": self.generate_windows_product_version(version),
            "windows_display_version": self.generate_windows_display_version(version),
            "build_number": self.generate_build_number(version),
            "builder": builder_name,
            "timestamp": datetime.now().astimezone().isoformat(),
        }

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as file:
                json.dump(metadata, file, indent=4)
            return output_path
        except OSError as err:
            raise VersionFileError(
                f"Failed writing version metadata file to {output_path}: {err}"
            ) from err

    def compare_versions(self, v1: VersionInformation, v2: VersionInformation) -> int:
        """Compares two VersionInformation objects.

        Args:
            v1: First VersionInformation.
            v2: Second VersionInformation.

        Returns:
            -1 if v1 < v2
             0 if v1 == v2
             1 if v1 > v2
        """
        # Compare major, minor, patch
        if v1.major != v2.major:
            return 1 if v1.major > v2.major else -1
        if v1.minor != v2.minor:
            return 1 if v1.minor > v2.minor else -1
        if v1.patch != v2.patch:
            return 1 if v1.patch > v2.patch else -1

        # Prerelease tag comparison (SemVer 2.0 rules: stable is higher than prerelease)
        if v1.prerelease is None and v2.prerelease is not None:
            return 1  # stable > prerelease
        if v1.prerelease is not None and v2.prerelease is None:
            return -1  # prerelease < stable
        if v1.prerelease is None and v2.prerelease is None:
            return 0

        # Both have prerelease tags, perform component-by-component comparison
        p1_parts = v1.prerelease.split(".")
        p2_parts = v2.prerelease.split(".")
        for p1, p2 in zip(p1_parts, p2_parts):
            p1_is_num = p1.isdigit()
            p2_is_num = p2.isdigit()
            if p1_is_num and p2_is_num:
                n1, n2 = int(p1), int(p2)
                if n1 != n2:
                    return 1 if n1 > n2 else -1
            elif not p1_is_num and not p2_is_num:
                if p1 != p2:
                    return 1 if p1 > p2 else -1
            else:
                # Numeric identifiers always have lower precedence than non-numeric identifiers
                return -1 if p1_is_num else 1

        # If all compared parts match, the version with more prerelease elements has higher precedence
        if len(p1_parts) != len(p2_parts):
            return 1 if len(p1_parts) > len(p2_parts) else -1

        return 0
