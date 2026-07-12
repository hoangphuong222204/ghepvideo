"""Strongly typed presentation models for Module 13: NiceGUI Desktop UI.

This module provides all Enums and Dataclasses representing user interface views,
states, notifications, task statuses, preferences, and data mapping helpers
for the desktop application.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.ui.exceptions import FormValidationError


class ApplicationPage(str, Enum):
    """Available application routes and views."""
    DASHBOARD = "dashboard"
    PROJECT = "project"
    PRODUCT = "product"
    SCRIPTS = "scripts"
    SPEECH = "speech"
    SUBTITLES = "subtitles"
    RENDER = "render"
    GENERATE_VIDEO = "generate_video"
    ASSETS = "assets"
    SETTINGS = "settings"
    DIAGNOSTICS = "diagnostics"


class UITaskStatus(str, Enum):
    """The execution status of UI asynchronous worker tasks."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Types of visual notifications displayed to the user."""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class DialogType(str, Enum):
    """Supported popup dialog types for user confirmation and interaction."""
    CONFIRMATION = "confirmation"
    UNSAVED_CHANGES = "unsaved_changes"
    OVERWRITE = "overwrite"
    DELETE_PROJECT = "delete_project"
    RECOVERY = "recovery"
    LOCK_CONFLICT = "lock_conflict"
    MISSING_ASSET = "missing_asset"
    FAILURE_DETAILS = "failure_details"
    SCRIPT_SELECTION = "script_selection"
    AWAITING_INPUT = "awaiting_input"
    ABOUT = "about"


class ThemeMode(str, Enum):
    """Active color styling mode."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class AccentColor(str, Enum):
    """Visual theme accent color configurations."""
    BLUE = "blue"
    INDIGO = "indigo"
    VIOLET = "violet"
    EMERALD = "emerald"
    AMBER = "amber"
    ROSE = "rose"
    SLATE = "slate"


class SidebarState(str, Enum):
    """Layout sizing mode of the persistent application sidebar."""
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"


class PreviewType(str, Enum):
    """Media and file categorization for preview panels."""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    SUBTITLE = "subtitle"
    SCRIPT = "script"
    NONE = "none"


# Helper function to ensure datetime is timezone-aware and UTC formatted
def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class NavigationItem:
    """Represents a navigation button entry on the primary sidebar.

    Attributes:
        page: Target route view.
        label: Visual display text.
        icon: Lucide or Material icon identifier string.
        requires_project: Toggle indicating if active project context is required to visit.
    """
    page: ApplicationPage
    label: str
    icon: str
    requires_project: bool = True


@dataclass(frozen=True)
class ValidationMessage:
    """A visual validation warning or error linked to a specific form field.

    Attributes:
        field_name: Target input name or identifier path.
        severity: Criticality rating ("error" or "warning").
        message: Descriptive validation tip text.
    """
    field_name: str
    severity: str
    message: str

    def __post_init__(self) -> None:
        if self.severity not in ("error", "warning"):
            raise FormValidationError(f"Invalid validation severity: {self.severity}")


@dataclass(frozen=True)
class FormFieldState:
    """The immediate validation and feedback state of an individual form input.

    Attributes:
        value: Input data value.
        is_valid: False if blocking errors exist.
        error_message: Error tip text.
        warning_message: Optional non-blocking warning text.
    """
    value: Any
    is_valid: bool = True
    error_message: Optional[str] = None
    warning_message: Optional[str] = None


@dataclass(frozen=True)
class UIWarning:
    """A non-fatal alert notification details package.

    Attributes:
        code: System warning category identifier code.
        message: Informational details.
        timestamp: Creation moment.
    """
    code: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


@dataclass(frozen=True)
class UIErrorInfo:
    """Detailed error tracing information suitable for dialog detail expandable drawers.

    Attributes:
        error_id: Unique diagnostic incident code.
        message: Human-friendly summary log string.
        exception_class: Underlying technical Exception name.
        stack_trace: Optional debug traceback details.
        timestamp: Crash moment.
    """
    error_id: str
    message: str
    exception_class: str
    stack_trace: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


@dataclass(frozen=True)
class RecentProjectDisplayItem:
    """Lightweight rendering model for project selectors on dashboards.

    Attributes:
        project_id: Unique project tracker.
        display_name: Project name.
        workspace_path: Workspace directory path.
        last_opened_at: Last access moment.
        last_saved_at: Last persistence save moment.
        is_pinned: Toggle user dashboard pin status.
        is_available: False if directory has been deleted or is offline.
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
class ProjectDisplayState:
    """Visual presentation state of the active project.

    Attributes:
        project_id: Open project identifier.
        name: Name of the project.
        description: Brief description text.
        is_dirty: Visual flag indicating unsaved document changes.
        is_read_only: fallbacks locked or open read-only mode indicator.
        workspace_path: Active workspace folder location on disk.
        created_at: Open project creation time.
        modified_at: Open project last modified metadata time.
        revision_number: Active session revision index.
        last_saved_revision: Revision successfully written to disk on save.
    """
    project_id: str
    name: str
    description: str
    is_dirty: bool
    is_read_only: bool
    workspace_path: Path
    created_at: datetime
    modified_at: datetime
    revision_number: int = 1
    last_saved_revision: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _ensure_utc(self.created_at))
        object.__setattr__(self, "modified_at", _ensure_utc(self.modified_at))


@dataclass(frozen=True)
class WorkflowStepDisplayState:
    """Visual status trackers representing workflow pipeline milestones.

    Attributes:
        step_type: Standard workflow step type identifier.
        label: Vietnamese or human-facing display label.
        status: Execution state ("pending", "running", "completed", "failed", "skipped").
        percentage: Percent progress compiled inside active step.
        started_at: Activation timestamp.
        completed_at: Finish timestamp.
        duration_seconds: Step elapsed latency.
        error_message: Summary error tracking.
        warnings: Capture anomalies.
    """
    step_type: str
    label: str
    status: str
    percentage: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.started_at is not None:
            object.__setattr__(self, "started_at", _ensure_utc(self.started_at))
        if self.completed_at is not None:
            object.__setattr__(self, "completed_at", _ensure_utc(self.completed_at))


@dataclass(frozen=True)
class ProgressDisplayState:
    """Aggregated numerical execution progress metrics.

    Attributes:
        percentage: Percent progress clamped between 0.0 and 100.0.
        elapsed_seconds: Elapsed duration.
        estimated_remaining_seconds: Approximated remaining time budget.
        status_message: Informational summary log string.
    """
    percentage: float
    elapsed_seconds: float
    estimated_remaining_seconds: Optional[float] = None
    status_message: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "percentage", max(0.0, min(100.0, self.percentage)))


@dataclass(frozen=True)
class WorkflowDisplayState:
    """Visual state mapping an ongoing background video compilation workflow.

    Attributes:
        workflow_id: Tracking session ID.
        workflow_type: Active pipeline category.
        status: Core operational status.
        current_step: Processing step identifier.
        steps: List containing statuses of individual milestones.
        progress: Aggregated progress percentages tracking.
        final_output_path: Target video file location.
        warnings: Minor non-blocking alert warnings.
        error_message: System error traceback description on crash.
    """
    workflow_id: str
    workflow_type: str
    status: str
    current_step: Optional[str] = None
    steps: List[WorkflowStepDisplayState] = field(default_factory=list)
    progress: ProgressDisplayState = field(default_factory=lambda: ProgressDisplayState(0.0, 0.0))
    final_output_path: Optional[Path] = None
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass(frozen=True)
class ScriptDisplayItem:
    """Rendering card model mapping a generated prompt marketing script.

    Attributes:
        script_id: Stable script identifier.
        title: Vietnamese description summary title.
        content_text: Plain-text script text.
        estimated_duration: Script estimated speaking timeline budget.
        generated_at: Timestamp creation.
        style: Style category name.
        hook: Intro hook line text.
        body: Narrative description lines.
        cta: Target action line text.
        warnings: Capture anomalies.
    """
    script_id: str
    title: str
    content_text: str
    estimated_duration: float
    generated_at: datetime
    style: str
    hook: str
    body: str
    cta: str
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        object.__setattr__(self, "generated_at", _ensure_utc(self.generated_at))


@dataclass(frozen=True)
class VoiceDisplayItem:
    """Vietnamese voice preset option representing Fish Speech models.

    Attributes:
        voice_id: Stable identifier of the voice.
        display_name: Readable description labels.
        gender: Male/Female categorization.
        language: ISO-639-1 layout code string.
        is_cloned: True if custom user-imported clone voice.
        sample_audio_path: Path pointing to sample voice WAV file.
        description: Informational bio text.
    """
    voice_id: str
    display_name: str
    gender: str
    language: str
    is_cloned: bool = False
    sample_audio_path: Optional[Path] = None
    description: str = ""


@dataclass(frozen=True)
class SubtitleStyleDisplayState:
    """Configured visualization overrides of subtitle tracks.

    Attributes:
        font_name: Family name of the font.
        font_size: Standard display size.
        primary_color: Main fill color hex code (e.g. '#FFFFFF').
        outline_color: Text stroke outline border color.
        outline_width: Pixel stroke width.
        shadow_color: Drop shadow color.
        alignment: SSA/ASS layout position code.
        karaoke_enabled: Active dynamic coloring tracking loops.
    """
    font_name: str
    font_size: int
    primary_color: str
    outline_color: str
    outline_width: float
    shadow_color: str
    alignment: int
    karaoke_enabled: bool = False


@dataclass(frozen=True)
class RenderSettingsDisplayState:
    """Configured settings packaging parameters for rendering.

    Attributes:
        aspect_ratio: Ratio layout preset.
        resolution: Resolution layout preset.
        frame_rate: Frame rate count.
        scaling_mode: Scaling adjustment strategy (pad, crop, stretch).
        encoder_preference: Auto/GPU/CPU selection preference.
        hardware_acceleration: GPU driver acceleration system.
        logo_opacity: Opacity ratio for corner watermark logo (0.0 to 1.0).
        logo_scale: Scale ratio for corner watermark logo (0.0 to 1.0).
        watermark_opacity: Opacity ratio for full-screen watermark (0.0 to 1.0).
        background_music_volume: Soundtrack volume ratio (0.0 to 1.0).
    """
    aspect_ratio: str
    resolution: str
    frame_rate: int
    scaling_mode: str
    encoder_preference: str
    hardware_acceleration: str
    logo_opacity: float
    logo_scale: float
    watermark_opacity: float
    background_music_volume: float


@dataclass(frozen=True)
class AssetDisplayItem:
    """Lightweight representation of registered project resources.

    Attributes:
        asset_id: Unique asset tracker.
        asset_type: File categorization (source, video, voice, etc.).
        display_name: Visual label.
        file_size_formatted: Readable string size (e.g. "12.4 MB").
        relative_path: Safe workspace location file path string.
        storage_mode: Disk copying state (internal, external).
        source_type: Disk mapping state (imported, generated).
        duration_formatted: Playback latency formatted string if relevant.
        dimensions: Grid layout width x height string if relevant.
        content_hash: Content verification identifier hash.
        modified_at: Modification datetime on disk.
        is_available: False if files are missing or offline on disk.
    """
    asset_id: str
    asset_type: str
    display_name: str
    file_size_formatted: str
    relative_path: str
    storage_mode: str
    source_type: str
    duration_formatted: Optional[str] = None
    dimensions: Optional[str] = None
    content_hash: Optional[str] = None
    modified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_available: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "modified_at", _ensure_utc(self.modified_at))


@dataclass(frozen=True)
class DiagnosticEntry:
    """Detailed visual logging structure representing a single logger transaction.

    Attributes:
        timestamp: Time logging.
        level: Severity (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        logger_name: Emitting class name indicator.
        message: Descriptive log text.
        exception_info: Debug information.
    """
    timestamp: datetime
    level: str
    logger_name: str
    message: str
    exception_info: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


@dataclass(frozen=True)
class WindowSettings:
    """Desktop startup geometry options.

    Attributes:
        width: Desktop width boundary.
        height: Desktop height boundary.
        is_maximized: Launch maximized toggle.
        x: Desktop coordinate horizontal layout offset.
        y: Desktop coordinate vertical layout offset.
    """
    width: int = 1280
    height: int = 720
    is_maximized: bool = False
    x: Optional[int] = None
    y: Optional[int] = None


@dataclass(frozen=True)
class UIPreferences:
    """Centralized user profile preferences.

    Attributes:
        theme_mode: Light, Dark, or System.
        accent_color: Accent color scheme.
        sidebar_state: Sidebar expand or collapse.
        dense_mode: Minimize layouts padding.
        language: Selected Vietnamese or English language locale string.
    """
    theme_mode: ThemeMode = ThemeMode.SYSTEM
    accent_color: AccentColor = AccentColor.BLUE
    sidebar_state: SidebarState = SidebarState.EXPANDED
    dense_mode: bool = False
    language: str = "vi"


@dataclass(frozen=True)
class ApplicationViewState:
    """Complete application presentation state representing the frontend snapshot.

    Attributes:
        current_page: Active visible page.
        status: Operational descriptive tag (e.g. "Idle", "Rendering...").
        running_task_count: Active asynchronous background jobs count.
        preferences: Theme preferences profile.
        window_settings: Custom geometry coordinates.
        active_project_id: Open project ID.
        active_project_name: Open project Name.
        is_project_dirty: Open project dirty unsaved changes tag.
        active_workflow_id: Open workflow compiling ID.
        active_workflow_status: Open workflow status.
    """
    current_page: ApplicationPage = ApplicationPage.DASHBOARD
    status: str = "Idle"
    running_task_count: int = 0
    preferences: UIPreferences = field(default_factory=UIPreferences)
    window_settings: WindowSettings = field(default_factory=WindowSettings)
    active_project_id: Optional[str] = None
    active_project_name: Optional[str] = None
    is_project_dirty: bool = False
    active_workflow_id: Optional[str] = None
    active_workflow_status: Optional[str] = None
