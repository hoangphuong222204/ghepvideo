"""Strongly typed build and release domain models for Module 15: Release Engineering.

This module provides all Enums and Dataclasses representing build configurations,
compilation settings, dependency assets, artifacts, checksums, signatures, manifests,
and validation reports for AI Marketing Studio PRO.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from build_tools.exceptions import BuildConfigurationError


class BuildType(str, Enum):
    """The distribution package form factor."""
    PORTABLE = "portable"
    INSTALLER = "installer"
    EXE_ONLY = "exe_only"


class BuildMode(str, Enum):
    """Compilation profiling mode."""
    DEBUG = "debug"
    RELEASE = "release"
    DEVELOPMENT = "development"


class ReleaseChannel(str, Enum):
    """Target audience stream for update distribution."""
    STABLE = "stable"
    BETA = "beta"
    DEVELOPMENT = "development"


class OperatingSystem(str, Enum):
    """Target platform identifier."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"


class CPUArchitecture(str, Enum):
    """Target processor instruction set."""
    X86_64 = "x86_64"
    ARM64 = "arm64"


class ArtifactType(str, Enum):
    """Categorization of compiled files in the release bundle."""
    EXECUTABLE = "executable"
    PORTABLE_ZIP = "portable_zip"
    INSTALLER_EXE = "installer_exe"
    MANIFEST_JSON = "manifest_json"
    CHECKSUM_TXT = "checksum_txt"
    SIGNATURE_DETACHED = "signature_detached"


class SignatureStatus(str, Enum):
    """Signing status check result."""
    UNSIGNED = "unsigned"
    SIGNED_VALID = "signed_valid"
    SIGNED_INVALID = "signed_invalid"
    UNKNOWN = "unknown"


class ValidationStatus(str, Enum):
    """Result of release verification suite."""
    PASSED = "passed"
    FAILED = "failed"
    PASSED_WITH_WARNINGS = "passed_with_warnings"


class BuildStatus(str, Enum):
    """Ultimate compile status code."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


# Helper function to ensure timezone-aware UTC datetime objects
def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class VersionInformation:
    """Semantic version details modeling the product version state.

    Attributes:
        major: Increment on breaking public API changes.
        minor: Increment on backwards-compatible feature additions.
        patch: Increment on backwards-compatible bug fixes.
        prerelease: Optional label for unstable iterations (e.g. 'rc1').
        build_metadata: Optional label for environment metadata.
    """
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build_metadata: Optional[str] = None

    def __post_init__(self) -> None:
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise BuildConfigurationError("Semantic version parts must be non-negative integers.")

    def __str__(self) -> str:
        ver = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            ver += f"-{self.prerelease}"
        if self.build_metadata:
            ver += f"+{self.build_metadata}"
        return ver


@dataclass(frozen=True)
class BuildMetadata:
    """Diagnostic compiling tracing stamps accompanying a frozen executable.

    Attributes:
        build_id: Unique build tracking identifier.
        builder_name: Environment username or automated runner ID.
        vcs_commit_hash: Git hash representing source revision.
        vcs_branch: Git branch name.
        python_version: Host python version compilation run (e.g. '3.11.4').
        pyinstaller_version: Host PyInstaller framework version.
        is_reproducible: True if sources and environment ensure deterministic outputs.
        built_at: Time compile sequence finished.
    """
    build_id: str
    builder_name: str
    vcs_commit_hash: Optional[str] = None
    vcs_branch: Optional[str] = None
    python_version: str = field(default_factory=lambda: "3.11")
    pyinstaller_version: str = field(default_factory=lambda: "6.0")
    is_reproducible: bool = False
    built_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "built_at", _ensure_utc(self.built_at))


@dataclass(frozen=True)
class PyInstallerConfiguration:
    """PyInstaller-specific pipeline parameters.

    Attributes:
        spec_path: Path to the SPEC build descriptor file.
        one_file: Package all binaries into a single executable if True (default is False, one-dir).
        console: Show the terminal console window on app startup.
        hidden_imports: Custom dependencies list that PyInstaller AST parser missed.
        data_files: Non-code static files to bundle into the execution directory.
        binary_files: compiled DLLs or executables to bundle.
        excludes: Packages explicitly stripped from compilation workspace.
    """
    spec_path: Path
    one_file: bool = False
    console: bool = False
    hidden_imports: List[str] = field(default_factory=list)
    data_files: List[tuple[str, str]] = field(default_factory=list)
    binary_files: List[tuple[str, str]] = field(default_factory=list)
    excludes: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class InstallerConfiguration:
    """Inno Setup script compiler configuration settings.

    Attributes:
        iss_path: Path pointing to the ISS compilation instructions.
        output_name: Descriptive setup output file name template.
        publisher_name: Organization label displayed in Windows setup alerts.
        app_url: Help link displayed in setup menus.
        default_dir_name: Program path template.
        silent_switch: Command line argument for un-prompted setup.
        uninstaller_silent_switch: Command line argument for un-prompted removal.
    """
    iss_path: Path
    output_name: str = "AI-Marketing-Studio-PRO-Setup"
    publisher_name: str = "AI Marketing Studio Corporation"
    app_url: str = "https://ai.studio/build"
    default_dir_name: str = "{userappdata}\\Programs\\AI Marketing Studio PRO"
    silent_switch: str = "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART"
    uninstaller_silent_switch: str = "/SILENT /SUPPRESSMSGBOXES /NORESTART"


@dataclass(frozen=True)
class PortableConfiguration:
    """Portable zip package packaging parameters.

    Attributes:
        archive_name: Template ZIP file target.
        include_readme: Automatically bundle release notes or usage manual.
        portable_mode_marker: Filename indicating a local registry-free app setting mode.
    """
    archive_name: str = "AI-Marketing-Studio-PRO-Portable"
    include_readme: bool = True
    portable_mode_marker: str = "portable.txt"


@dataclass(frozen=True)
class BuildConfiguration:
    """Unified release pipeline parameters config.

    Attributes:
        project_root: Workspace directory parent root.
        source_root: Main code workspace parent directory.
        entry_point: Python script starting the application (e.g. 'src/main.py').
        app_name: Visual product identifier.
        version: Application target version.
        build_mode: Profiling mode selector.
        release_channel: Release stream target.
        target_os: Platform OS target.
        target_arch: Platform CPU target.
        output_dir: Target path to dump compiled products.
        temp_dir: Path to compile temporary scratchpads.
        icon_path: Path pointing to visual EXE graphic (.ico).
        manifest_path: Path pointing to application manifest configuration.
        version_resource_path: Path pointing to Windows version file.
        pyinstaller_config: Compilation directives.
        installer_config: Packaging directives.
        portable_config: Zip packaging directives.
        ffmpeg_bin_dir: Path to directory containing local ffmpeg builds.
        include_fish_speech_models: Bundling model weights flag.
        runtime_profile: GPU runtime compatibility profile ("cpu_only" vs. "cuda_enabled").
        enable_code_signing: Code signature enforcement flag.
        enable_manifest_signing: Detached update manifest signature enforcement flag.
        clean_before_build: Recreate build dirs.
    """
    project_root: Path
    source_root: Path
    entry_point: Path
    app_name: str
    version: VersionInformation
    build_mode: BuildMode
    release_channel: ReleaseChannel
    target_os: OperatingSystem
    target_arch: CPUArchitecture
    output_dir: Path
    temp_dir: Path
    icon_path: Path
    manifest_path: Path
    version_resource_path: Path
    pyinstaller_config: PyInstallerConfiguration
    installer_config: InstallerConfiguration
    portable_config: PortableConfiguration
    ffmpeg_bin_dir: Optional[Path] = None
    include_fish_speech_models: bool = False
    runtime_profile: str = "cpu_only"
    enable_code_signing: bool = False
    enable_manifest_signing: bool = False
    clean_before_build: bool = True

    def __post_init__(self) -> None:
        if not self.app_name.strip():
            raise BuildConfigurationError("app_name cannot be empty inside BuildConfiguration.")


@dataclass(frozen=True)
class ResourceDefinition:
    """Models a non-code static asset file bundled into frozen executable resources.

    Attributes:
        resource_id: Stable resource identifier.
        source_path: Real file path on developer host machine.
        target_relative_path: Extracted relative path inside frozen package resources.
        is_required: False if resource absence is non-fatal for execution.
    """
    resource_id: str
    source_path: Path
    target_relative_path: Path
    is_required: bool = True


@dataclass(frozen=True)
class BundledDependency:
    """Details identifying a third-party DLL, model binary, or external library packed inside frozen outputs.

    Attributes:
        dependency_name: package or binary name (e.g. 'ffmpeg.exe').
        version: Version string.
        category: Library classification ('binary', 'python_package', 'model_weights').
        license_name: Legal copyright license identifier (e.g. 'GPL-3.0').
        license_file_path: Optional path to license notice file.
    """
    dependency_name: str
    version: str
    category: str
    license_name: str
    license_file_path: Optional[Path] = None


@dataclass(frozen=True)
class ArtifactChecksum:
    """Represents a computed security verification stamp for a compiled artifact.

    Attributes:
        sha256_hex: The 64-character lowercase SHA-256 string.
        sha512_hex: Optional 128-character lowercase SHA-512 string.
    """
    sha256_hex: str
    sha512_hex: Optional[str] = None

    def __post_init__(self) -> None:
        if len(self.sha256_hex) != 64:
            raise BuildConfigurationError("sha256_hex must be exactly 64 characters long.")
        if self.sha512_hex and len(self.sha512_hex) != 128:
            raise BuildConfigurationError("sha512_hex must be exactly 128 characters long.")


@dataclass(frozen=True)
class ArtifactSignature:
    """Authenticode digital signature details backing a release file.

    Attributes:
        status: Validation status of the signature.
        certificate_thumbprint: Hexadecimal thumbprint representing signee cert.
        signer_name: Common Name of the certificate owner.
        timestamp_authority: Time Stamp Authority url or identifier string.
        signed_at: Time of signature creation.
    """
    status: SignatureStatus
    certificate_thumbprint: Optional[str] = None
    signer_name: Optional[str] = None
    timestamp_authority: Optional[str] = None
    signed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.signed_at is not None:
            object.__setattr__(self, "signed_at", _ensure_utc(self.signed_at))


@dataclass(frozen=True)
class BuildArtifact:
    """Models a single product file compiled and packaged by the pipeline.

    Attributes:
        artifact_id: Unique asset identifier.
        artifact_type: File categorization.
        file_path: Path to the artifact on local disk.
        file_size_bytes: Real physical size in bytes.
        checksum: Verification checksums.
        signature: Signing metadata block.
    """
    artifact_id: str
    artifact_type: ArtifactType
    file_path: Path
    file_size_bytes: int
    checksum: ArtifactChecksum
    signature: ArtifactSignature

    def __post_init__(self) -> None:
        if self.file_size_bytes < 0:
            raise BuildConfigurationError("file_size_bytes must be non-negative.")


@dataclass(frozen=True)
class ReleaseManifestEntry:
    """A single artifact node serialized inside public update manifests.

    Attributes:
        artifact_id: Stable identifier matching build output.
        artifact_type: Classification string.
        filename: Physical output filename.
        download_url: CDN or server download path endpoint.
        file_size_bytes: Size on disk.
        sha256_checksum: Hexadecimal verification hash.
        signature_thumbprint: Visual signature check.
        silent_install_args: Recommended quiet setup CLI arguments if relevant.
        rollback_supported: Toggle indicating if rollback is safe.
    """
    artifact_id: str
    artifact_type: str
    filename: str
    download_url: str
    file_size_bytes: int
    sha256_checksum: str
    signature_thumbprint: Optional[str] = None
    silent_install_args: Optional[str] = None
    rollback_supported: bool = True


@dataclass(frozen=True)
class ReleaseManifest:
    """The root serializable data schema representing a published software update.

    Attributes:
        schema_version: Manifest layout format index (e.g. '1.0').
        app_id: Bound product tracking code.
        app_name: Visual product name.
        app_version: Version of this release update.
        release_channel: Active channel.
        published_at: Time stamp of publication.
        minimum_supported_version: Floor version restriction. Users below this must update.
        minimum_updater_version: Floor updater engine requirement index.
        mandatory_update: Flag forcing execution of update on clients.
        release_notes_markdown: Visual feature changelog log.
        supported_os: Platform compatibility.
        supported_architecture: CPU instruction compatibility.
        artifacts: List of file nodes.
    """
    schema_version: str
    app_id: str
    app_name: str
    app_version: str
    release_channel: str
    published_at: datetime
    minimum_supported_version: str
    minimum_updater_version: str
    mandatory_update: bool
    release_notes_markdown: str
    supported_os: str
    supported_architecture: str
    artifacts: List[ReleaseManifestEntry] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "published_at", _ensure_utc(self.published_at))

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest structure into serializable dictionary."""
        data = asdict(self)
        data["published_at"] = self.published_at.isoformat()
        return data


@dataclass(frozen=True)
class BuildWarning:
    """A non-fatal alert discovered during compilation or resource resolution."""
    code: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


@dataclass(frozen=True)
class BuildErrorInfo:
    """Exception tracking details compiled during a failed build step."""
    step_name: str
    message: str
    exception_class: str
    stack_trace: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


@dataclass(frozen=True)
class BuildResult:
    """Outcome report documenting standalone executable compilation results."""
    build_id: str
    status: BuildStatus
    app_version: VersionInformation
    build_mode: BuildMode
    release_channel: ReleaseChannel
    target_os: OperatingSystem
    target_arch: CPUArchitecture
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    executable_path: Optional[Path] = None
    distribution_directory: Optional[Path] = None
    metadata_path: Optional[Path] = None
    warnings: List[BuildWarning] = field(default_factory=list)
    error_info: Optional[BuildErrorInfo] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "started_at", _ensure_utc(self.started_at))
        object.__setattr__(self, "completed_at", _ensure_utc(self.completed_at))


@dataclass(frozen=True)
class InstallerResult:
    """Outcome report documenting Windows setup installer compilation results."""
    installer_path: Optional[Path]
    is_successful: bool
    duration_seconds: float
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass(frozen=True)
class PortableResult:
    """Outcome report documenting portable ZIP archive generation results."""
    portable_path: Optional[Path]
    is_successful: bool
    duration_seconds: float
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass(frozen=True)
class ReleaseValidationIssue:
    """A check failure discovered by the ReleaseValidator."""
    severity: str  # "error" or "warning"
    code: str
    message: str


@dataclass(frozen=True)
class ReleaseValidationReport:
    """Consolidated assessment report verifying integrity of final release outputs."""
    status: ValidationStatus
    issues: List[ReleaseValidationIssue] = field(default_factory=list)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "checked_at", _ensure_utc(self.checked_at))
        has_errors = any(issue.severity == "error" for issue in self.issues)
        if has_errors and self.status != ValidationStatus.FAILED:
            object.__setattr__(self, "status", ValidationStatus.FAILED)


@dataclass(frozen=True)
class ReleaseResult:
    """The terminal release result compiling all distributions and verification sidecars."""
    release_id: str
    app_version: VersionInformation
    release_channel: ReleaseChannel
    is_successful: bool
    executable_artifact: Optional[BuildArtifact] = None
    portable_artifact: Optional[BuildArtifact] = None
    installer_artifact: Optional[BuildArtifact] = None
    manifest_artifact: Optional[BuildArtifact] = None
    checksum_artifacts: List[BuildArtifact] = field(default_factory=list)
    validation_report: Optional[ReleaseValidationReport] = None
    release_directory: Optional[Path] = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: float = 0.0
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "started_at", _ensure_utc(self.started_at))
        object.__setattr__(self, "completed_at", _ensure_utc(self.completed_at))

    def to_dict(self) -> Dict[str, Any]:
        """Convert release result into serializable map structure."""
        data = asdict(self)
        data["app_version"] = str(self.app_version)
        data["release_channel"] = self.release_channel.value
        data["started_at"] = self.started_at.isoformat()
        data["completed_at"] = self.completed_at.isoformat()
        if self.release_directory:
            data["release_directory"] = str(self.release_directory)
        return data
