"""Focused tests for Module 14 public foundations: exceptions, config, protocols, and api_models.

This test suite validates Pydantic v2 request/response schemas, stable enum values,
timezone-aware datetimes, safe path serialization, secret-field exclusion, the error response shape,
and the public exceptions and imports.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest
from pydantic import ValidationError, SecretStr

# Public import testing
from src.api import (
    # Exceptions
    APIServiceError,
    APIConfigurationError,
    APIInitializationError,
    DependencyResolutionError,
    InvalidAPIRequestError,
    RequestValidationError,
    AuthenticationError,
    MissingCredentialsError,
    InvalidCredentialsError,
    ExpiredCredentialsError,
    AuthorizationError,
    ForbiddenOperationError,
    RateLimitExceededError,
    ResourceNotFoundError,
    ResourceConflictError,
    IdempotencyConflictError,
    InvalidIdempotencyKeyError,
    RequestTimeoutError,
    ServiceUnavailableError,
    DownstreamServiceError,
    ProjectAPIError,
    AssetAPIError,
    WorkflowAPIError,
    WorkflowEventError,
    ProgressStreamError,
    ResponseSerializationError,
    PaginationError,
    MiddlewareError,
    OpenAPIConfigurationError,
    ShutdownError,

    # Models & Enums
    APIStatus,
    APIErrorCode,
    AuthenticationScheme,
    Permission,
    ResourceType,
    WorkflowEventType,
    ProgressTransportType,
    PaginationMetadata,
    APIErrorDetail,
    APIErrorResponse,
    APISuccessResponse,
    HealthResponse,
    LivenessResponse,
    ReadinessResponse,
    ProjectCreateRequest,
    ProjectOpenRequest,
    ProjectSaveAsRequest,
    ProjectCloseRequest,
    ProjectDeleteRequest,
    ProjectSummaryResponse,
    ProjectDetailResponse,
    ProjectValidationResponse,
    AssetImportRequest,
    ExternalAssetRegistrationRequest,
    AssetDeleteRequest,
    AssetResponse,
    AssetListResponse,
    WorkflowInputReferencesRequest,
    WorkflowOptionsRequest,
    WorkflowStartRequest,
    FullVideoWorkflowRequest,
    ScriptOnlyWorkflowRequest,
    SpeechOnlyWorkflowRequest,
    SubtitleOnlyWorkflowRequest,
    RenderOnlyWorkflowRequest,
    WorkflowResumeRequest,
    WorkflowRetryRequest,
    WorkflowRegenerateStepRequest,
    WorkflowCancelRequest,
    WorkflowInputResponseRequest,
    StepExecutionResultResponse,
    WorkflowProgressResponse,
    ResumeInformationResponse,
    WorkflowOutputReferencesResponse,
    WorkflowResponse,
    WorkflowStateResponse,
    WorkflowEventResponse,
    BatchWorkflowRequest,
    BatchWorkflowResponse,
    SettingsResponse,
    SettingsUpdateRequest,
    ServerInformationResponse,
    DiagnosticsResponse,
    CapabilityResponse,
    SecureServiceCredentials,
    SafePathResponse,

    # Protocols
    LoggerProtocol,
    ClockProtocol,
    IdProviderProtocol,
    IdempotencyStoreProtocol,
    RateLimiterBackendProtocol,
    ProgressBrokerProtocol,
    AuthenticationProviderProtocol,
    AuthorizationProviderProtocol,

    # Config
    APIConfig,
)


# =====================================================================
# 1. PUBLIC IMPORTS & EXCEPTION HIERARCHY TESTS
# =====================================================================

def test_public_imports():
    """Verify all expected public assets can be imported from top-level package."""
    assert APIServiceError is not None
    assert APIConfig is not None
    assert APIStatus is not None
    assert LoggerProtocol is not None


def test_exception_hierarchy():
    """Verify custom exception inheritance and raise-catch behavior."""
    # Base check
    assert issubclass(APIConfigurationError, APIServiceError)
    assert issubclass(RequestValidationError, InvalidAPIRequestError)
    assert issubclass(InvalidAPIRequestError, APIServiceError)
    assert issubclass(MissingCredentialsError, AuthenticationError)
    assert issubclass(AuthenticationError, APIServiceError)
    assert issubclass(ForbiddenOperationError, AuthorizationError)
    assert issubclass(AuthorizationError, APIServiceError)

    # Trigger exception handling flow
    with pytest.raises(APIServiceError):
        raise APIInitializationError("Failed to start server")

    with pytest.raises(InvalidAPIRequestError):
        raise RequestValidationError("Invalid payload parameters")


# =====================================================================
# 2. STABLE ENUM VALUE TESTS
# =====================================================================

def test_stable_enum_values():
    """Ensure defined enums have stable, unmutated string values."""
    assert APIStatus.HEALTHY == "healthy"
    assert APIStatus.DEGRADED == "degraded"
    assert APIStatus.UNHEALTHY == "unhealthy"

    assert APIErrorCode.VALIDATION_ERROR == "VALIDATION_ERROR"
    assert APIErrorCode.AUTHENTICATION_FAILED == "AUTHENTICATION_FAILED"
    assert APIErrorCode.NOT_FOUND == "NOT_FOUND"
    assert APIErrorCode.INTERNAL_ERROR == "INTERNAL_ERROR"

    assert AuthenticationScheme.API_KEY == "API_KEY"
    assert AuthenticationScheme.BEARER == "BEARER"
    assert AuthenticationScheme.NONE == "NONE"

    assert Permission.PROJECT_READ == "PROJECT_READ"
    assert Permission.WORKFLOW_EXECUTE == "WORKFLOW_EXECUTE"

    assert ResourceType.PROJECT == "PROJECT"
    assert ResourceType.WORKFLOW == "WORKFLOW"

    assert WorkflowEventType.WORKFLOW_STARTED == "WORKFLOW_STARTED"
    assert WorkflowEventType.STEP_COMPLETED == "STEP_COMPLETED"
    assert WorkflowEventType.WORKFLOW_COMPLETED == "WORKFLOW_COMPLETED"

    assert ProgressTransportType.SSE == "SSE"
    assert ProgressTransportType.WEBSOCKET == "WEBSOCKET"


# =====================================================================
# 3. PYDANTIC REQUEST VALIDATION & ERROR SHAPE TESTS
# =====================================================================

def test_project_create_request_validation():
    """Verify validation boundaries for ProjectCreateRequest."""
    # Valid model
    req = ProjectCreateRequest(name="My Campaign", description="Intro ad", workspace_parent_dir="/opt")
    assert req.name == "My Campaign"
    assert req.description == "Intro ad"

    # Too short
    with pytest.raises(ValidationError):
        ProjectCreateRequest(name="")

    # Too long
    with pytest.raises(ValidationError):
        ProjectCreateRequest(name="a" * 256)


def test_error_response_shape_and_serialization():
    """Verify structure and timezone handling of APIErrorResponse."""
    now_utc = datetime.now(timezone.utc)
    detail = APIErrorDetail(field="inputs.voice_id", message="Voice not supported", code="UNSUPPORTED_VOICE")
    
    err = APIErrorResponse(
        error_code=APIErrorCode.VALIDATION_ERROR,
        message="Inputs failed schema validation rules.",
        status_code=422,
        correlation_id="corr-12345",
        timestamp=now_utc,
        details=[detail],
        retryable=False
    )

    dump = err.model_dump(mode="json")
    assert dump["error_code"] == "VALIDATION_ERROR"
    assert dump["status_code"] == 422
    assert dump["correlation_id"] == "corr-12345"
    assert dump["details"][0]["field"] == "inputs.voice_id"
    assert dump["details"][0]["code"] == "UNSUPPORTED_VOICE"
    assert "timestamp" in dump


# =====================================================================
# 4. TIMEZONE-AWARE DATETIMES
# =====================================================================

def test_timezone_aware_datetimes():
    """Ensure model timestamps serialize as standard UTC ISO-8601 strings."""
    # Test offset aware datetime
    now_utc = datetime.now(timezone.utc)
    res = APISuccessResponse(
        success=True,
        message="Resource created",
        correlation_id="corr-xyz",
        timestamp=now_utc,
        data={"id": "abc"}
    )
    dump = res.model_dump(mode="json")
    assert "+" in dump["timestamp"] or "Z" in dump["timestamp"] or "00:00" in dump["timestamp"]

    # Test that datetime field remains timezone aware in Python object
    assert res.timestamp.tzinfo is not None
    assert res.timestamp.tzinfo.utcoffset(res.timestamp) == timedelta(0)


# =====================================================================
# 5. SAFE PATH SERIALIZATION & PATH TRAVERSAL PREVENTIONS
# =====================================================================

def test_safe_path_serialization():
    """Verify pathlib Path objects serialize seamlessly to JSON strings and detect path traversals."""
    safe_path = SafePathResponse(
        workspace_root=Path("/var/workspace"),
        assets_directory=Path("/var/workspace/assets"),
        export_target=Path("/var/workspace/releases")
    )
    
    # Assert serializes to string correctly in JSON mode
    dump = safe_path.model_dump(mode="json")
    assert dump["workspace_root"] == "/var/workspace"
    assert dump["assets_directory"] == "/var/workspace/assets"
    assert dump["export_target"] == "/var/workspace/releases"

    # Assert path traversals are caught and rejected
    with pytest.raises(ValidationError) as exc_info:
        SafePathResponse(
            workspace_root=Path("../unsafe_traversal"),
            assets_directory=Path("/var/workspace/assets")
        )
    assert "unsafe sequence characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SafePathResponse(
            workspace_root=Path("/var/workspace"),
            assets_directory="/var//double_slash"
        )
    assert "unsafe sequence characters" in str(exc_info.value)


# =====================================================================
# 6. SECRET-FIELD EXCLUSION
# =====================================================================

def test_secret_field_exclusion_and_masking():
    """Verify sensitive fields using SecretStr are masked on print/repr and excluded properly."""
    creds = SecureServiceCredentials(
        service_name="Gemini LLM Engine",
        api_key_secret=SecretStr("super-secret-production-token-999"),
        client_id="client-aims-pro",
        auth_url="https://api.example.com/oauth"
    )

    # 1. Standard repr or str should NOT leak the raw value
    assert "super-secret-production-token-999" not in str(creds)
    assert "super-secret-production-token-999" not in repr(creds)
    assert "**********" in str(creds.api_key_secret)

    # 2. Raw value is retrievable if explicitly decoded
    assert creds.api_key_secret.get_secret_value() == "super-secret-production-token-999"

    # 3. Verify standard JSON serialization masks the SecretStr to standard format
    dump_json = creds.model_dump_json()
    assert "super-secret-production-token-999" not in dump_json


# =====================================================================
# 7. CAPABILITY RESPONSE MODEL
# =====================================================================

def test_capability_response_model():
    """Verify properties and constraints of CapabilityResponse."""
    caps = CapabilityResponse(
        hardware_acceleration_available=True,
        active_device="cuda",
        supported_video_codecs=["h264", "hevc"],
        supported_audio_formats=["mp3", "wav"],
        max_concurrency_limit=4,
        features={"async_workflows": True, "sse_logging": True}
    )

    assert caps.hardware_acceleration_available is True
    assert caps.active_device == "cuda"
    assert "h264" in caps.supported_video_codecs
    assert caps.features["async_workflows"] is True


# =====================================================================
# 8. PROJECT & WORKFLOW ENDPOINT SCHEMAS
# =====================================================================

def test_project_api_models():
    """Validate project manager requests and detailed metrics responses."""
    # Test open request
    open_req = ProjectOpenRequest(path="/var/workspace/my_project")
    assert open_req.path == "/var/workspace/my_project"
    assert open_req.project_id is None

    # Test detailed summary response
    now = datetime.now(timezone.utc)
    summary = ProjectSummaryResponse(
        project_id="proj-123",
        name="Ad Campaign",
        description="Q3 Campaign",
        workspace_path="/var/workspace/my_project",
        is_dirty=False,
        is_read_only=False,
        last_saved_at=now
    )
    assert summary.project_id == "proj-123"
    assert summary.is_dirty is False


def test_workflow_api_models():
    """Validate workflow request payloads, retry states, and terminal results."""
    # Inputs schema
    inputs = WorkflowInputReferencesRequest(
        product_name="AIMS Pro",
        product_description="Enterprise suite",
        video_inputs=["/assets/b-roll.mp4"]
    )
    
    # Options schema
    options = WorkflowOptionsRequest(
        priority=30,
        timeout_seconds=600.0,
        allow_cpu_fallback=False
    )

    # Unified start request
    start_req = WorkflowStartRequest(
        workflow_type="full_video",
        inputs=inputs,
        options=options
    )

    assert start_req.workflow_type == "full_video"
    assert start_req.inputs.product_name == "AIMS Pro"
    assert start_req.options.priority == 30
    assert start_req.options.allow_cpu_fallback is False


# =====================================================================
# 9. APICONFIG VALIDATION TESTS
# =====================================================================

def test_api_config_validation():
    """Verify validation and default values of global APIConfig."""
    # Default verify
    conf = APIConfig()
    assert conf.host == "127.0.0.1"
    assert conf.port == 3000
    assert conf.auth_mode == AuthenticationScheme.NONE

    # Custom override
    custom_conf = APIConfig(host="0.0.0.0", port=8080, auth_mode=AuthenticationScheme.API_KEY)
    assert custom_conf.host == "0.0.0.0"
    assert custom_conf.port == 8080
    assert custom_conf.auth_mode == AuthenticationScheme.API_KEY

    # Blank host validation
    with pytest.raises(ValidationError):
        APIConfig(host="  ")

    # Port out of bounds validation
    with pytest.raises(ValidationError):
        APIConfig(port=99999)
