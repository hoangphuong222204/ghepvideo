"""Exception hierarchy for Module 11: Project Manager.

This module defines all custom exceptions raised by the Project Manager,
covering project lifecycle, validation, asset management, serialization,
history, locking, and recovery.
"""

class ProjectManagerError(Exception):
    """Base exception class for all errors originating in the Project Manager (Module 11)."""
    pass


# Configuration & Request Validation Errors
class ProjectConfigError(ProjectManagerError):
    """Raised when there is an invalid configuration for the Project Manager."""
    pass


class InvalidProjectRequestError(ProjectManagerError):
    """Raised when a project operation request is malformed or invalid."""
    pass


class InvalidProjectNameError(InvalidProjectRequestError):
    """Raised when a project name does not meet requirements (e.g. empty, invalid characters)."""
    pass


class InvalidProjectPathError(InvalidProjectRequestError):
    """Raised when a specified project or workspace path is invalid or unsafe."""
    pass


# Lifecycle Errors
class ProjectNotFoundError(ProjectManagerError):
    """Raised when the specified project cannot be found."""
    pass


class ProjectAlreadyExistsError(ProjectManagerError):
    """Raised when trying to create a project at a location where one already exists."""
    pass


class ProjectOpenError(ProjectManagerError):
    """Raised when a project fails to open."""
    pass


class ProjectSaveError(ProjectManagerError):
    """Raised when a project fails to save."""
    pass


class ProjectCloseError(ProjectManagerError):
    """Raised when a project fails to close cleanly."""
    pass


class ProjectDeleteError(ProjectManagerError):
    """Raised when a project or its workspace fails to delete."""
    pass


class WorkspaceCleanupError(ProjectDeleteError):
    """Raised when cleaning up temporary or cached workspace directories fails."""
    pass


# Validation & Serialization Errors
class ProjectValidationError(ProjectManagerError):
    """Raised when a project document or workspace fails integrity and schema checks."""
    pass


class ProjectCorruptionError(ProjectValidationError):
    """Raised when critical project metadata or state is detected as corrupt."""
    pass


class UnsupportedProjectVersionError(ProjectValidationError):
    """Raised when a project's schema version is not supported by the current software version."""
    pass


class ProjectMigrationError(ProjectManagerError):
    """Raised when migrating a project from an older schema version fails."""
    pass


class SerializationError(ProjectManagerError):
    """Raised when serializing project models into a transport/storage format fails."""
    pass


class DeserializationError(ProjectManagerError):
    """Raised when deserializing storage formats back into project models fails."""
    pass


class RepositoryError(ProjectManagerError):
    """Raised when persistence or retrieval operations in the project repository fail."""
    pass


class AtomicWriteError(RepositoryError):
    """Raised when writing project files atomically fails."""
    pass


# Asset Registry Errors
class AssetError(ProjectManagerError):
    """Base exception for all asset-related operations."""
    pass


class AssetNotFoundError(AssetError):
    """Raised when an asset reference is not found in the registry or disk."""
    pass


class AssetAlreadyRegisteredError(AssetError):
    """Raised when registering an asset that already exists in the workspace registry."""
    pass


class InvalidAssetTypeError(AssetError):
    """Raised when an asset's media or file type is unsupported or invalid."""
    pass


class AssetImportError(AssetError):
    """Raised when importing an external file into the project workspace fails."""
    pass


class AssetCopyError(AssetError):
    """Raised when copying an asset file fails."""
    pass


class AssetMoveError(AssetError):
    """Raised when moving an asset file fails."""
    pass


class AssetDeleteError(AssetError):
    """Raised when deleting an asset file from the workspace fails."""
    pass


class AssetPathEscapeError(AssetError):
    """Raised when an asset path attempts directory traversal or escapes the workspace root."""
    pass


# History Errors
class HistoryError(ProjectManagerError):
    """Base exception for undo, redo, and state history tracking."""
    pass


class UndoUnavailableError(HistoryError):
    """Raised when an undo operation is requested but no undo history is available."""
    pass


class RedoUnavailableError(HistoryError):
    """Raised when a redo operation is requested but no redo history is available."""
    pass


class SnapshotCreationError(HistoryError):
    """Raised when creating a project state snapshot fails."""
    pass


class SnapshotRestoreError(HistoryError):
    """Raised when restoring a project state snapshot fails."""
    pass


# Autosave, Recovery, & Lock Errors
class AutosaveError(ProjectManagerError):
    """Raised when performing autosave background/periodic operations fails."""
    pass


class AutosaveUnavailableError(AutosaveError):
    """Raised when autosave functionality is unavailable or cannot be initialized."""
    pass


class RecoveryError(ProjectManagerError):
    """Raised when detecting, validating, or performing disaster/autosave recovery fails."""
    pass


class BackupError(ProjectManagerError):
    """Raised when creating or maintaining project file backups fails."""
    pass


class ProjectLockError(ProjectManagerError):
    """Base exception for project concurrency locks."""
    pass


class ProjectAlreadyLockedError(ProjectLockError):
    """Raised when attempting to acquire a lock on an already locked project."""
    pass


class StaleLockError(ProjectLockError):
    """Raised when detecting, validating, or taking over a stale lock file fails."""
    pass


class ConcurrentModificationError(ProjectManagerError):
    """Raised when external modifications are detected before saving a project."""
    pass


# Database & Recent Project Errors
class RecentProjectsError(ProjectManagerError):
    """Raised when indexing, querying, or modifying the recent projects registry fails."""
    pass
