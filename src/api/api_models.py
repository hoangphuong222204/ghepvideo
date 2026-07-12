"""Pydantic v2 response and request schemas for Module 14: FastAPI Service.

This module defines all HTTP request and response models, schemas, enums, and validators
for the FastAPI application. All models use Pydantic v2 and enforce strict typing.
"""

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# =====================================================================
# ENUMS
# =====================================================================

class APIStatus(str, Enum):
    """The operational status of the API or its components."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class APIErrorCode(str, Enum):
    """Stable identifiers for specific API error scenarios."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    IDEMPOTENCY_CONFLICT = "IDEMPOTENCY_CONFLICT"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DOWNSTREAM_ERROR = "DOWNSTREAM_ERROR"
    PROJECT_ERROR = "PROJECT_ERROR"
    ASSET_ERROR = "ASSET_ERROR"
    WORKFLOW_ERROR = "WORKFLOW_ERROR"


class AuthenticationScheme(str, Enum):
    """Supported API authentication methods."""
    API_KEY = "API_KEY"
    BEARER = "BEARER"
    NONE = "NONE"


class Permission(str, Enum):
    """API permissions required for specific endpoints."""
    HEALTH_READ = "HEALTH_READ"
    PROJECT_READ = "PROJECT_READ"
    PROJECT_WRITE = "PROJECT_WRITE"
    PROJECT_DELETE = "PROJECT_DELETE"
    ASSET_READ = "ASSET_READ"
    ASSET_WRITE = "ASSET_WRITE"
    WORKFLOW_READ = "WORKFLOW_READ"
    WORKFLOW_EXECUTE = "WORKFLOW_EXECUTE"
    WORKFLOW_CANCEL = "WORKFLOW_CANCEL"
    SETTINGS_READ = "SETTINGS_READ"
    SETTINGS_WRITE = "SETTINGS_WRITE"
    DIAGNOSTICS_READ = "DIAGNOSTICS_READ"


class ResourceType(str, Enum):
    """System resource categories managed via the API."""
    PROJECT = "PROJECT"
    ASSET = "ASSET"
    WORKFLOW = "WORKFLOW"
    SETTINGS = "SETTINGS"
    DIAGNOSTIC = "DIAGNOSTIC"


class WorkflowEventType(str, Enum):
    """The categories of progress events emitted during workflow execution."""
    WORKFLOW_CREATED = "WORKFLOW_CREATED"
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    STEP_STARTED = "STEP_STARTED"
    STEP_PROGRESS = "STEP_PROGRESS"
    STEP_COMPLETED = "STEP_COMPLETED"
    STEP_FAILED = "STEP_FAILED"
    STEP_RETRYING = "STEP_RETRYING"
    WORKFLOW_AWAITING_INPUT = "WORKFLOW_AWAITING_INPUT"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    WORKFLOW_CANCELLED = "WORKFLOW_CANCELLED"
    HEARTBEAT = "HEARTBEAT"


class ProgressTransportType(str, Enum):
    """Protocol used to deliver real-time progress to API clients."""
    SSE = "SSE"
    WEBSOCKET = "WEBSOCKET"
    POLLING = "POLLING"


# =====================================================================
# COMMON UTILITY SCHEMAS
# =====================================================================

class PaginationMetadata(BaseModel):
    """Standard metadata enclosing paginated result lists."""
    total_count: int = Field(..., description="Total number of items matching query.")
    page: int = Field(..., description="Current page index.")
    page_size: int = Field(..., description="Number of items per page.")
    total_pages: int = Field(..., description="Total computed pages available.")
    has_next: bool = Field(..., description="True if there is a next page.")
    has_previous: bool = Field(..., description="True if there is a previous page.")


class APIErrorDetail(BaseModel):
    """A detailed sub-error tip, primarily used for validation issues."""
    field: Optional[str] = Field(None, description="The target input field name or JSON path.")
    message: str = Field(..., description="The user-friendly validation feedback message.")
    code: Optional[str] = Field(None, description="Specific error classification code.")


class APIErrorResponse(BaseModel):
    """Standard error response payload returned on all API failures."""
    error_code: APIErrorCode = Field(..., description="Stable system error code.")
    message: str = Field(..., description="Human-readable high-level failure description.")
    status_code: int = Field(..., description="HTTP status code duplicate.")
    correlation_id: str = Field(..., description="Tracing code matching server telemetry logs.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: List[APIErrorDetail] = Field(default_factory=list, description="Optional nested error list.")
    retryable: bool = Field(False, description="True if clients can retry this request unmodified.")
    retry_after_seconds: Optional[int] = Field(None, description="Time to wait before retrying.")


class APISuccessResponse(BaseModel):
    """Standard envelope wrapping successful mutations or actions."""
    success: bool = Field(True, description="Indicates if the operation was successful.")
    message: Optional[str] = Field(None, description="Optional informational display message.")
    correlation_id: str = Field(..., description="Correlation ID for auditing.")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Optional[Any] = Field(None, description="The core returned payload of the resource.")


# =====================================================================
# SYSTEM HEALTH SCHEMAS
# =====================================================================

class HealthResponse(BaseModel):
    """Response enclosing aggregate server health checks."""
    status: APIStatus = Field(..., description="Cumulative service health status.")
    version: str = Field(..., description="API service version string.")
    timestamp: datetime = Field(..., description="Time of assessment.")
    details: Dict[str, Any] = Field(default_factory=dict, description="Nested components statuses.")


class LivenessResponse(BaseModel):
    """Response for fast liveness probe checks."""
    status: str = Field("ok", description="Liveness confirmation string.")


class ReadinessResponse(BaseModel):
    """Response enclosing readiness of dependencies."""
    status: str = Field("ready", description="Readiness confirmation string.")
    dependencies: Dict[str, str] = Field(default_factory=dict, description="Statuses of connected modules.")


# =====================================================================
# PROJECT LIFECYCLE SCHEMAS
# =====================================================================

class ProjectCreateRequest(BaseModel):
    """Payload to create a new project workspace."""
    name: str = Field(..., min_length=1, max_length=255, description="Visual name for the project.")
    description: str = Field("", max_length=1000, description="Brief descriptive summary of purpose.")
    workspace_parent_dir: Optional[str] = Field(None, description="Optional host-specific parent path.")


class ProjectOpenRequest(BaseModel):
    """Payload to open an existing project workspace from disk."""
    project_id: Optional[str] = Field(None, description="Optional expected project ID to verify.")
    path: str = Field(..., description="Path pointing to project folder or project.json.")


class ProjectSaveAsRequest(BaseModel):
    """Payload to copy and persist the project to a new workspace location."""
    new_name: str = Field(..., min_length=1, max_length=255, description="New visual project name.")
    new_path: str = Field(..., description="Target directory on disk.")


class ProjectCloseRequest(BaseModel):
    """Payload to close the active project workspace."""
    save_before_close: bool = Field(True, description="Save changes automatically before closing.")


class ProjectDeleteRequest(BaseModel):
    """Payload to delete an inactive project workspace."""
    confirm_token: str = Field(..., description="Anti-accidental delete validation token.")
    delete_workspace_files: bool = Field(False, description="Permanently delete project workspace directory.")


class ProjectSummaryResponse(BaseModel):
    """Lightweight summary model for project listings."""
    project_id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    workspace_path: str = Field(...)
    is_dirty: bool = Field(...)
    is_read_only: bool = Field(...)
    last_saved_at: datetime = Field(...)


class ProjectDetailResponse(BaseModel):
    """Detailed model enclosing active project status and metrics."""
    project_id: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    workspace_path: str = Field(...)
    is_dirty: bool = Field(...)
    is_read_only: bool = Field(...)
    created_at: datetime = Field(...)
    modified_at: datetime = Field(...)
    last_saved_at: datetime = Field(...)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    assets_count: int = Field(0)


class ProjectValidationResponse(BaseModel):
    """Diagnostic report validation of project parameters."""
    is_valid: bool = Field(...)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


# =====================================================================
# PROJECT ASSET SCHEMAS
# =====================================================================

class AssetImportRequest(BaseModel):
    """Payload to import an external file into the workspace."""
    source_path: str = Field(..., description="Absolute local path of file to import.")
    asset_type: str = Field(..., description="Asset type e.g. video, image, audio, voice.")
    copy_to_workspace: bool = Field(True, description="Copy file to project workspace directory.")
    custom_name: Optional[str] = Field(None, description="Optional override for filename.")


class ExternalAssetRegistrationRequest(BaseModel):
    """Payload to link a file without copying it into the workspace."""
    absolute_path: str = Field(..., description="Absolute local path of the external file.")
    asset_type: str = Field(..., description="Asset type e.g. video, image, audio, voice.")
    custom_name: Optional[str] = Field(None, description="Optional custom label.")


class AssetDeleteRequest(BaseModel):
    """Payload to remove an asset reference."""
    delete_from_disk: bool = Field(False, description="Delete file from disk if located inside workspace.")


class AssetResponse(BaseModel):
    """Standard details envelope enclosing a registered project asset."""
    asset_id: str = Field(...)
    asset_type: str = Field(...)
    display_name: str = Field(...)
    relative_path: str = Field(...)
    absolute_path: str = Field(...)
    file_size: int = Field(...)
    file_size_formatted: str = Field(...)
    storage_mode: str = Field(...)
    source_type: str = Field(...)
    duration_seconds: Optional[float] = Field(None)
    duration_formatted: Optional[str] = Field(None)
    dimensions: Optional[str] = Field(None)
    content_hash: Optional[str] = Field(None)
    modified_at: datetime = Field(...)
    is_available: bool = Field(True)


class AssetListResponse(BaseModel):
    """Paginated collection of asset response envelopes."""
    assets: List[AssetResponse] = Field(default_factory=list)
    pagination: PaginationMetadata = Field(...)


# =====================================================================
# WORKFLOW EXECUTION SCHEMAS
# =====================================================================

class WorkflowInputReferencesRequest(BaseModel):
    """User-supplied inputs and parameters directing pipeline stages."""
    product_name: Optional[str] = Field(None, max_length=255)
    product_description: Optional[str] = Field(None, max_length=5000)
    target_audience: Optional[str] = Field(None, max_length=1000)
    script_style: Optional[str] = Field(None, max_length=100)
    selected_script_id: Optional[str] = Field(None)
    voice_id: Optional[str] = Field(None)
    reference_voice_path: Optional[str] = Field(None)
    reference_transcript: Optional[str] = Field(None)
    subtitle_style: Optional[str] = Field(None)
    video_inputs: List[str] = Field(default_factory=list)
    image_inputs: List[str] = Field(default_factory=list)
    background_music_path: Optional[str] = Field(None)
    logo_path: Optional[str] = Field(None)


class WorkflowOptionsRequest(BaseModel):
    """Configurable behaviors and limits directing step executions."""
    failure_policy: str = Field("fail_fast")
    compensation_strategy: str = Field("clean_temporary")
    retry_max_retries: int = Field(3, ge=0)
    retry_initial_delay: float = Field(1.0, ge=0.0)
    priority: int = Field(20, description="Priority rating: 10=Low, 20=Medium, 30=High.")
    timeout_seconds: float = Field(1200.0, gt=0.0)
    save_project_on_completion: bool = Field(True)
    allow_cpu_fallback: bool = Field(True)


class WorkflowStartRequest(BaseModel):
    """General unified API workflow execution request."""
    workflow_type: str = Field(..., description="Target category: full_video, script_only, speech_only, subtitle_only, render_only.")
    inputs: WorkflowInputReferencesRequest = Field(...)
    options: Optional[WorkflowOptionsRequest] = Field(None)


class FullVideoWorkflowRequest(BaseModel):
    """Payload to trigger a complete video compilation workflow."""
    inputs: WorkflowInputReferencesRequest = Field(...)
    options: Optional[WorkflowOptionsRequest] = Field(None)


class ScriptOnlyWorkflowRequest(BaseModel):
    """Payload to trigger script generation only."""
    inputs: WorkflowInputReferencesRequest = Field(...)
    options: Optional[WorkflowOptionsRequest] = Field(None)


class SpeechOnlyWorkflowRequest(BaseModel):
    """Payload to trigger speech synthesis only."""
    inputs: WorkflowInputReferencesRequest = Field(...)
    options: Optional[WorkflowOptionsRequest] = Field(None)


class SubtitleOnlyWorkflowRequest(BaseModel):
    """Payload to trigger subtitle timeline generation only."""
    inputs: WorkflowInputReferencesRequest = Field(...)
    options: Optional[WorkflowOptionsRequest] = Field(None)


class RenderOnlyWorkflowRequest(BaseModel):
    """Payload to trigger video rendering only."""
    inputs: WorkflowInputReferencesRequest = Field(...)
    options: Optional[WorkflowOptionsRequest] = Field(None)


class WorkflowResumeRequest(BaseModel):
    """Payload to resume an interrupted workflow from its last saved state."""
    overrides: Optional[WorkflowInputReferencesRequest] = Field(None, description="Optional inputs overrides.")


class WorkflowRetryRequest(BaseModel):
    """Payload to retry the current failed workflow step."""
    step_type: Optional[str] = Field(None, description="Optional step classification to retry specifically.")


class WorkflowRegenerateStepRequest(BaseModel):
    """Payload to invalidate a step output and trigger regeneration from that point."""
    step_type: str = Field(..., description="Step type target (e.g. generate_script, generate_speech).")
    preserve_old_outputs: bool = Field(True, description="Save invalidated outputs as historical assets.")


class WorkflowCancelRequest(BaseModel):
    """Payload to request cooperative workflow cancellation."""
    reason: Optional[str] = Field(None, max_length=500, description="Optional cancellation reason.")


class WorkflowInputResponseRequest(BaseModel):
    """Payload providing manual feedback or parameters to a paused AWAITING_INPUT step."""
    step_type: str = Field(..., description="The paused step type awaiting interaction.")
    response_data: Dict[str, Any] = Field(..., description="Validation payload matching step requirements.")


# =====================================================================
# WORKFLOW RESPONSE SCHEMAS
# =====================================================================

class StepExecutionResultResponse(BaseModel):
    """Response enclosing execution status and latency metrics of a step."""
    step_type: str = Field(...)
    status: str = Field(...)
    execution_duration_seconds: float = Field(0.0)
    warnings: List[str] = Field(default_factory=list)
    error_message: Optional[str] = Field(None)
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Intermediate output paths or IDs compiled.")


class WorkflowProgressResponse(BaseModel):
    """Unified progress telemetries schema."""
    workflow_id: str = Field(...)
    status: str = Field(...)
    percentage: float = Field(...)
    elapsed_seconds: float = Field(...)
    estimated_remaining_seconds: Optional[float] = Field(None)
    current_step: Optional[str] = Field(None)
    status_message: str = Field("")
    timestamp: datetime = Field(...)


class ResumeInformationResponse(BaseModel):
    """Response diagnostics explaining workflow resumption possibility."""
    workflow_id: str = Field(...)
    project_id: str = Field(...)
    last_completed_step: Optional[str] = Field(None)
    resumable_status: bool = Field(...)
    missing_outputs_detected: List[str] = Field(default_factory=list)


class WorkflowOutputReferencesResponse(BaseModel):
    """Output paths compiled during workflow execution."""
    script_id: Optional[str] = Field(None)
    script_text: Optional[str] = Field(None)
    speech_id: Optional[str] = Field(None)
    speech_audio_path: Optional[str] = Field(None)
    subtitle_id: Optional[str] = Field(None)
    subtitle_path: Optional[str] = Field(None)
    render_id: Optional[str] = Field(None)
    final_video_path: Optional[str] = Field(None)


class WorkflowResponse(BaseModel):
    """The terminal workflow outcome schema."""
    workflow_id: str = Field(...)
    workflow_type: str = Field(...)
    mode: str = Field(...)
    status: str = Field(...)
    project_id: str = Field(...)
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    duration_seconds: float = Field(0.0)
    final_step: Optional[str] = Field(None)
    step_results: Dict[str, StepExecutionResultResponse] = Field(default_factory=dict)
    outputs: WorkflowOutputReferencesResponse = Field(...)
    progress: Optional[WorkflowProgressResponse] = Field(None)
    resume_info: Optional[ResumeInformationResponse] = Field(None)
    warnings: List[str] = Field(default_factory=list)
    error_message: Optional[str] = Field(None)


class WorkflowStateResponse(BaseModel):
    """Detailed runtime snapshot representing workflow state records on disk."""
    workflow_id: str = Field(...)
    workflow_type: str = Field(...)
    status: str = Field(...)
    project_id: str = Field(...)
    current_step: Optional[str] = Field(None)
    step_states: Dict[str, Any] = Field(default_factory=dict)
    outputs: WorkflowOutputReferencesResponse = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)
    resume_count: int = Field(0)


class WorkflowEventResponse(BaseModel):
    """Event envelope delivered to Server-Sent Events or WebSockets clients."""
    event_id: str = Field(...)
    workflow_id: str = Field(...)
    event_type: WorkflowEventType = Field(...)
    timestamp: datetime = Field(...)
    sequence_number: int = Field(...)
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific metadata.")


# =====================================================================
# BATCH WORKFLOW SCHEMAS
# =====================================================================

class BatchWorkflowRequest(BaseModel):
    """Payload to trigger concurrent workflow compilations in a batch."""
    batch_id: str = Field(..., description="Unique batch tracking identifier.")
    requests: List[WorkflowStartRequest] = Field(..., description="stand-alone workflow requests list.")
    concurrency_limit: int = Field(2, ge=1, description="Parallel processing thread budget.")
    fail_fast: bool = Field(False, description="Abort unstarted workflows if one item fails.")


class BatchWorkflowResponse(BaseModel):
    """Response wrapping outcomes of a batch process."""
    batch_id: str = Field(...)
    status: str = Field(...)
    results: List[WorkflowResponse] = Field(default_factory=list)
    total_count: int = Field(0)
    success_count: int = Field(0)
    failure_count: int = Field(0)
    cancelled_count: int = Field(0)
    awaiting_input_count: int = Field(0)
    total_duration_seconds: float = Field(0.0)
    warnings: List[str] = Field(default_factory=list)


# =====================================================================
# SETTINGS SCHEMAS
# =====================================================================

class SettingsResponse(BaseModel):
    """Response enclosing editable application settings and preferences."""
    theme_mode: str = Field(...)
    accent_color: str = Field(...)
    dense_mode: bool = Field(...)
    language: str = Field(...)
    additional_settings: Dict[str, Any] = Field(default_factory=dict)


class SettingsUpdateRequest(BaseModel):
    """Payload to update editable settings fields."""
    theme_mode: Optional[str] = Field(None)
    accent_color: Optional[str] = Field(None)
    dense_mode: Optional[bool] = Field(None)
    language: Optional[str] = Field(None)
    additional_settings: Optional[Dict[str, Any]] = Field(None)


# =====================================================================
# DIAGNOSTICS & TELEMETRIES SCHEMAS
# =====================================================================

class ServerInformationResponse(BaseModel):
    """Detailed runtime metrics of the hosting container or machine."""
    os: str = Field(...)
    python_version: str = Field(...)
    api_version: str = Field(...)
    app_version: str = Field(...)
    uptime_seconds: float = Field(...)
    cpu_usage_percent: float = Field(...)
    memory_usage_percent: float = Field(...)


class DiagnosticsResponse(BaseModel):
    """Diagnostic telemetry package reflecting internal operational status."""
    is_healthy: bool = Field(...)
    status_message: str = Field(...)
    server_info: ServerInformationResponse = Field(...)
    module_health: Dict[str, str] = Field(default_factory=dict)
    active_workflows_count: int = Field(0)
    active_project_id: Optional[str] = Field(None)
    recent_warnings_count: int = Field(0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
