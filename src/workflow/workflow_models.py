"""Strongly typed domain and operational models for Module 12: Workflow Engine.

This module defines all Enums and Dataclasses representing workflow types, modes,
priorities, request payloads, steps, state management, progress tracking, results, and diagnostics.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.workflow.exceptions import InvalidWorkflowRequestError, WorkflowValidationError


class WorkflowType(str, Enum):
    """Supported pipeline workflow categories."""
    FULL_VIDEO = "full_video"
    SCRIPT_ONLY = "script_only"
    SPEECH_ONLY = "speech_only"
    SUBTITLE_ONLY = "subtitle_only"
    RENDER_ONLY = "render_only"


class WorkflowMode(str, Enum):
    """Operational mode directing execution behaviors."""
    STANDARD = "standard"
    RESUME = "resume"
    RETRY = "retry"
    REGENERATE = "regenerate"
    DRY_RUN = "dry_run"


class WorkflowStatus(str, Enum):
    """Runtime execution status of a workflow."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    AWAITING_INPUT = "awaiting_input"


class WorkflowStepType(str, Enum):
    """Discrete milestones inside the workflow execution pipeline."""
    INITIALIZE = "initialize"
    VALIDATE_INPUT = "validate_input"
    GENERATE_SCRIPT = "generate_script"
    SELECT_SCRIPT = "select_script"
    GENERATE_SPEECH = "generate_speech"
    GENERATE_SUBTITLES = "generate_subtitles"
    PREPARE_RENDER = "prepare_render"
    RENDER_VIDEO = "render_video"
    VALIDATE_OUTPUT = "validate_output"
    UPDATE_PROJECT = "update_project"
    FINALIZE = "finalize"
    CLEANUP = "cleanup"


class WorkflowStepStatus(str, Enum):
    """Status tracking for individual workflow steps."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class WorkflowFailurePolicy(str, Enum):
    """Error handling policy when a step fails."""
    FAIL_FAST = "fail_fast"
    RETRY_THEN_FAIL = "retry_then_fail"
    COMPENSATE_AND_FAIL = "compensate_and_fail"
    KEEP_COMPLETED_OUTPUTS = "keep_completed_outputs"
    COMPLETE_WITH_WARNINGS = "complete_with_warnings"


class RetryStrategy(str, Enum):
    """Delay calculation strategy for step retries."""
    FIXED = "fixed"
    EXPONENTIAL_BACKOFF = "exponential_backoff"


class CompensationStrategy(str, Enum):
    """Strategy for rolling back changes and cleaning resources on failure."""
    CLEAN_ALL = "clean_all"
    CLEAN_TEMPORARY = "clean_temporary"
    NONE = "none"


class WorkflowPriority(int, Enum):
    """Scheduling priority tier for queued workflows."""
    LOW = 10
    MEDIUM = 20
    HIGH = 30


# Helper function to ensure datetime is timezone-aware and UTC formatted
def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _make_serializable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(x) for x in obj]
    elif isinstance(obj, (set, tuple)):
        return [_make_serializable(x) for x in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, Enum):
        return obj.value
    return obj



@dataclass(frozen=True)
class RetryPolicy:
    """Configurable retry behaviors for recoverable step failures.

    Attributes:
        strategy: Time spacing algorithm (fixed vs. backoff).
        max_retries: Limit of attempt loops.
        initial_delay_seconds: Base delay spacing.
        max_delay_seconds: Maximum spacing threshold under exponential growth.
    """
    strategy: RetryStrategy = RetryStrategy.FIXED
    max_retries: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 10.0

    def __post_init__(self) -> None:
        if self.max_retries < 0:
            raise InvalidWorkflowRequestError("max_retries must be non-negative.")
        if self.initial_delay_seconds < 0:
            raise InvalidWorkflowRequestError("initial_delay_seconds must be non-negative.")
        if self.max_delay_seconds < self.initial_delay_seconds:
            raise InvalidWorkflowRequestError("max_delay_seconds must be >= initial_delay_seconds.")


@dataclass(frozen=True)
class WorkflowOptions:
    """Consolidated execution policies and tracking constraints.

    Attributes:
        failure_policy: Action path when a step encounters a fatal error.
        compensation_strategy: Resource cleanup policy on aborts.
        retry_policy: Common policy applied to recoverable step failures.
        priority: Processing weight for queuing.
        timeout_seconds: hard execution budget limit.
        save_project_on_completion: Automatically trigger saving in Project Manager.
        allow_cpu_fallback: Allow lower modules to use CPU on GPU OOMs.
    """
    failure_policy: WorkflowFailurePolicy = WorkflowFailurePolicy.FAIL_FAST
    compensation_strategy: CompensationStrategy = CompensationStrategy.CLEAN_TEMPORARY
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    priority: WorkflowPriority = WorkflowPriority.MEDIUM
    timeout_seconds: float = 1200.0
    save_project_on_completion: bool = True
    allow_cpu_fallback: bool = True

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise InvalidWorkflowRequestError("timeout_seconds must be positive.")


@dataclass(frozen=True)
class WorkflowConstraints:
    """Analytical constraints restricting acceptable inputs and ranges.

    Attributes:
        max_script_length_characters: character budget for Module 07 prompt.
        max_video_duration_seconds: Video duration ceiling.
        required_languages: Supported language codes.
    """
    max_script_length_characters: int = 5000
    max_video_duration_seconds: float = 300.0
    required_languages: List[str] = field(default_factory=lambda: ["vi", "en"])


@dataclass(frozen=True)
class WorkflowProjectContext:
    """Association context binding a workflow session to an active Project workspace.

    Attributes:
        project_id: Open target project identifier.
        workspace_root: Parent project directory.
        relative_output_dir: Subdirectory inside workspace root to place final renders.
    """
    project_id: str
    workspace_root: Path
    relative_output_dir: Path = field(default_factory=lambda: Path("generated/renders"))

    def __post_init__(self) -> None:
        if not self.project_id.strip():
            raise InvalidWorkflowRequestError("project_id cannot be empty inside context.")


# Structural Inputs Mapping References
@dataclass(frozen=True)
class WorkflowInputReferences:
    """User-supplied inputs and override parameters for the pipeline steps.

    Attributes:
        product_name: Product name for script generation.
        product_description: Product features or marketing angles.
        target_audience: Segment keyword descriptors.
        script_style: Narrative structure template (e.g. 'Problem Solution').
        selected_script_id: Preselected script reference to skip script-gen.
        voice_id: TTS voice selection.
        reference_voice_path: Optional local path to WAV for cloning.
        reference_transcript: Optional cloned reference text.
        subtitle_style: Subtitle preset template.
        video_inputs: Video clip source paths.
        image_inputs: Image slide source paths.
        background_music_path: Optional soundtrack path.
        logo_path: Brand image overlay path.
    """
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    target_audience: Optional[str] = None
    script_style: Optional[str] = None
    selected_script_id: Optional[str] = None
    voice_id: Optional[str] = None
    reference_voice_path: Optional[Path] = None
    reference_transcript: Optional[str] = None
    subtitle_style: Optional[str] = None
    video_inputs: List[Path] = field(default_factory=list)
    image_inputs: List[Path] = field(default_factory=list)
    background_music_path: Optional[Path] = None
    logo_path: Optional[Path] = None


@dataclass(frozen=True)
class WorkflowRequest:
    """The complete public request payload to execute a specific workflow.

    Attributes:
        workflow_id: Unique task tracking identifier.
        workflow_type: Target category of execution.
        project_context: Associated project binding parameters.
        inputs: Input data.
        options: Behavior options and policies.
        mode: Initial mode directing step resumption or dry-runs.
    """
    workflow_id: str
    workflow_type: WorkflowType
    project_context: WorkflowProjectContext
    inputs: WorkflowInputReferences = field(default_factory=WorkflowInputReferences)
    options: WorkflowOptions = field(default_factory=WorkflowOptions)
    mode: WorkflowMode = WorkflowMode.STANDARD

    def __post_init__(self) -> None:
        if not self.workflow_id.strip():
            raise InvalidWorkflowRequestError("workflow_id cannot be empty.")


@dataclass(frozen=True)
class BatchWorkflowRequest:
    """Collection payload wrapping multiple standalone requests for batch execution.

    Attributes:
        batch_id: Track identifier for the batch.
        requests: Sequence of workflow requests.
        concurrency_limit: Maximum concurrent worker execution threads.
        fail_fast: Abort remaining items immediately if one fails.
    """
    batch_id: str
    requests: List[WorkflowRequest]
    concurrency_limit: int = 2
    fail_fast: bool = False

    def __post_init__(self) -> None:
        if not self.batch_id.strip():
            raise InvalidWorkflowRequestError("batch_id cannot be empty.")
        if not self.requests:
            raise InvalidWorkflowRequestError("requests sequence cannot be empty inside BatchWorkflowRequest.")
        if self.concurrency_limit <= 0:
            raise InvalidWorkflowRequestError("concurrency_limit must be strictly positive.")


# Output References compiled between Steps
@dataclass(frozen=True)
class WorkflowOutputReferences:
    """Intermediate and final file output paths generated during step transitions.

    Attributes:
        script_id: ID of the generated script.
        script_text: text body of script.
        speech_id: ID of the generated speech asset.
        speech_audio_path: output path to compiled WAV.
        subtitle_id: ID of the generated subtitle track.
        subtitle_path: output path to SRT/ASS file.
        render_id: ID of final render task.
        final_video_path: output path to finalized MP4.
    """
    script_id: Optional[str] = None
    script_text: Optional[str] = None
    speech_id: Optional[str] = None
    speech_audio_path: Optional[Path] = None
    subtitle_id: Optional[str] = None
    subtitle_path: Optional[Path] = None
    render_id: Optional[str] = None
    final_video_path: Optional[Path] = None


@dataclass(frozen=True)
class WorkflowStepDefinition:
    """Static graph model defining a single step dependencies and execution properties.

    Attributes:
        step_type: Standard task classification.
        dependencies: list of step types that must execute successfully first.
        retry_eligible: Allow retry procedures on errors.
        is_optional: Failures on this step do not crash the pipeline if True.
    """
    step_type: WorkflowStepType
    dependencies: List[WorkflowStepType] = field(default_factory=list)
    retry_eligible: bool = True
    is_optional: bool = False


@dataclass(frozen=True)
class WorkflowDefinition:
    """The resolved pipeline graph defining step order.

    Attributes:
        workflow_type: Associated workflow category.
        steps: Map tracking step layout settings indexed by step_type.
    """
    workflow_type: WorkflowType
    steps: Dict[WorkflowStepType, WorkflowStepDefinition]


@dataclass(frozen=True)
class WorkflowStepState:
    """Operational metrics tracking the real-time execution trace of a step.

    Attributes:
        step_type: Targeted step classification.
        status: Progress state of the step.
        started_at: Activation timestamp.
        completed_at: Finish timestamp.
        execution_duration_seconds: Computes elapsed latency.
        retry_count: Triggered retry loops counts.
        error_message: Summary diagnostic traceback on failure.
        warnings: List of minor non-fatal flags.
    """
    step_type: WorkflowStepType
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_duration_seconds: float = 0.0
    retry_count: int = 0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.started_at is not None:
            object.__setattr__(self, "started_at", _ensure_utc(self.started_at))
        if self.completed_at is not None:
            object.__setattr__(self, "completed_at", _ensure_utc(self.completed_at))


@dataclass(frozen=True)
class WorkflowState:
    """Serializable snapshot documenting the state of an active workflow.

    Attributes:
        workflow_id: Unique tracking tracker.
        workflow_type: Associated pipeline category.
        status: Cumulative execution status.
        project_id: Bound project ID.
        request_snapshot: Request payload backup.
        current_step: Current processing step type.
        step_states: Map cataloging the run history of individual steps.
        outputs: Intermediate and final output path registrations.
        created_at: Creation timestamp.
        updated_at: Last state update timestamp.
        started_at: Process start timestamp.
        completed_at: Process completion timestamp.
        resume_count: Total count of session loads.
    """
    workflow_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus
    project_id: str
    request_snapshot: WorkflowRequest
    current_step: Optional[WorkflowStepType] = None
    step_states: Dict[WorkflowStepType, WorkflowStepState] = field(default_factory=dict)
    outputs: WorkflowOutputReferences = field(default_factory=WorkflowOutputReferences)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    resume_count: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", _ensure_utc(self.created_at))
        object.__setattr__(self, "updated_at", _ensure_utc(self.updated_at))
        if self.started_at is not None:
            object.__setattr__(self, "started_at", _ensure_utc(self.started_at))
        if self.completed_at is not None:
            object.__setattr__(self, "completed_at", _ensure_utc(self.completed_at))


@dataclass(frozen=True)
class WorkflowProgress:
    """Telemetry structure documenting immediate execution percentage metrics.

    Attributes:
        workflow_id: Unique task tracker.
        status: Cumulative state.
        percentage: Progress clamped between 0.0 and 100.0.
        elapsed_seconds: Operational duration in seconds.
        estimated_remaining_seconds: Approximated remaining cost budget.
        current_step: Processing step.
        status_message: Informational summary log string.
        timestamp: Creation timestamp.
    """
    workflow_id: str
    status: WorkflowStatus
    percentage: float
    elapsed_seconds: float
    estimated_remaining_seconds: Optional[float] = None
    current_step: Optional[WorkflowStepType] = None
    status_message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "percentage", max(0.0, min(100.0, self.percentage)))
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


# Step Execution Payloads
@dataclass(frozen=True)
class StepExecutionRequest:
    """Operational payload invoking a step handler.

    Attributes:
        workflow_id: Unique parent tracker.
        step_type: Target step type.
        project_context: Bound workspace context parameters.
        inputs: Input data.
        previous_outputs: Cumulative output parameters generated in prior steps.
        allow_cpu_fallback: Toggle directing GPU recovery procedures.
    """
    workflow_id: str
    step_type: WorkflowStepType
    project_context: WorkflowProjectContext
    inputs: WorkflowInputReferences
    previous_outputs: WorkflowOutputReferences
    allow_cpu_fallback: bool = True


@dataclass(frozen=True)
class StepExecutionResult:
    """Result object documenting step execution outcomes.

    Attributes:
        step_type: Target step type.
        status: Execution status.
        outputs: Updated outputs compiled during this step.
        execution_duration_seconds: Computes elapsed latency.
        warnings: Captured minor anomalies.
        error_message: System traceback description on failure.
    """
    step_type: WorkflowStepType
    status: WorkflowStepStatus
    outputs: WorkflowOutputReferences
    execution_duration_seconds: float = 0.0
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass(frozen=True)
class CompensationAction:
    """Discrete rollback operation cataloged inside CompensationManager.

    Attributes:
        step_type: Original generating step type.
        action_description: Informational details log descriptive string.
        timestamp: Execution timestamp.
        is_successful: Operational success status.
    """
    step_type: WorkflowStepType
    action_description: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_successful: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "timestamp", _ensure_utc(self.timestamp))


@dataclass(frozen=True)
class ResumeInformation:
    """Historical checkpoint analytics parsing the potential to resume saved workflows.

    Attributes:
        workflow_id: Target workflow tracker.
        project_id: Project identifier.
        last_completed_step: Latest successfully committed milestone.
        resumable_status: Indicates whether data references still exist on disk.
        missing_outputs_detected: Sequence of step types whose outputs must be regenerated.
    """
    workflow_id: str
    project_id: str
    last_completed_step: Optional[WorkflowStepType]
    resumable_status: bool
    missing_outputs_detected: List[WorkflowStepType] = field(default_factory=list)


@dataclass(frozen=True)
class WorkflowValidationIssue:
    """A discrete parameter discrepancy found by the WorkflowValidator.

    Attributes:
        severity: Criticality classification ("error", "warning").
        code: Identifier categorizing issue category.
        message: Readable summary log descriptive string.
    """
    severity: str
    code: str
    message: str

    def __post_init__(self) -> None:
        if self.severity not in ("error", "warning"):
            raise WorkflowValidationError(f"Invalid validation severity: {self.severity}")


@dataclass(frozen=True)
class WorkflowValidationReport:
    """Consolidated diagnostic report assessing readiness parameters of a request.

    Attributes:
        is_valid: True if no issues of 'error' severity are found.
        issues: Full sequence of findings.
        checked_at: Verification timestamp.
    """
    is_valid: bool
    issues: List[WorkflowValidationIssue] = field(default_factory=list)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "checked_at", _ensure_utc(self.checked_at))
        has_error = any(issue.severity == "error" for issue in self.issues)
        if has_error and self.is_valid:
            object.__setattr__(self, "is_valid", False)


@dataclass(frozen=True)
class WorkflowResult:
    """The final completed results model mapping a pipeline session execution.

    Attributes:
        workflow_id: Track identifier.
        workflow_type: Workflow pipeline category.
        mode: Run mode.
        status: Cumulative final outcome status.
        project_id: Bound project ID.
        started_at: Activation timestamp.
        completed_at: Finish timestamp.
        duration_seconds: Processing runtime cost.
        final_step: Last step executed.
        step_results: Trace maps cataloging results of individual steps.
        outputs: Output References.
        progress: Terminal progress snapshot.
        resume_info: Accompanying resume stats.
        warnings: Aggregate minor pipeline warnings.
        error_message: Final diagnostics trace on crash or failures.
    """
    workflow_id: str
    workflow_type: WorkflowType
    mode: WorkflowMode
    status: WorkflowStatus
    project_id: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    final_step: Optional[WorkflowStepType]
    step_results: Dict[WorkflowStepType, StepExecutionResult] = field(default_factory=dict)
    outputs: WorkflowOutputReferences = field(default_factory=WorkflowOutputReferences)
    progress: Optional[WorkflowProgress] = None
    resume_info: Optional[ResumeInformation] = None
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "started_at", _ensure_utc(self.started_at))
        object.__setattr__(self, "completed_at", _ensure_utc(self.completed_at))

    def to_dict(self) -> Dict[str, Any]:
        """Convert results payload into serializable map structure."""
        return _make_serializable(asdict(self))


@dataclass(frozen=True)
class BatchWorkflowResult:
    """Outcome report describing overall execution properties of a workflow batch.

    Attributes:
        batch_id: Targeted batch tracking identifier.
        status: Aggregate outcome status.
        results: Collection of individual WorkflowResult models.
        total_count: Total request items.
        success_count: Successfully compiled items.
        failure_count: Failed items.
        cancelled_count: Items cancelled before or during processing.
        awaiting_input_count: Items paused awaiting manual selection or input.
        total_duration_seconds: Cumulative elapsed process time.
        warnings: Captured warnings.
    """
    batch_id: str
    status: WorkflowStatus
    results: List[WorkflowResult]
    total_count: int
    success_count: int
    failure_count: int
    cancelled_count: int
    awaiting_input_count: int
    total_duration_seconds: float
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch result into serializable map structure."""
        return _make_serializable(asdict(self))



@dataclass(frozen=True)
class WorkflowHealthStatus:
    """Structural report analyzing system-wide workflow engines readiness status.

    Attributes:
        is_healthy: Cumulative operational status.
        status_message: Informational diagnostics summary log string.
        last_checked_at: Precise checking timestamp.
    """
    is_healthy: bool
    status_message: str
    last_checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        object.__setattr__(self, "last_checked_at", _ensure_utc(self.last_checked_at))
