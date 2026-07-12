"""Structural typing protocols for Module 11: Project Manager.

These protocols define clean interfaces for the low-level repository, workspace management,
concurrency locking, state history (undo/redo), autosaving, validation, and top-level orchestration.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from src.project_manager.project_models import (
    ProjectDocument,
    ProjectSummary,
    ProjectWorkspacePaths,
    ProjectLockInformation,
    ProjectChange,
    AutosaveMetadata,
    ProjectAsset,
    ValidationReport,
    ProjectOpenResult,
    ProjectSaveResult,
    ProjectOperationResult,
    ProjectDeleteResult,
    ProjectState,
)


@runtime_checkable
class ProjectRepositoryProtocol(Protocol):
    """Protocol for reading, writing, listing, and physically deleting projects and documents."""

    def load_document(self, project_path: Path) -> ProjectDocument:
        """Load and deserialize a project document from disk.

        Args:
            project_path: Path to the project workspace directory.

        Returns:
            The loaded ProjectDocument.

        Raises:
            ProjectNotFoundError: If the project file cannot be found.
            DeserializationError: If JSON deserialization fails.
            ProjectValidationError: If the document violates schema constraints.
        """
        ...

    def save_document_atomically(self, project_path: Path, document: ProjectDocument) -> None:
        """Atomically write the project document to disk to prevent corruption on crash.

        Args:
            project_path: Path to the project workspace directory.
            document: The ProjectDocument instance to save.

        Raises:
            ProjectSaveError: If saving fails.
            AtomicWriteError: If renaming the temp file fails.
        """
        ...

    def list_projects(self, search_root: Path) -> List[ProjectSummary]:
        """Scan a directory for valid project workspace structures and return summaries.

        Args:
            search_root: Root directory to search.

        Returns:
            A list of project summaries.
        """
        ...

    def delete_project_files(self, project_path: Path) -> None:
        """Permanently delete all files associated with a project on disk.

        Args:
            project_path: Path to the project workspace directory.

        Raises:
            ProjectDeleteError: If deletion fails.
        """
        ...


@runtime_checkable
class WorkspaceManagerProtocol(Protocol):
    """Protocol for establishing directory hierarchies, resolving relative paths, and safe cleanup."""

    def create_workspace_layout(self, root: Path) -> ProjectWorkspacePaths:
        """Physically create all project subdirectories (assets, generated, logs, etc.).

        Args:
            root: Root path of the project workspace.

        Returns:
            A populated ProjectWorkspacePaths container.

        Raises:
            ProjectPathError: If directory creation fails.
        """
        ...

    def validate_path_safety(self, path: Path, root: Path) -> Path:
        """Verify that a path is safe and does not escape the project root.

        Args:
            path: Target path to check (relative or absolute).
            root: Absolute project workspace root.

        Returns:
            A resolved, absolute safe path.

        Raises:
            AssetPathEscapeError: If directory traversal or escape is detected.
        """
        ...

    def cleanup_temp_directories(self, root: Path) -> None:
        """Clean up transient files or temp workspaces inside the project.

        Args:
            root: Root path of the project workspace.
        """
        ...


@runtime_checkable
class ProjectLockManagerProtocol(Protocol):
    """Protocol for managing directory-level exclusive write locks to prevent data loss."""

    def acquire_lock(self, project_path: Path, session_id: str) -> ProjectLockInformation:
        """Acquire an exclusive lock file on the project directory.

        Args:
            project_path: Path to the project workspace directory.
            session_id: Unique identifier representing the current session.

        Returns:
            A ProjectLockInformation block.

        Raises:
            ProjectAlreadyLockedError: If another process/session holds a valid lock.
        """
        ...

    def release_lock(self, project_path: Path, session_id: str) -> None:
        """Release the exclusive lock file if held by the current session.

        Args:
            project_path: Path to the project workspace directory.
            session_id: Session identifier.

        Raises:
            ProjectLockError: If release fails.
        """
        ...

    def is_lock_valid(self, lock_info: ProjectLockInformation) -> bool:
        """Check if a lock is currently valid or has become stale.

        Args:
            lock_info: Lock information record.

        Returns:
            True if the lock is active and valid, False if stale.
        """
        ...

    def break_stale_lock(self, project_path: Path) -> None:
        """Forcefully remove a stale lock file from a project directory.

        Args:
            project_path: Path to the project workspace directory.
        """
        ...


@runtime_checkable
class HistoryManagerProtocol(Protocol):
    """Protocol for managing the session undo/redo change stacks."""

    def push_change(self, change: ProjectChange) -> None:
        """Commit an atomic transactional change to the history stack.

        Args:
            change: The ProjectChange transaction to record.
        """
        ...

    def undo(self) -> ProjectChange:
        """Revert the last change from the stack.

        Returns:
            The reverted ProjectChange.

        Raises:
            UndoUnavailableError: If the undo stack is empty.
        """
        ...

    def redo(self) -> ProjectChange:
        """Re-apply the previously undone change.

        Returns:
            The re-applied ProjectChange.

        Raises:
            RedoUnavailableError: If the redo stack is empty.
        """
        ...

    def clear_history(self) -> None:
        """Reset and discard all undo/redo history stacks."""
        ...

    def get_undo_stack_size(self) -> int:
        """Return the count of undoable changes."""
        ...

    def get_redo_stack_size(self) -> int:
        """Return the count of redoable changes."""
        ...


@runtime_checkable
class AutosaveManagerProtocol(Protocol):
    """Protocol for orchestrating background periodic state saves."""

    def initialize_autosave(self, project_path: Path, interval_seconds: int) -> None:
        """Start a background worker or scheduler to periodically save state.

        Args:
            project_path: Path to the project workspace.
            interval_seconds: Saved period interval.
        """
        ...

    def trigger_autosave(self, document: ProjectDocument) -> Optional[AutosaveMetadata]:
        """Perform an immediate, non-blocking atomic autosave snapshot.

        Args:
            document: Current ProjectDocument.

        Returns:
            AutosaveMetadata if saved successfully, None otherwise.
        """
        ...

    def stop_autosave(self) -> None:
        """Stop the autosave scheduler and clean up background tasks."""
        ...

    def cleanup_stale_autosaves(self, project_path: Path) -> None:
        """Remove older autosave snapshot files keeping only a designated count.

        Args:
            project_path: Path to the project workspace.
        """
        ...


@runtime_checkable
class ProjectValidatorProtocol(Protocol):
    """Protocol for performing structural schema and workspace asset audits."""

    def validate_document(self, document: ProjectDocument) -> ValidationReport:
        """Perform recursive structural integrity checks on metadata, settings, and references.

        Args:
            document: Target ProjectDocument to analyze.

        Returns:
            ValidationReport detailing all issues found.
        """
        ...

    def validate_assets(self, project_path: Path, assets: Dict[str, ProjectAsset]) -> ValidationReport:
        """Check the physical existence, accessibility, and hashes of registered assets on disk.

        Args:
            project_path: Root project path.
            assets: Dictionary of registered assets.

        Returns:
            ValidationReport.
        """
        ...


@runtime_checkable
class ProjectManagerProtocol(Protocol):
    """Top-level controller interface orchestrating the Project Manager lifecycle."""

    def create_project(self, name: str, root_dir: Path, description: str = "") -> ProjectOpenResult:
        """Create a new project workspace directory, metadata layout, and database registrations.

        Args:
            name: Project name.
            root_dir: Directory where the workspace will be created.
            description: Optional project description.

        Returns:
            ProjectOpenResult.

        Raises:
            ProjectAlreadyExistsError: If a workspace already exists at the target.
            InvalidProjectNameError: If name fails validations.
        """
        ...

    def open_project(self, project_path: Path, read_only: bool = False) -> ProjectOpenResult:
        """Open an existing project, acquiring locks and running schema migrations if required.

        Args:
            project_path: Path to project directory.
            read_only: Force open in read-only mode to bypass lock acquisition.

        Returns:
            ProjectOpenResult.

        Raises:
            ProjectNotFoundError: If the project path is invalid or empty.
            ProjectOpenError: If loading fails.
        """
        ...

    def save_project(self) -> ProjectSaveResult:
        """Save the active project document atomically, incrementing revisions.

        Returns:
            ProjectSaveResult.

        Raises:
            ProjectSaveError: If saving fails or if no project is active.
        """
        ...

    def close_project(self) -> ProjectOperationResult:
        """Close the active project, clearing state, releasing locks, and ending autosave timers.

        Returns:
            ProjectOperationResult.
        """
        ...

    def delete_project(self, project_path: Path) -> ProjectDeleteResult:
        """Permanently delete a project and all workspace files.

        Args:
            project_path: Path to project directory.

        Returns:
            ProjectDeleteResult.
        """
        ...

    def register_asset(self, asset: ProjectAsset) -> ProjectAsset:
        """Add a new source or generated media file to the active project's asset registry.

        Args:
            asset: ProjectAsset to register.

        Returns:
            The registered ProjectAsset.
        """
        ...

    def get_state(self) -> ProjectState:
        """Return the current immutable runtime snapshot of the project session.

        Returns:
            ProjectState.
        """
        ...
