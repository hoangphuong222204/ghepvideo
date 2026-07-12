"""Exception hierarchy for Module 12: Workflow Engine.

This module defines all custom exceptions raised by the Workflow Engine,
covering workflow definition, validation, mapping, execution, steps, retry,
compensation, states, and batch processes.
"""

class WorkflowEngineError(Exception):
    """Base exception class for all errors originating in the Workflow Engine (Module 12)."""
    pass


# Configuration & Setup Errors
class WorkflowConfigError(WorkflowEngineError):
    """Raised when there is an invalid configuration for the Workflow Engine."""
    pass


class WorkflowDependencyError(WorkflowEngineError):
    """Base class for workflow dependency resolution errors."""
    pass


class MissingWorkflowDependencyError(WorkflowDependencyError):
    """Raised when a required external module or engine dependency is missing or unavailable."""
    pass


# Request & Definition Validation Errors
class InvalidWorkflowRequestError(WorkflowEngineError):
    """Raised when a workflow request is malformed or invalid."""
    pass


class InvalidWorkflowDefinitionError(WorkflowEngineError):
    """Raised when a workflow graph definition is malformed, invalid, or inconsistent."""
    pass


class CircularWorkflowDependencyError(InvalidWorkflowDefinitionError):
    """Raised when a circular step dependency is detected in the workflow definition."""
    pass


class UnsupportedWorkflowModeError(WorkflowEngineError):
    """Raised when the requested execution mode is unsupported or invalid."""
    pass


class WorkflowValidationError(WorkflowEngineError):
    """Raised when a workflow request or execution state fails readiness or integrity validation."""
    pass


# Context & State Errors
class InvalidWorkflowContextError(WorkflowEngineError):
    """Raised when a workflow runtime context is invalid, missing, or corrupt."""
    pass


class WorkflowNotFoundError(WorkflowEngineError):
    """Raised when the specified workflow execution or state cannot be found."""
    pass


class WorkflowAlreadyRunningError(WorkflowEngineError):
    """Raised when attempting to execute or modify a workflow that is currently running."""
    pass


class WorkflowExecutionError(WorkflowEngineError):
    """Raised when general workflow execution fails or is aborted."""
    pass


class WorkflowStateError(WorkflowEngineError):
    """Base exception for workflow state loading, saving, or transition tracking."""
    pass


class WorkflowStateCorruptionError(WorkflowStateError):
    """Raised when the loaded workflow execution state is detected as corrupt or unparseable."""
    pass


class WorkflowStatePersistenceError(WorkflowStateError):
    """Raised when saving or loading workflow execution state to/from disk fails."""
    pass


class WorkflowResumeError(WorkflowEngineError):
    """Raised when attempting to resume an interrupted or saved workflow fails."""
    pass


# Step-Specific Errors
class StepError(WorkflowEngineError):
    """Base exception for all workflow step operations."""
    pass


class StepNotFoundError(StepError):
    """Raised when a requested workflow step type has no registered execution handler."""
    pass


class StepAlreadyCompletedError(StepError):
    """Raised when trying to execute or modify a step that has already completed successfully."""
    pass


class StepExecutionError(StepError):
    """Raised when an individual workflow step fails execution."""
    pass


class StepTimeoutError(StepExecutionError):
    """Raised when a workflow step exceeds its configured maximum execution time."""
    pass


class StepCancellationError(StepError):
    """Raised when a workflow step is aborted or cancelled mid-execution."""
    pass


class StepRetryExhaustedError(StepExecutionError):
    """Raised when a workflow step fails repeatedly and all configured retries are exhausted."""
    pass


class InvalidStepTransitionError(StepError):
    """Raised when an illegal step execution sequence or status transition is attempted."""
    pass


# Process-Specific & Mapping Errors
class WorkflowCompensationError(WorkflowEngineError):
    """Raised when rolling back or executing compensation/cleanup routines for a failed workflow fails."""
    pass


class ProgressAggregationError(WorkflowEngineError):
    """Raised when calculating or broadcasting aggregated workflow progress fails."""
    pass


class InputMappingError(WorkflowEngineError):
    """Raised when mapping product or step outputs into the next step's input parameters fails."""
    pass


class OutputMappingError(WorkflowEngineError):
    """Raised when mapping completed step outputs into workflow context or final results fails."""
    pass


class ProjectUpdateError(WorkflowEngineError):
    """Raised when updating project metadata, settings, or assets via the Project Manager fails."""
    pass


class BatchWorkflowError(WorkflowEngineError):
    """Raised when executing or orchestrating a batch sequence of workflows fails."""
    pass


# Additional Specific Errors
class StepPreconditionError(StepError):
    """Raised when a step's preconditions are not met before execution."""
    pass


class WorkflowCancellationError(WorkflowEngineError):
    """Raised when a workflow execution is cancelled or aborted."""
    pass


class AwaitingInputValidationError(WorkflowEngineError):
    """Raised when user-provided input for an AWAITING_INPUT step is invalid."""
    pass


class ExecutionOwnershipConflictError(WorkflowEngineError):
    """Raised when another runner is already executing the same workflow ID."""
    pass

