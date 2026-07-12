"""Strongly typed domain and operational models for Module 11: Project Manager.

This module provides all Enums and Dataclasses representing project status,
operation status, settings, asset tracking, history, locking, recovery, and results.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.project_manager.exceptions import InvalidProjectRequestError, ProjectValidationError


class ProjectStatus(str, Enum):
    """The runtime lifecycle or operational state of the Project Manager."""
    NO_PROJECT_OPEN = "no_project_open"
    OPENING = "opening"
    OPEN = "open"
    OPEN_READ_ONLY = "open_read_only"
    SAVING = "saving"
    CLOSING = "closing"
    RECOVERING = "recovering"
    MIGRATING = "migrating"
    ERROR = "error"


class ProjectOperationStatus(str, Enum):
    """Execution outcome status for project operations."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProjectAssetType(str, Enum):
    """Classification of assets tracked inside the project registry."""
    SOURCE = "source"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    SUBTITLE = "subtitle"
    LOGO = "logo"
    MUSIC = "music"
    OTHER = "other"


class AssetStorageMode(str, Enum):
    """Indicates where the asset file physically resides relative to the workspace."""
    INTERNAL = "internal"
    EXTERNAL = "external"


class AssetSourceType(str, Enum):
    """Origin of the registered asset."""
    IMPORTED = "imported"
    GENERATED = "generated"
    REFERENCED = "referenced"


class ProjectChangeType(str, Enum):
    """The category of modification applied during project mutation."""
    METADATA = "metadata"
    SETTINGS = "settings"
    ASSET_REGISTERED = "asset_registered"
    ASSET_REMOVED = "asset_removed"
    SCRIPT_REFERENCE = "script_reference"
    SPEECH_REFERENCE = "speech_reference"
    SUBTITLE_REFERENCE = "subtitle_reference"
    RENDER_REFERENCE = "render_reference"
    SELECTION_CHANGE = "selection_change"


class HistoryActionType(str, Enum):
    """Type of action executed on the project state stack."""
    COMMIT = "commit"
    UNDO = "undo"
    REDO = "redo"
    ROLLBACK = "rollback"


class SnapshotType(str, Enum):
    """Classification of state backups / snapshots."""
    MANUAL = "manual"
    AUTO = "auto"
    BACKUP = "backup"
    MIGRATION = "migration"


class LockStatus(str, Enum):
    """The exclusive write lock status of a project directory."""
    FREE = "free"
    LOCKED = "locked"
    STALE = "stale"


class RecoveryStatus(str, Enum):
    """Disaster recovery state for candidate projects."""
    NO_RECOVERY_NEEDED = "no_recovery_needed"
    AVAILABLE = "available"
    RECOVERED = "recovered"
    DISCARDED = "discarded"


class ProjectSchemaVersion(str, Enum):
    """Supported schema versions of the project document."""
    V1 = "1.0.0"


# Helper function to ensure datetime is timezone-aware
def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class ProjectMetadata:
    """Core descriptive information and revision metrics of a project.

    Attributes:
        project_id: Unique identifier of the project.
        name: User-facing name of the project.
        description: User-defined text summary of the project.
        created_at: Creation timestamp (timezone-aware).
        modified_at: Last modification timestamp (timezone-aware).
        application_version: Software version that created or saved this document.
        schema_version: Structural version of the JSON schema layout.
        revision_number: Monotonically increasing revision count of operations.
        last_saved_revision: Last committed revision successfully saved to disk.
        user_metadata: Flexible dictionary of unstructured extension fields.
    """
    project_id: str
    name: str
    description: str
    created_at: datetime
    modified_at: datetime
    application_version: str
    schema_version: str = ProjectSchemaVersion.V1.value
    revision_number: int = 1
    last_saved_revision: int = 1
    user_metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.project_id.strip():
            raise InvalidProjectRequestError("project_id cannot be empty.")
        if not self.name.strip():
            raise InvalidProjectRequestError("Project name cannot be empty.")
        # Re-assigning frozen dataclass fields via __setattr__ to guarantee UTC safety
        object.__setattr__(self, "created_at", _ensure_utc(self.created_at))
        object.__setattr__(self, "modified_at", _ensure_utc(self.modified_at))
        if self.revision_number <= 0:
            raise InvalidProjectRequestError("revision_number must be strictly positive.")
        if self.last_saved_revision <= 0:
            raise InvalidProjectRequestError("last_saved_revision must be strictly positive.")


@dataclass(frozen=True)
class ProjectPlatformSettings:
    """Pre-configured platform overrides for renders and uploads.

    Attributes:
        target_platform: Primary destination (e.g., 'tiktok', 'youtube_shorts').
        default_aspect_ratio: Target aspect ratio preset (e.g. '9:16').
        default_resolution: Default resolution preset (e.g. '1080x1920').
        default_frame_rate: Frame count per second.
    """
    target_platform: str = "tiktok"
    default_aspect_ratio: str = "9:16"
    default_resolution: str = "1080x1920"
    default_frame_rate: int = 30

    def __post_init__(self) -> None:
        if not self.target_platform.strip():
            raise InvalidProjectRequestError("target_platform cannot be empty.")
        if self.default_frame_rate <= 0:
            raise InvalidProjectRequestError("default_frame_rate must be strictly positive.")


@dataclass(frozen=True)
class ProjectSettings:
    """Aggregated project-specific overrides for Module 11 workspace behavior.

    Attributes:
        platform_settings: Visual defaults for video rendering targets.
        default_script_duration_seconds: Default target script timeline length.
        default_voice_id: Preselected TTS voice identifier.
        default_subtitle_style: Preselected styling template for subtitles.
        default_render_preset: Performance preference profile for FFmpeg rendering.
        default_output_directory: Default output location inside the workspace.
        autosave_enabled: Toggle periodic background autosave operations.
        autosave_interval_seconds: Trigger threshold interval for autosaves.
        history_retention_limit: Maximum size of the undo/redo stack.
        snapshot_retention_limit: Maximum count of state snapshots to preserve.
        cache_policy: Expiry or clean instructions for intermediate caches.
    """
    platform_settings: ProjectPlatformSettings = field(default_factory=ProjectPlatformSettings)
    default_script_duration_seconds: float = 60.0
    default_voice_id: str = "preset_vietnamese_male"
    default_subtitle_style: str = "default_tiktok"
    default_render_preset: str = "medium"
    default_output_directory: str = "generated/renders"
    autosave_enabled: bool = True
    autosave_interval_seconds: int = 300
    history_retention_limit: int = 50
    snapshot_retention_limit: int = 10
    cache_policy: str = "default"

    def __post_init__(self) -> None:
        if self.default_script_duration_seconds <= 0:
            raise InvalidProjectRequestError("default_script_duration_seconds must be positive.")
        if self.autosave_interval_seconds <= 0:
            raise InvalidProjectRequestError("autosave_interval_seconds must be positive.")
        if self.history_retention_limit < 0:
            raise InvalidProjectRequestError("history_retention_limit must be non-negative.")
        if self.snapshot_retention_limit < 0:
            raise InvalidProjectRequestError("snapshot_retention_limit must be non-negative.")


@dataclass(frozen=True)
class ProjectScriptReference:
    """A reference record pointing to a script generated by Module 07.

    Attributes:
        script_id: Stable identifier of the script.
        title: Descriptive script title.
        content_text: Plain-text script content.
        generated_at: Timestamp when generation succeeded.
        metadata: Accompanying statistics or prompt generation info.
    """
    script_id: str
    title: str
    content_text: str
    generated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.script_id.strip():
            raise InvalidProjectRequestError("script_id cannot be empty.")
        object.__setattr__(self, "generated_at", _ensure_utc(self.generated_at))


@dataclass(frozen=True)
class ProjectSpeechReference:
    """A reference record pointing to generated speech audio produced by Module 08.

    Attributes:
        speech_id: Stable identifier of the speech generation result.
        script_id: script source origin identifier.
        audio_path: Project-relative or external filesystem path to the WAV asset.
        voice_id: Profile ID utilized during synthesis.
        duration_seconds: True playback duration.
        generated_at: Timestamp when TTS completed.
        metadata: Accent, pitch, or device information.
    """
    speech_id: str
    script_id: str
    audio_path: str
    voice_id: str
    duration_seconds: float
    generated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.speech_id.strip():
            raise InvalidProjectRequestError("speech_id cannot be empty.")
        if not self.script_id.strip():
            raise InvalidProjectRequestError("script_id cannot be empty.")
        if not self.audio_path.strip():
            raise InvalidProjectRequestError("audio_path cannot be empty.")
        if self.duration_seconds < 0:
            raise InvalidProjectRequestError("duration_seconds cannot be negative.")
        object.__setattr__(self, "generated_at", _ensure_utc(self.generated_at))


@dataclass(frozen=True)
class ProjectSubtitleReference:
    """A reference record pointing to generated subtitles from Module 09.

    Attributes:
        subtitle_id: Stable identifier of the subtitle.
        script_id: script source origin identifier.
        subtitle_path: Project-relative or external path to SRT/ASS.
        style_preset: Name of applied style preset.
        generated_at: Timestamp when subtitle file compiled.
        metadata: Average character count, line counts, or overlapping warnings.
    """
    subtitle_id: str
    script_id: str
    subtitle_path: str
    style_preset: str
    generated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.subtitle_id.strip():
            raise InvalidProjectRequestError("subtitle_id cannot be empty.")
        if not self.script_id.strip():
            raise InvalidProjectRequestError("script_id cannot be empty.")
        if not self.subtitle_path.strip():
            raise InvalidProjectRequestError("subtitle_path cannot be empty.")
        object.__setattr__(self, "generated_at", _ensure_utc(self.generated_at))


@dataclass(frozen=True)
class ProjectRenderReference:
    """A reference record pointing to a compiled video asset from Module 10.

    Attributes:
        render_id: Stable identifier of the render task output.
        output_path: Path location of the final MP4.
        duration_seconds: True runtime length.
        file_size_bytes: True file footprint size on disk.
        video_codec: Encoder mapping compiled under.
        audio_codec: Audio layout compression mapping.
        resolution: Text dimensions string.
        frame_rate: Frames per second.
        rendered_at: Timestamp when compilation finished.
        metadata: GPU speed, hardware acceleration, warnings, etc.
    """
    render_id: str
    output_path: str
    duration_seconds: float
    file_size_bytes: int
    video_codec: str
    audio_codec: str
    resolution: str
    frame_rate: float
    rendered_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.render_id.strip():
            raise InvalidProjectRequestError("render_id cannot be empty.")
        if not self.output_path.strip():
            raise InvalidProjectRequestError("output_path cannot be empty.")
        if self.duration_seconds < 0:
            raise InvalidProjectRequestError("duration_seconds cannot be negative.")
        if self.file_size_bytes < 0:
            raise InvalidProjectRequestError("file_size_bytes cannot be negative.")
        if self.frame_rate <= 0:
            raise InvalidProjectRequestError("frame_rate must be strictly positive.")
        object.__setattr__(self, "rendered_at", _ensure_utc(self.rendered_at))


@dataclass(frozen=True)
class AssetMetadata:
    """Physical and analytical parameters of a registered media file.

    Attributes:
        mime_type: File container format standard label.
        duration_seconds: Playback time length if relevant.
        width: Pixel width if relevant.
        height: Pixel height if relevant.
        extra_info: Flexible dictionary for custom analysis variables.
    """
    mime_type: Optional[str] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    extra_info: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectAsset:
    """Structural details tracking a source or generated media file in the registry.

    Attributes:
        asset_id: Unique identifier for tracking and reference links.
        asset_type: Visual/sound/text category of the media.
        display_name: Human-readable file tag.
        relative_path: Safe project-relative file location (or absolute for external assets).
        storage_mode: Indication of internal copying or external referencing.
        source_type: Indication of imported assets vs outputs generated by studio modules.
        file_size_bytes: Actual disk footprint size.
        content_hash: SHA-256 or MD5 data fingerprint.
        created_at: Creation timestamp in registry.
        modified_at: Modification timestamp on disk.
        generated_by_module: Code string for originating module (e.g. 'Module 08').
        metadata: Detailed stream/media metadata parameters.
        availability_status: Diagnostic status indicating if file is online or missing.
    """
    asset_id: str
    asset_type: ProjectAssetType
    display_name: str
    relative_path: str
    storage_mode: AssetStorageMode
    source_type: AssetSourceType
    file_size_bytes: int
    content_hash: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by_module: Optional[str] = None
    metadata: AssetMetadata = field(default_factory=AssetMetadata)
    availability_status: str = "active"

    def __post_init__(self) -> None:
        if not self.asset_id.strip():
            raise InvalidProjectRequestError("asset_id cannot be empty.")
        if not self.display_name.strip():
            raise InvalidProjectRequestError("display_name cannot be empty.")
        if not self.relative_path.strip():
            raise InvalidProjectRequestError("relative_path cannot be empty.")
        if self.file_size_bytes < 0:
            raise InvalidProjectRequestError("file_size_bytes cannot be negative.")
        object.__setattr__(self, "created_at", _ensure_utc(self.created_at))
        object.__setattr__(self, "modified_at", _ensure_utc(self.modified_at))


@dataclass(frozen=True)
class ProjectWorkspacePaths:
    """Standard subdirectory layouts allocated per project workspace.

    Attributes:
        root: The physical parent workspace directory.
        assets_dir: Subfolder housing source, video, audio, image imports.
        generated_dir: Subfolder housing scripts, speech, and final renders.
        cache_dir: Workspace temporary calculation caches.
        autosave_dir: Target directory for atomic background autosaves.
        history_dir: Target directory for saving undo/redo state revisions.
        backups_dir: Subfolder containing zipped or manual saves.
        temp_dir: Subfolder containing transient process workspaces.
        logs_dir: Subfolder tracking file system changes and diagnostic traces.
    """
    root: Path
    assets_dir: Path
    generated_dir: Path
    cache_dir: Path
    autosave_dir: Path
    history_dir: Path
    backups_dir: Path
    temp_dir: Path
    logs_dir: Path


@dataclass(frozen=True)
class ProjectDocument:
    """The complete, fully serializable schema model representing a project's state.

    Attributes:
        metadata: Descriptor schema mapping.
        settings: Override settings.
        scripts: Collection of Module 07 script outputs indexed by script_id.
        speech: Collection of Module 08 voice files indexed by speech_id.
        subtitles: Collection of Module 09 subtitles indexed by subtitle_id.
        renders: Collection of Module 10 export files indexed by render_id.
        assets: System registered assets index.
        active_selections: Map storing client selection parameters.
    """
    metadata: ProjectMetadata
    settings: ProjectSettings
    scripts: Dict[str, ProjectScriptReference] = field(default_factory=dict)
    speech: Dict[str, ProjectSpeechReference] = field(default_factory=dict)
    subtitles: Dict[str, ProjectSubtitleReference] = field(default_factory=dict)
    renders: Dict[str, ProjectRenderReference] = field(default_factory=dict)
    assets: Dict[str, ProjectAsset] = field(default_factory=dict)
    active_selections: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert project document payload into a serializable map structure."""
        return asdict(self)


@dataclass(frozen=True)
class ProjectSummary:
    """A lightweight indexing layout mapping external workspace descriptors.

    Attributes:
        project_id: Unique project identifier.
        name: Name of the project.
        description: Brief description text.
        created_at: Time project was created.
        modified_at: Time project was modified.
        workspace_path: System workspace path.
        schema_version: Schema format version.
        file_size_bytes: project.json file footprint size on disk.
    """
    project_id: str
    name: str
    description: str
    created_at: datetime
    modified_at: datetime
    workspace_path: Path
    schema_version: str
    file_size_bytes: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _ensure_utc(self.created_at))
        object.__setattr__(self, "modified_at", _ensure_utc(self.modified_at))


@dataclass(frozen=True)
class ProjectState:
    """An immutable runtime snapshot reflecting the operational state of a project.

    Attributes:
        status: Core operational status.
        dirty: Indicates unsaved changes in the session document.
        current_revision: Total revision mutations count.
        last_saved_revision: Last committed disk save revision.
        active_project_path: Workspace directory path on disk.
        active_project_id: Open project identifier.
        read_only: Opened under exclusive read-only locks fallback.
        lock_status: Status tracking the directory's locks.
        autosave_available: Background periodic saves system availability.
        undo_available: Undo operation stack size indicator.
        redo_available: Redo operation stack size indicator.
    """
    status: ProjectStatus
    dirty: bool
    current_revision: int
    last_saved_revision: int
    active_project_path: Optional[Path] = None
    active_project_id: Optional[str] = None
    read_only: bool = False
    lock_status: LockStatus = LockStatus.FREE
    autosave_available: bool = False
    undo_available: bool = False
    redo_available: bool = False


@dataclass(frozen=True)
class ProjectChange:
    """An atomic transactional mutation representation for history and rollback logic.

    Attributes:
        change_id: Unique change tracking identifier.
        change_type: Action class of modified document field.
        timestamp: Creation timestamp.
        description: Verbose text documenting change context.
        inverse_patch: Delta payload required to revert changes back.
        forward_patch: Delta payload required to re-apply the change forward.
    """
    change_id: str
    change_type: ProjectChangeType
    timestamp: datetime
    description: str
    inverse_patch: Dict[str, Any] = field(default_factory=dict)
    forward_patch: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.change_id.strip():
            raise InvalidProjectRequestError("change_id cannot be empty.")
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


@dataclass(frozen=True)
class HistoryEntry:
    """A collection of grouped changes committed inside one revision milestone.

    Attributes:
        revision: Core target revision number associated.
        action_type: Transaction trigger classification (e.g., Commit, Undo).
        timestamp: Operational timestamp.
        description: Summary text describing operation.
        changes: Ordered list of delta changes executed inside this transaction.
    """
    revision: int
    action_type: HistoryActionType
    timestamp: datetime
    description: str
    changes: List[ProjectChange] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.revision <= 0:
            raise InvalidProjectRequestError("revision must be strictly positive.")
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


@dataclass(frozen=True)
class SnapshotMetadata:
    """Structural info describing a manual or automated project backup snapshot.

    Attributes:
        snapshot_id: Unique identifier tracking the state archive.
        project_id: Target project identifier.
        revision: State revision the snapshot represents.
        created_at: Datetime archiving.
        snapshot_type: Categorized trigger context.
        description: Informational comment.
        file_path: Archive backup path location.
    """
    snapshot_id: str
    project_id: str
    revision: int
    created_at: datetime
    snapshot_type: SnapshotType
    description: str
    file_path: Path

    def __post_init__(self) -> None:
        if not self.snapshot_id.strip():
            raise InvalidProjectRequestError("snapshot_id cannot be empty.")
        if self.revision <= 0:
            raise InvalidProjectRequestError("revision must be strictly positive.")
        object.__setattr__(self, "created_at", _ensure_utc(self.created_at))


@dataclass(frozen=True)
class AutosaveMetadata:
    """Operational metrics representing an atomic background autosave file.

    Attributes:
        project_id: Target project identifier.
        revision: Project state revision saved.
        autosaved_at: Datetime of backup creation.
        file_path: Path file location on disk.
    """
    project_id: str
    revision: int
    autosaved_at: datetime
    file_path: Path

    def __post_init__(self) -> None:
        if self.revision <= 0:
            raise InvalidProjectRequestError("revision must be positive.")
        object.__setattr__(self, "autosaved_at", _ensure_utc(self.autosaved_at))


@dataclass(frozen=True)
class BackupMetadata:
    """Historical restore archive details.

    Attributes:
        project_id: Unique project ID.
        revision: Source document state revision.
        backed_up_at: Backup datetime.
        file_path: Safe path pointing to zip or backup file on disk.
    """
    project_id: str
    revision: int
    backed_up_at: datetime
    file_path: Path

    def __post_init__(self) -> None:
        if self.revision <= 0:
            raise InvalidProjectRequestError("revision must be positive.")
        object.__setattr__(self, "backed_up_at", _ensure_utc(self.backed_up_at))


@dataclass(frozen=True)
class ProjectLockInformation:
    """A concurrency control mapping representing exclusive write lock ownership.

    Attributes:
        project_id: Target locked project.
        process_id: Operating system process ID holding locks.
        host_name: Name of local machine environment.
        session_id: Client UUID representing session runtime.
        acquired_at: Acquisition timestamp.
        is_stale: Marked flag if expiration timeout exceeded or process dead.
    """
    project_id: str
    process_id: int
    host_name: str
    session_id: str
    acquired_at: datetime
    is_stale: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "acquired_at", _ensure_utc(self.acquired_at))


@dataclass(frozen=True)
class RecoveryInformation:
    """Candidate metrics describing recovered state possibilities on crash startup.

    Attributes:
        project_id: Candidate recovery target.
        recovery_status: Tracking status of the recovery.
        last_autosave_time: Time of newest autosave snapshot if present.
        project_last_modified: Time of official metadata document modification.
        autosave_revision: Revision count inside the autosave file.
        project_revision: Revision count inside standard project document.
    """
    project_id: str
    recovery_status: RecoveryStatus
    last_autosave_time: Optional[datetime] = None
    project_last_modified: Optional[datetime] = None
    autosave_revision: int = 0
    project_revision: int = 0

    def __post_init__(self) -> None:
        if self.last_autosave_time is not None:
            object.__setattr__(self, "last_autosave_time", _ensure_utc(self.last_autosave_time))
        if self.project_last_modified is not None:
            object.__setattr__(self, "project_last_modified", _ensure_utc(self.project_last_modified))


@dataclass(frozen=True)
class RecentProjectEntry:
    """A lightweight record stored inside indices for fast dashboard loading.

    Attributes:
        project_id: Target project tracker.
        display_name: Client name.
        workspace_path: Path pointing to workspace on disk.
        last_opened_at: Open datetime.
        last_saved_at: Save datetime.
        is_pinned: Toggle user dashboard pin status.
        is_available: Operational check checking if workspace still exists on disk.
    """
    project_id: str
    display_name: str
    workspace_path: Path
    last_opened_at: datetime
    last_saved_at: datetime
    is_pinned: bool = False
    is_available: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "last_opened_at", _ensure_utc(self.last_opened_at))
        object.__setattr__(self, "last_saved_at", _ensure_utc(self.last_saved_at))


@dataclass(frozen=True)
class ValidationIssue:
    """A discrete discrepancy discovered during structure or registry scanning.

    Attributes:
        severity: Criticality classification ("error", "warning").
        code: Identifier categorizing issue category.
        message: Readable summary log descriptive string.
        field_path: JSON path key pointing to target field (e.g., 'metadata.name').
    """
    severity: str
    code: str
    message: str
    field_path: Optional[str] = None

    def __post_init__(self) -> None:
        if self.severity not in ("error", "warning"):
            raise ProjectValidationError(f"Invalid validation severity: {self.severity}")


@dataclass(frozen=True)
class ValidationReport:
    """Result summary produced by the ProjectValidator scanning system.

    Attributes:
        is_valid: True if no issues of 'error' severity are found.
        issues: Full indexed sequence of findings.
        checked_at: Scanner execution timestamp.
    """
    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "checked_at", _ensure_utc(self.checked_at))
        # Dynamically enforce that if any issue has "error" severity, is_valid must be False
        has_error = any(issue.severity == "error" for issue in self.issues)
        if has_error and self.is_valid:
            object.__setattr__(self, "is_valid", False)


@dataclass(frozen=True)
class ProjectOperationResult:
    """General structural response documenting basic single project transaction outcomes.

    Attributes:
        operation_id: Transaction transaction tracker.
        status: Execution status.
        project_id: Target project identifier.
        project_path: Parent workspace path.
        warnings: Capture anomalies.
        error_message: Summary error tracking.
    """
    operation_id: str
    status: ProjectOperationStatus
    project_id: Optional[str] = None
    project_path: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass(frozen=True)
class ProjectOpenResult:
    """Comprehensive payload detailing success parameters of opening workspaces.

    Attributes:
        operation_id: Transaction tracker.
        status: Execution status.
        project_id: Unique project ID.
        project_path: Path location of active workspace.
        project_state: Runtime operational metrics snapshot.
        read_only_status: Opened under fallback read-only parameters.
        validation_report: Diagnostic validator report.
        recovery_available: Toggle indicating newer autosaves exist.
        migration_performed: Flag indicating schema was updated on open.
        lock_info: Reference to active session locks.
        warnings: Capture anomalies.
    """
    operation_id: str
    status: ProjectOperationStatus
    project_id: str
    project_path: Path
    project_state: ProjectState
    read_only_status: bool
    validation_report: ValidationReport
    recovery_available: bool
    migration_performed: bool
    lock_info: Optional[ProjectLockInformation] = None
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProjectSaveResult:
    """Comprehensive payload detailing committed metrics of successful saves.

    Attributes:
        operation_id: Transaction tracker.
        status: Execution status.
        project_id: Target project ID.
        project_path: Path location of workspace.
        revision: Document mutation revision saved.
        saved_timestamp: Timestamp when save completed.
        backup_path: Path pointing to history backup if archived.
        autosave_cleaned: Cleaned obsolete recovery files as safety.
        warnings: Capture non-fatal anomalies.
    """
    operation_id: str
    status: ProjectOperationStatus
    project_id: str
    project_path: Path
    revision: int
    saved_timestamp: datetime
    backup_path: Optional[Path] = None
    autosave_cleaned: bool = False
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "saved_timestamp", _ensure_utc(self.saved_timestamp))


@dataclass(frozen=True)
class ProjectDeleteResult:
    """Payload documenting final outcome of explicit deletion requests.

    Attributes:
        operation_id: Transaction tracker.
        status: Execution status.
        project_id: Terminated project ID.
        deleted_project_path: Deleted path.
        deletion_mode: Permanent delete or operating system trash mode.
        warnings: Capture anomalies.
    """
    operation_id: str
    status: ProjectOperationStatus
    project_id: str
    deleted_project_path: Path
    deletion_mode: str
    warnings: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class HealthStatus:
    """Operational diagnostic integrity report.

    Attributes:
        is_healthy: True if system is completely operational.
        status_message: Informational diagnostics log string.
        last_checked_at: Verification timestamp.
    """
    is_healthy: bool
    status_message: str
    last_checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "last_checked_at", _ensure_utc(self.last_checked_at))
