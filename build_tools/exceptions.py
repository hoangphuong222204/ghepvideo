"""Exception hierarchy for Module 15: Build, Packaging, Installer, Auto Update, and Release.

This module defines all custom exceptions raised during the build process, packaging,
installer generation, and release artifact validation of AI Marketing Studio PRO.
"""

class BuildToolError(Exception):
    """Base exception for all errors in the build and release tools (Module 15)."""
    pass


class BuildConfigurationError(BuildToolError):
    """Raised when there is an invalid or incomplete build configuration."""
    pass


class InvalidBuildEnvironmentError(BuildToolError):
    """Raised when the host environment is unsuitable or missing build requirements."""
    pass


class UnsupportedPlatformError(BuildToolError):
    """Raised when the target or current operating system is not supported."""
    pass


class UnsupportedArchitectureError(BuildToolError):
    """Raised when the CPU architecture is unsupported."""
    pass


class VersionError(BuildToolError):
    """Base exception for all application versioning failures."""
    pass


class InvalidVersionError(VersionError):
    """Raised when a version string fails semantic version parsing or validation rules."""
    pass


class VersionFileError(VersionError):
    """Raised when reading, updating, or writing version source files fails."""
    pass


class ResourceError(BuildToolError):
    """Base exception for all asset and resources resolving failures."""
    pass


class MissingResourceError(ResourceError):
    """Raised when a required application asset or file resource is not found."""
    pass


class DependencyCollectionError(BuildToolError):
    """Raised when parsing or bundling third-party dependencies fails."""
    pass


class BundledDependencyError(DependencyCollectionError):
    """Raised when a compiled/bundled dependency exhibits incompatibilities or missing components."""
    pass


class PyInstallerError(BuildToolError):
    """Base exception for PyInstaller operations."""
    pass


class ExecutableBuildFailureError(PyInstallerError):
    """Raised when compilation of the standalone Windows executable fails."""
    pass


class PortableBuildFailureError(BuildToolError):
    """Raised when packaging the portable distribution archive fails."""
    pass


class InstallerBuildFailureError(BuildToolError):
    """Raised when compilation of the Windows installer fails."""
    pass


class InnoSetupNotFoundError(InstallerBuildFailureError):
    """Raised when Inno Setup command-line compiler is not found in the system."""
    pass


class ArtifactError(BuildToolError):
    """Base exception for all produced release artifact failures."""
    pass


class ChecksumError(ArtifactError):
    """Raised when generating or verifying an artifact checksum fails."""
    pass


class SignatureError(ArtifactError):
    """Base exception for all digital and code signature failures."""
    pass


class CodeSigningError(SignatureError):
    """Raised when signing or verifying a Windows executable or installer fails."""
    pass


class ManifestGenerationError(BuildToolError):
    """Raised when building or validating the release update manifest fails."""
    pass


class ReleaseValidationError(BuildToolError):
    """Raised when final release validation fails due to broken or missing requirements."""
    pass


class ReleaseCreationError(BuildToolError):
    """Raised when the high-level release manager fails to assemble the release artifacts."""
    pass


class ReleasePublishingError(BuildToolError):
    """Raised when publishing release artifacts to a distribution target fails."""
    pass


class CleanupError(BuildToolError):
    """Raised when cleaning temporary build and distribution workspaces fails."""
    pass


class RuntimeValidationError(BuildToolError):
    """Raised when post-build sanity checks or startup dry-runs of the produced executable fail."""
    pass
