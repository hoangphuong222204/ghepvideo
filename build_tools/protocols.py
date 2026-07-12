"""Stable contracts using typing.Protocol for Module 15 release engineering framework.

This module defines the dependency interfaces for the build, packaging, and update tools,
ensuring decoupling and testability of each component.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from build_tools.build_models import (
    ArtifactChecksum,
    ArtifactSignature,
    BuildArtifact,
    BuildConfiguration,
    BuildResult,
    BundledDependency,
    InstallerResult,
    PortableResult,
    ReleaseManifest,
    ReleaseValidationReport,
    ResourceDefinition,
    VersionInformation,
)


@runtime_checkable
class Logger(Protocol):
    """Protocol for logging subsystem integration."""

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with DEBUG severity."""
        ...

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with INFO severity."""
        ...

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with WARNING severity."""
        ...

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a message with ERROR severity."""
        ...

    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an exception message with ERROR severity containing traceback."""
        ...


@runtime_checkable
class ConfigurationProvider(Protocol):
    """Protocol for configuration retrieval."""

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a raw configuration value by key."""
        ...

    def get_string(self, key: str, default: str = "") -> str:
        """Retrieve a configuration value as a string."""
        ...

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Retrieve a configuration value as a boolean."""
        ...

    def get_int(self, key: str, default: int = 0) -> int:
        """Retrieve a configuration value as an integer."""
        ...


@runtime_checkable
class ClockProvider(Protocol):
    """Protocol for timezone-aware temporal tracking."""

    def now(self) -> datetime:
        """Return the current timezone-aware datetime."""
        ...


@runtime_checkable
class IDProvider(Protocol):
    """Protocol for unique identifier generation."""

    def generate_id(self, prefix: Optional[str] = None) -> str:
        """Generate a cryptographically safe or unique identifier string."""
        ...


@runtime_checkable
class CommandRunner(Protocol):
    """Protocol for executing host subprocess tasks safely."""

    def run_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        timeout_seconds: Optional[float] = None,
    ) -> tuple[int, str, str]:
        """Runs a host subprocess command and captures its output.

        Args:
            args: Command arguments list.
            cwd: Optional execution directory.
            env: Optional environment dictionary overrides.
            timeout_seconds: Optional watchdog execution timeout.

        Returns:
            A tuple of (exit_code, stdout_text, stderr_text).
        """
        ...


@runtime_checkable
class FilesystemProvider(Protocol):
    """Protocol wrapping OS filesystem mutations for deterministic unit mocking."""

    def exists(self, path: Path) -> bool:
        """Check if a path exists on disk."""
        ...

    def is_file(self, path: Path) -> bool:
        """Check if a path points to a file."""
        ...

    def is_dir(self, path: Path) -> bool:
        """Check if a path points to a directory."""
        ...

    def create_dir(self, path: Path, exist_ok: bool = True) -> None:
        """Recursively create a directory structure."""
        ...

    def remove_file(self, path: Path) -> None:
        """Remove a file from disk."""
        ...

    def remove_dir(self, path: Path, recursive: bool = False) -> None:
        """Remove a directory structure from disk."""
        ...

    def copy_file(self, source: Path, destination: Path) -> None:
        """Copy a file atomically to a new destination."""
        ...

    def move_file(self, source: Path, destination: Path) -> None:
        """Move a file atomically to a new destination."""
        ...

    def write_text(self, path: Path, text: str, encoding: str = "utf-8") -> None:
        """Write content text safely to a file."""
        ...

    def read_text(self, path: Path, encoding: str = "utf-8") -> str:
        """Read content text safely from a file."""
        ...

    def list_dir(self, path: Path) -> List[Path]:
        """List all entries in a directory."""
        ...


@runtime_checkable
class VersionProvider(Protocol):
    """Protocol for reading target release versions."""

    def get_current_version(self) -> VersionInformation:
        """Retrieve the current product version from the master version source of truth."""
        ...


@runtime_checkable
class ResourceResolver(Protocol):
    """Protocol for locating and normalizing static application resources."""

    def resolve_resources(self, config: BuildConfiguration) -> List[ResourceDefinition]:
        """Locates and maps static assets for inclusion in frozen packages.

        Args:
            config: Unified build configuration settings.

        Returns:
            A list of validated resource definitions.
        """
        ...


@runtime_checkable
class DependencyCollector(Protocol):
    """Protocol for discovering hidden Python imports, shared libraries, and DLL dependencies."""

    def collect_dependencies(self, config: BuildConfiguration) -> List[BundledDependency]:
        """Scans the source workspace and Python env to collect hidden imports and binaries.

        Args:
            config: Unified build configuration settings.

        Returns:
            A list of gathered package and binary metadata.
        """
        ...


@runtime_checkable
class ExecutableBuilder(Protocol):
    """Protocol for building frozen Windows executables (using PyInstaller)."""

    def build_executable(
        self,
        config: BuildConfiguration,
        resources: List[ResourceDefinition],
        dependencies: List[BundledDependency],
    ) -> BuildResult:
        """Invokes PyInstaller to build a frozen executable package.

        Args:
            config: Unified build configuration settings.
            resources: Validated list of resource definitions to embed.
            dependencies: Python library dependencies and system binaries to bundle.

        Returns:
            The outcome BuildResult object.
        """
        ...


@runtime_checkable
class InstallerBuilder(Protocol):
    """Protocol for assembling a setup installer compiler package (using Inno Setup)."""

    def build_installer(
        self, config: BuildConfiguration, build_result: BuildResult
    ) -> InstallerResult:
        """Invokes Inno Setup compiler to assemble a setup installation executable.

        Args:
            config: Unified build configuration settings.
            build_result: The results of the frozen executable compilation step.

        Returns:
            The outcome InstallerResult object.
        """
        ...


@runtime_checkable
class PortableBuilder(Protocol):
    """Protocol for bundling portable ZIP archives."""

    def build_portable(
        self, config: BuildConfiguration, build_result: BuildResult
    ) -> PortableResult:
        """Packages the frozen executable distribution into a portable ZIP archive.

        Args:
            config: Unified build configuration settings.
            build_result: The results of the frozen executable compilation step.

        Returns:
            The outcome PortableResult object.
        """
        ...


@runtime_checkable
class ArtifactManager(Protocol):
    """Protocol tracking build outputs, hashes, and staging areas."""

    def create_release_workspace(self, version: VersionInformation) -> Path:
        """Initializes a clean staging workspace folder for assembling the release artifacts.

        Args:
            version: The release version to namespace the workspace with.

        Returns:
            Path pointing to the staging directory.
        """
        ...

    def track_artifact(self, artifact: BuildArtifact) -> None:
        """Registers a produced build artifact into the release tracking session."""
        ...

    def get_artifact(self, artifact_id: str) -> Optional[BuildArtifact]:
        """Retrieves a tracked artifact by its unique identifier."""
        ...

    def list_artifacts(self) -> List[BuildArtifact]:
        """Lists all registered artifacts tracked in this release session."""
        ...

    def clean_incomplete_artifacts(self) -> None:
        """Removes un-finalized or corrupted artifacts in the active workspace."""
        ...


@runtime_checkable
class ChecksumProvider(Protocol):
    """Protocol for calculating and validating SHA-256/SHA-512 hashes."""

    def calculate_checksum(self, file_path: Path) -> ArtifactChecksum:
        """Computes SHA-256 and SHA-512 hashes for a physical file.

        Args:
            file_path: Target path on disk.

        Returns:
            An ArtifactChecksum object containing the hash hex strings.
        """
        ...

    def verify_checksum(self, file_path: Path, expected: ArtifactChecksum) -> bool:
        """Compares calculated checksum of a file with the expected checksum.

        Args:
            file_path: Target path on disk.
            expected: The expected checksum object.

        Returns:
            True if the checksum matches, False otherwise.
        """
        ...


@runtime_checkable
class SignatureProvider(Protocol):
    """Protocol for code-signing executable binaries and updates."""

    def sign_file(self, file_path: Path) -> ArtifactSignature:
        """Applies digital signature to a file using code-signing credentials.

        Args:
            file_path: Target path on disk.

        Returns:
            The generated or verified ArtifactSignature object.
        """
        ...

    def verify_signature(self, file_path: Path) -> ArtifactSignature:
        """Checks the digital signature authenticity of a physical file.

        Args:
            file_path: Target path on disk.

        Returns:
            The verified ArtifactSignature object status.
        """
        ...


@runtime_checkable
class ManifestBuilder(Protocol):
    """Protocol for serializing stable update description documents."""

    def build_manifest(
        self,
        config: BuildConfiguration,
        artifacts: List[BuildArtifact],
        validation_report: ReleaseValidationReport,
    ) -> ReleaseManifest:
        """Assembles a release manifest object listing all release details and artifacts.

        Args:
            config: Unified build configuration settings.
            artifacts: Tracked artifacts list.
            validation_report: The final release validation report.

        Returns:
            The compiled ReleaseManifest object.
        """
        ...


@runtime_checkable
class ReleaseValidator(Protocol):
    """Protocol for running release sanity checks."""

    def validate_release(
        self, config: BuildConfiguration, artifacts: List[BuildArtifact]
    ) -> ReleaseValidationReport:
        """Performs safety checks verifying the integrity and security of the release workspace.

        Args:
            config: Unified build configuration settings.
            artifacts: Assembled list of release artifacts to evaluate.

        Returns:
            A ReleaseValidationReport documenting warnings or errors.
        """
        ...


@runtime_checkable
class ReleasePublisher(Protocol):
    """Protocol for uploading release artifacts and manifests to production CDNs."""

    def publish_release(
        self, manifest: ReleaseManifest, artifacts: List[BuildArtifact]
    ) -> None:
        """Publishes the validated release manifest and its artifacts to a distribution target.

        Args:
            manifest: The validated update release manifest.
            artifacts: Assembled list of release artifacts.
        """
        ...
