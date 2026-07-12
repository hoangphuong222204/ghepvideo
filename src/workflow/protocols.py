"""Structural typing protocols for Module 12: Workflow Engine.

These protocols define the component interfaces for definition parsing, input mapping,
step execution, progress tracking, state storage, retry handling, and engine orchestration.
"""

from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable
from pathlib import Path
from datetime import datetime

from src.workflow.workflow_models import (
    WorkflowRequest,
    WorkflowResult,
    BatchWorkflowRequest,
    BatchWorkflowResult,
    WorkflowValidationReport,
    WorkflowState,
    WorkflowProgress,
    WorkflowHealthStatus,
    WorkflowStepType,
    WorkflowStepState,
    StepExecutionRequest,
    StepExecutionResult,
    ResumeInformation,
    CompensationAction,
    WorkflowDefinition,
)


@runtime_checkable
class WorkflowStateStoreProtocol(Protocol):
    """Protocol for loading, saving, and checking persistence of workflow state snapshots."""

    def save_state(self, state: WorkflowState) -> None:
        """Atomically persist workflow execution state to disk or database.

        Args:
            state: The WorkflowState instance to serialize and save.

        Raises:
            WorkflowStatePersistenceError: If saving fails.
        """
        ...

    def load_state(self, workflow_id: str) -> WorkflowState:
        """Load and deserialize workflow execution state.

        Args:
            workflow_id: Unique identifier of the workflow.

        Returns:
            The loaded WorkflowState instance.

        Raises:
            WorkflowNotFoundError: If the state file does not exist.
            WorkflowStateCorruptionError: If loaded data cannot be parsed.
        """
        ...

    def list_resumable_workflows(self, project_id: Optional[str] = None) -> List[WorkflowState]:
        """Scan state storage for workflows that are in a resumable state (paused, failed, etc.).

        Args:
            project_id: Optional project identifier to filter by.

        Returns:
            A list of WorkflowState objects representing resumable workflows.
        """
        ...

    def delete_state(self, workflow_id: str) -> None:
        """Remove a workflow's state from the store.

        Args:
            workflow_id: Unique identifier of the workflow.
        """
        ...


@runtime_checkable
class DependencyResolverProtocol(Protocol):
    """Protocol for analyzing step dependencies and determining valid execution sequences."""

    def resolve_execution_order(self, definition: WorkflowDefinition) -> List[WorkflowStepType]:
        """Perform topological sort on step dependencies to find a deterministic execution order.

        Args:
            definition: Resolved workflow definition graph.

        Returns:
            A list of WorkflowStepType ordered deterministically.

        Raises:
            CircularWorkflowDependencyError: If a dependency cycle is detected.
        """
        ...

    def get_downstream_dependents(self, definition: WorkflowDefinition, step_type: WorkflowStepType) -> List[WorkflowStepType]:
        """Find all downstream steps that depend directly or indirectly on the given step.

        Args:
            definition: Resolved workflow definition graph.
            step_type: The starting step type.

        Returns:
            A list of downstream WorkflowStepType elements.
        """
        ...


@runtime_checkable
class InputMapperProtocol(Protocol):
    """Protocol for mapping data safely between pipeline step boundaries without mutating sources."""

    def map_to_script_request(self, request: WorkflowRequest) -> Any:
        """Map workflow request fields to Module 07 script engine inputs."""
        ...

    def map_to_speech_request(self, request: WorkflowRequest, script_output: Any) -> Any:
        """Map selected script output to Module 08 TTS engine inputs."""
        ...

    def map_to_subtitle_request(self, request: WorkflowRequest, script_output: Any, speech_output: Any) -> Any:
        """Map script and speech outputs to Module 09 subtitle engine inputs."""
        ...

    def map_to_render_request(self, request: WorkflowRequest, script_output: Any, speech_output: Any, subtitle_output: Any) -> Any:
        """Map media inputs, audio, and subtitle references to Module 10 render engine inputs."""
        ...

    def map_to_project_registration(self, request: WorkflowRequest, outputs: Any) -> Any:
        """Map compiled outputs to Module 11 asset/reference registration parameters."""
        ...


@runtime_checkable
class StepRegistryProtocol(Protocol):
    """Protocol for registering and retrieving dedicated execution handlers by step type."""

    def register_handler(self, step_type: WorkflowStepType, handler: Any) -> None:
        """Register a handler for a specific workflow step type.

        Args:
            step_type: The step type identifier.
            handler: The execution handler object.

        Raises:
            ValueError: If a duplicate handler is registered or handler is invalid.
        """
        ...

    def get_handler(self, step_type: WorkflowStepType) -> Any:
        """Retrieve the registered handler for a workflow step type.

        Args:
            step_type: The step type identifier.

        Returns:
            The registered handler object.

        Raises:
            StepNotFoundError: If no handler is registered.
        """
        ...


@runtime_checkable
class RetryManagerProtocol(Protocol):
    """Protocol for deciding retry actions, backing off, and tracking retry states."""

    def is_recoverable(self, error: Exception) -> bool:
        """Analyze an exception to classify if it is transient/recoverable.

        Args:
            error: The Exception encountered.

        Returns:
            True if the error is considered transient, False otherwise.
        """
        ...

    def calculate_delay(self, attempt: int, initial_delay: float, max_delay: float, strategy: str) -> float:
        """Calculate retry delay based on strategy and attempt number.

        Args:
            attempt: Current retry attempt count.
            initial_delay: Starting delay in seconds.
            max_delay: Cap on delay in seconds.
            strategy: Time spacing algorithm (fixed vs. exponential).

        Returns:
            The calculated delay in seconds.
        """
        ...


@runtime_checkable
class CompensationManagerProtocol(Protocol):
    """Protocol for coordinating reversions of partial outputs when workflows abort."""

    def record_completed_step(self, step_type: WorkflowStepType, compensation_handler: Any) -> None:
        """Track a completed step and its associated cleanup routine.

        Args:
            step_type: Completed step.
            compensation_handler: Cleanup callback or handler.
        """
        ...

    def execute_compensation(self, workflow_id: str) -> List[CompensationAction]:
        """Run all registered compensations in reverse order to clean up uncommitted outputs.

        Args:
            workflow_id: Active workflow identifier.

        Returns:
            A list of completed CompensationAction records.
        """
        ...


@runtime_checkable
class ProgressAggregatorProtocol(Protocol):
    """Protocol for aggregating multi-step progress with normalized step weights."""

    def calculate_progress(
        self,
        step_states: Dict[WorkflowStepType, WorkflowStepState],
        active_steps: List[WorkflowStepType],
        current_step: Optional[WorkflowStepType],
        current_step_progress: float = 0.0,
    ) -> WorkflowProgress:
        """Aggregate numeric progress and clamp it strictly between 0.0 and 100.0.

        Args:
            step_states: Map of step execution states.
            active_steps: List of steps active in the current definition.
            current_step: The currently running step type.
            current_step_progress: Progress of the current step (0.0 to 100.0).

        Returns:
            WorkflowProgress telemetry.
        """
        ...


@runtime_checkable
class WorkflowValidatorProtocol(Protocol):
    """Protocol for verifying workflow requests, engine readiness, and project context."""

    def validate_request(self, request: WorkflowRequest) -> WorkflowValidationReport:
        """Perform recursive structural readiness and constraint validations.

        Args:
            request: The payload to analyze.

        Returns:
            A completed WorkflowValidationReport.
        """
        ...


@runtime_checkable
class StepExecutorProtocol(Protocol):
    """Protocol for coordinating precondition checks, handlers, and capturing outputs."""

    def execute_step(self, step_req: StepExecutionRequest, handler: Any) -> StepExecutionResult:
        """Run precondition checks, execute the handler, and record metrics.

        Args:
            step_req: Context parameters.
            handler: Registered execution handler.

        Returns:
            A populated StepExecutionResult.
        """
        ...


@runtime_checkable
class WorkflowEngineProtocol(Protocol):
    """Main orchestration application-facing interface for workflow lifecycles."""

    def run(self, request: WorkflowRequest) -> WorkflowResult:
        """Synchronously execute a workflow request from start to finish.

        Args:
            request: Complete payload.

        Returns:
            WorkflowResult summarizing final status and outputs.
        """
        ...

    def submit(self, request: WorkflowRequest) -> Any:
        """Submit a workflow for non-blocking asynchronous execution.

        Args:
            request: Complete payload.

        Returns:
            A submission descriptor or future containing the workflow ID.
        """
        ...

    def run_batch(self, request: BatchWorkflowRequest) -> BatchWorkflowResult:
        """Execute a batch of workflows using configured concurrency boundaries.

        Args:
            request: Batch request wrapping multiple sub-requests.

        Returns:
            BatchWorkflowResult.
        """
        ...

    def validate(self, request: WorkflowRequest) -> WorkflowValidationReport:
        """Validate input parameters and system health without running the pipeline.

        Args:
            request: Target payload.

        Returns:
            WorkflowValidationReport.
        """
        ...

    def get_state(self, workflow_id: str) -> WorkflowState:
        """Fetch the exact execution and outputs snapshot of a workflow.

        Args:
            workflow_id: Unique workflow identifier.

        Returns:
            WorkflowState model.
        """
        ...

    def get_progress(self, workflow_id: str) -> WorkflowProgress:
        """Fetch the latest progress metrics of a workflow.

        Args:
            workflow_id: Unique workflow identifier.

        Returns:
            WorkflowProgress telemetry.
        """
        ...

    def cancel(self, workflow_id: str) -> WorkflowResult:
        """Cooperatively signal a running workflow to abort.

        Args:
            workflow_id: Target workflow identifier.

        Returns:
            WorkflowResult showing CANCELLED or intermediate terminal state.
        """
        ...

    def resume(self, workflow_id: str, options: Optional[Any] = None) -> WorkflowResult:
        """Load and resume an interrupted, failed, or paused workflow session.

        Args:
            workflow_id: Target workflow identifier.
            options: Optional override configuration parameters.

        Returns:
            WorkflowResult.
        """
        ...

    def retry_step(self, workflow_id: str, step: WorkflowStepType) -> WorkflowResult:
        """Force a single failed step to retry.

        Args:
            workflow_id: Target workflow identifier.
            step: Targeted failed step type.

        Returns:
            WorkflowResult.
        """
        ...

    def regenerate_step(self, workflow_id: str, step: WorkflowStepType, overrides: Optional[Any] = None) -> WorkflowResult:
        """Explicitly regenerate an earlier step, invalidating dependent downstream steps.

        Args:
            workflow_id: Target workflow identifier.
            step: The step to run again.
            overrides: Optional replacement input fields or parameters.

        Returns:
            WorkflowResult.
        """
        ...

    def provide_input(self, workflow_id: str, input_response: Any) -> WorkflowResult:
        """Resume a workflow currently in AWAITING_INPUT state by providing requested data.

        Args:
            workflow_id: Target workflow identifier.
            input_response: Data response answering the input request.

        Returns:
            WorkflowResult.
        """
        ...

    def list_resumable(self, project_id: Optional[str] = None) -> List[WorkflowState]:
        """Query and filter states available for resumption.

        Args:
            project_id: Optional project filter.

        Returns:
            A list of WorkflowState snapshots.
        """
        ...

    def health(self) -> WorkflowHealthStatus:
        """Assess global and component availability for all workflow steps.

        Returns:
            WorkflowHealthStatus snapshot.
        """
        ...
