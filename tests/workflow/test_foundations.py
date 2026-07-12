"""Unit tests for the foundations of Module 12: Workflow Engine.

This suite validates exception hierarchy, enum stability, public imports, and model validation/serialization
of all core dataclasses used in Workflow Engine.
"""

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

import src.workflow as wf


class TestWorkflowFoundations(unittest.TestCase):
    """Foundational test suite for Module 12 exception structure, models, and public exports."""

    def test_public_imports(self) -> None:
        """Verify all major foundations, exceptions, models, and protocols are exported."""
        # Exceptions
        self.assertTrue(hasattr(wf, "WorkflowEngineError"))
        self.assertTrue(hasattr(wf, "WorkflowConfigError"))
        self.assertTrue(hasattr(wf, "InvalidWorkflowRequestError"))
        self.assertTrue(hasattr(wf, "WorkflowValidationError"))
        self.assertTrue(hasattr(wf, "StepPreconditionError"))
        self.assertTrue(hasattr(wf, "ExecutionOwnershipConflictError"))

        # Models
        self.assertTrue(hasattr(wf, "WorkflowType"))
        self.assertTrue(hasattr(wf, "WorkflowMode"))
        self.assertTrue(hasattr(wf, "WorkflowStatus"))
        self.assertTrue(hasattr(wf, "WorkflowStepType"))
        self.assertTrue(hasattr(wf, "WorkflowStepStatus"))
        self.assertTrue(hasattr(wf, "WorkflowRequest"))
        self.assertTrue(hasattr(wf, "WorkflowResult"))

        # Protocols
        self.assertTrue(hasattr(wf, "WorkflowEngineProtocol"))
        self.assertTrue(hasattr(wf, "WorkflowStateStoreProtocol"))

    def test_exception_hierarchy(self) -> None:
        """Verify custom exception inheritance matches design requirements."""
        self.assertTrue(issubclass(wf.WorkflowEngineError, Exception))
        self.assertTrue(issubclass(wf.WorkflowConfigError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.WorkflowDependencyError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.MissingWorkflowDependencyError, wf.WorkflowDependencyError))

        self.assertTrue(issubclass(wf.InvalidWorkflowRequestError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.InvalidWorkflowDefinitionError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.CircularWorkflowDependencyError, wf.InvalidWorkflowDefinitionError))
        self.assertTrue(issubclass(wf.UnsupportedWorkflowModeError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.WorkflowValidationError, wf.WorkflowEngineError))

        self.assertTrue(issubclass(wf.InvalidWorkflowContextError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.WorkflowNotFoundError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.WorkflowAlreadyRunningError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.WorkflowExecutionError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.WorkflowStateError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.WorkflowStateCorruptionError, wf.WorkflowStateError))
        self.assertTrue(issubclass(wf.WorkflowStatePersistenceError, wf.WorkflowStateError))
        self.assertTrue(issubclass(wf.WorkflowResumeError, wf.WorkflowEngineError))

        self.assertTrue(issubclass(wf.StepError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.StepNotFoundError, wf.StepError))
        self.assertTrue(issubclass(wf.StepAlreadyCompletedError, wf.StepError))
        self.assertTrue(issubclass(wf.StepExecutionError, wf.StepError))
        self.assertTrue(issubclass(wf.StepTimeoutError, wf.StepExecutionError))
        self.assertTrue(issubclass(wf.StepCancellationError, wf.StepError))
        self.assertTrue(issubclass(wf.StepRetryExhaustedError, wf.StepExecutionError))
        self.assertTrue(issubclass(wf.InvalidStepTransitionError, wf.StepError))
        self.assertTrue(issubclass(wf.StepPreconditionError, wf.StepError))

        self.assertTrue(issubclass(wf.WorkflowCompensationError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.ProgressAggregationError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.InputMappingError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.OutputMappingError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.ProjectUpdateError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.BatchWorkflowError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.WorkflowCancellationError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.AwaitingInputValidationError, wf.WorkflowEngineError))
        self.assertTrue(issubclass(wf.ExecutionOwnershipConflictError, wf.WorkflowEngineError))

    def test_enum_stability(self) -> None:
        """Ensure all domain enums remain stable and match specific wiring values."""
        self.assertEqual(wf.WorkflowType.FULL_VIDEO.value, "full_video")
        self.assertEqual(wf.WorkflowType.SCRIPT_ONLY.value, "script_only")
        self.assertEqual(wf.WorkflowType.SPEECH_ONLY.value, "speech_only")
        self.assertEqual(wf.WorkflowType.SUBTITLE_ONLY.value, "subtitle_only")
        self.assertEqual(wf.WorkflowType.RENDER_ONLY.value, "render_only")

        self.assertEqual(wf.WorkflowMode.STANDARD.value, "standard")
        self.assertEqual(wf.WorkflowMode.RESUME.value, "resume")
        self.assertEqual(wf.WorkflowMode.RETRY.value, "retry")
        self.assertEqual(wf.WorkflowMode.REGENERATE.value, "regenerate")
        self.assertEqual(wf.WorkflowMode.DRY_RUN.value, "dry_run")

        self.assertEqual(wf.WorkflowStatus.PENDING.value, "pending")
        self.assertEqual(wf.WorkflowStatus.RUNNING.value, "running")
        self.assertEqual(wf.WorkflowStatus.COMPLETED.value, "completed")
        self.assertEqual(wf.WorkflowStatus.FAILED.value, "failed")
        self.assertEqual(wf.WorkflowStatus.CANCELLED.value, "cancelled")
        self.assertEqual(wf.WorkflowStatus.AWAITING_INPUT.value, "awaiting_input")

        self.assertEqual(wf.WorkflowStepType.INITIALIZE.value, "initialize")
        self.assertEqual(wf.WorkflowStepType.VALIDATE_INPUT.value, "validate_input")
        self.assertEqual(wf.WorkflowStepType.GENERATE_SCRIPT.value, "generate_script")
        self.assertEqual(wf.WorkflowStepType.SELECT_SCRIPT.value, "select_script")
        self.assertEqual(wf.WorkflowStepType.GENERATE_SPEECH.value, "generate_speech")
        self.assertEqual(wf.WorkflowStepType.GENERATE_SUBTITLES.value, "generate_subtitles")
        self.assertEqual(wf.WorkflowStepType.PREPARE_RENDER.value, "prepare_render")
        self.assertEqual(wf.WorkflowStepType.RENDER_VIDEO.value, "render_video")
        self.assertEqual(wf.WorkflowStepType.VALIDATE_OUTPUT.value, "validate_output")
        self.assertEqual(wf.WorkflowStepType.UPDATE_PROJECT.value, "update_project")
        self.assertEqual(wf.WorkflowStepType.FINALIZE.value, "finalize")
        self.assertEqual(wf.WorkflowStepType.CLEANUP.value, "cleanup")

        self.assertEqual(wf.WorkflowStepStatus.PENDING.value, "pending")
        self.assertEqual(wf.WorkflowStepStatus.RUNNING.value, "running")
        self.assertEqual(wf.WorkflowStepStatus.COMPLETED.value, "completed")
        self.assertEqual(wf.WorkflowStepStatus.FAILED.value, "failed")
        self.assertEqual(wf.WorkflowStepStatus.CANCELLED.value, "cancelled")
        self.assertEqual(wf.WorkflowStepStatus.SKIPPED.value, "skipped")

        self.assertEqual(wf.WorkflowFailurePolicy.FAIL_FAST.value, "fail_fast")
        self.assertEqual(wf.WorkflowFailurePolicy.RETRY_THEN_FAIL.value, "retry_then_fail")
        self.assertEqual(wf.WorkflowFailurePolicy.COMPENSATE_AND_FAIL.value, "compensate_and_fail")
        self.assertEqual(wf.WorkflowFailurePolicy.KEEP_COMPLETED_OUTPUTS.value, "keep_completed_outputs")
        self.assertEqual(wf.WorkflowFailurePolicy.COMPLETE_WITH_WARNINGS.value, "complete_with_warnings")

        self.assertEqual(wf.RetryStrategy.FIXED.value, "fixed")
        self.assertEqual(wf.RetryStrategy.EXPONENTIAL_BACKOFF.value, "exponential_backoff")

        self.assertEqual(wf.CompensationStrategy.CLEAN_ALL.value, "clean_all")
        self.assertEqual(wf.CompensationStrategy.CLEAN_TEMPORARY.value, "clean_temporary")
        self.assertEqual(wf.CompensationStrategy.NONE.value, "none")

        self.assertEqual(wf.WorkflowPriority.LOW.value, 10)
        self.assertEqual(wf.WorkflowPriority.MEDIUM.value, 20)
        self.assertEqual(wf.WorkflowPriority.HIGH.value, 30)

    def test_retry_policy_validation(self) -> None:
        """Verify constraints inside RetryPolicy dataclass."""
        policy = wf.RetryPolicy(wf.RetryStrategy.EXPONENTIAL_BACKOFF, 5, 2.0, 30.0)
        self.assertEqual(policy.max_retries, 5)

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.RetryPolicy(max_retries=-1)

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.RetryPolicy(initial_delay_seconds=-0.5)

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.RetryPolicy(initial_delay_seconds=5.0, max_delay_seconds=4.0)

    def test_workflow_options_validation(self) -> None:
        """Verify constraints inside WorkflowOptions dataclass."""
        opts = wf.WorkflowOptions(timeout_seconds=300.0)
        self.assertEqual(opts.timeout_seconds, 300.0)

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.WorkflowOptions(timeout_seconds=0)

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.WorkflowOptions(timeout_seconds=-10.0)

    def test_project_context_validation(self) -> None:
        """Verify constraints inside WorkflowProjectContext dataclass."""
        ctx = wf.WorkflowProjectContext(project_id="p-123", workspace_root=Path("/a/b"))
        self.assertEqual(ctx.project_id, "p-123")

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.WorkflowProjectContext(project_id="", workspace_root=Path("/a/b"))

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.WorkflowProjectContext(project_id="   ", workspace_root=Path("/a/b"))

    def test_workflow_request_validation(self) -> None:
        """Verify constraints inside WorkflowRequest dataclass."""
        ctx = wf.WorkflowProjectContext("p-123", Path("/a"))
        req = wf.WorkflowRequest(
            workflow_id="wf-abc",
            workflow_type=wf.WorkflowType.FULL_VIDEO,
            project_context=ctx,
        )
        self.assertEqual(req.workflow_id, "wf-abc")

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.WorkflowRequest(
                workflow_id="",
                workflow_type=wf.WorkflowType.FULL_VIDEO,
                project_context=ctx,
            )

    def test_batch_workflow_request_validation(self) -> None:
        """Verify constraints inside BatchWorkflowRequest dataclass."""
        ctx = wf.WorkflowProjectContext("p-123", Path("/a"))
        req1 = wf.WorkflowRequest("wf-1", wf.WorkflowType.SCRIPT_ONLY, ctx)
        req2 = wf.WorkflowRequest("wf-2", wf.WorkflowType.SPEECH_ONLY, ctx)

        batch = wf.BatchWorkflowRequest("batch-100", [req1, req2], concurrency_limit=4)
        self.assertEqual(batch.batch_id, "batch-100")
        self.assertEqual(len(batch.requests), 2)

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.BatchWorkflowRequest("", [req1])

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.BatchWorkflowRequest("batch-100", [])

        with self.assertRaises(wf.InvalidWorkflowRequestError):
            wf.BatchWorkflowRequest("batch-100", [req1], concurrency_limit=0)

    def test_workflow_step_state(self) -> None:
        """Verify timezone enforcement and property calculations of WorkflowStepState."""
        now_naive = datetime.now()
        state = wf.WorkflowStepState(
            step_type=wf.WorkflowStepType.VALIDATE_INPUT,
            status=wf.WorkflowStepStatus.RUNNING,
            started_at=now_naive,
            retry_count=1,
            warnings=["Warn 1"],
        )
        self.assertEqual(state.started_at.tzinfo, timezone.utc)
        self.assertEqual(state.retry_count, 1)

    def test_workflow_state(self) -> None:
        """Verify timezone enforcement and fields in WorkflowState."""
        ctx = wf.WorkflowProjectContext("p-123", Path("/a"))
        req = wf.WorkflowRequest("wf-1", wf.WorkflowType.SCRIPT_ONLY, ctx)
        state = wf.WorkflowState(
            workflow_id="wf-1",
            workflow_type=wf.WorkflowType.SCRIPT_ONLY,
            status=wf.WorkflowStatus.RUNNING,
            project_id="p-123",
            request_snapshot=req,
        )
        self.assertEqual(state.created_at.tzinfo, timezone.utc)
        self.assertEqual(state.updated_at.tzinfo, timezone.utc)

    def test_workflow_progress(self) -> None:
        """Verify percentage clipping and timestamps inside WorkflowProgress."""
        prog_high = wf.WorkflowProgress("wf-1", wf.WorkflowStatus.RUNNING, 150.0, 10.0)
        self.assertEqual(prog_high.percentage, 100.0)

        prog_low = wf.WorkflowProgress("wf-1", wf.WorkflowStatus.RUNNING, -20.0, 10.0)
        self.assertEqual(prog_low.percentage, 0.0)

    def test_validation_issue_and_report(self) -> None:
        """Verify constraints inside WorkflowValidationIssue and report validation behavior."""
        with self.assertRaises(wf.WorkflowValidationError):
            wf.WorkflowValidationIssue("invalid-severity", "code", "msg")

        issue = wf.WorkflowValidationIssue("error", "E_CODE", "Error message")
        report = wf.WorkflowValidationReport(is_valid=True, issues=[issue])
        self.assertFalse(report.is_valid)  # Must self-correct to False on errors

    def test_workflow_result_serialization(self) -> None:
        """Verify full convertibility to serializable maps for UI/FastAPI mapping."""
        now = datetime.now(timezone.utc)
        res = wf.WorkflowResult(
            workflow_id="wf-1",
            workflow_type=wf.WorkflowType.FULL_VIDEO,
            mode=wf.WorkflowMode.STANDARD,
            status=wf.WorkflowStatus.COMPLETED,
            project_id="p-123",
            started_at=now,
            completed_at=now,
            duration_seconds=12.5,
            final_step=wf.WorkflowStepType.FINALIZE,
            outputs=wf.WorkflowOutputReferences(
                script_id="s-1",
                speech_audio_path=Path("generated/speech.wav"),
                subtitle_path=Path("generated/subtitles.srt"),
                final_video_path=Path("generated/final.mp4"),
            ),
        )

        d = res.to_dict()
        self.assertEqual(d["workflow_id"], "wf-1")
        self.assertEqual(d["outputs"]["speech_audio_path"], "generated/speech.wav")
        self.assertEqual(d["outputs"]["subtitle_path"], "generated/subtitles.srt")
        self.assertEqual(d["outputs"]["final_video_path"], "generated/final.mp4")
        self.assertEqual(d["status"], "completed")

        # Check JSON dumpability
        json_str = json.dumps(d)
        self.assertTrue(isinstance(json_str, str))


if __name__ == "__main__":
    unittest.main()
