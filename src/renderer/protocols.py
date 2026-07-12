"""Structural typing protocols for Module 10: FFmpeg Render Engine.

These protocols define standard contracts for all major rendering sub-components,
supporting complete dependency injection, clean mock-based testing, and decoupling.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from src.renderer.render_models import (
    MediaMetadata,
    RenderRequest,
    RenderResult,
    BatchRenderRequest,
    BatchRenderResult,
    RenderValidationReport,
    RendererHealthStatus,
    FFmpegCapabilityInformation,
    RenderPlan,
)


@runtime_checkable
class FFmpegLocatorProtocol(Protocol):
    """Protocol for finding and verifying FFmpeg and FFprobe binary locations."""

    def locate_ffmpeg(self) -> Path:
        """Locate the FFmpeg executable, raising FFmpegNotFoundError if missing.

        Returns:
            Absolute Path to the FFmpeg executable.
        """
        ...

    def locate_ffprobe(self) -> Path:
        """Locate the FFprobe executable, raising FFprobeNotFoundError if missing.

        Returns:
            Absolute Path to the FFprobe executable.
        """
        ...


@runtime_checkable
class CapabilityDetectorProtocol(Protocol):
    """Protocol for inspecting and caching available FFmpeg codecs and filters."""

    def detect_capabilities(self, ffmpeg_path: Path) -> FFmpegCapabilityInformation:
        """Inspect and parse available encoders, decoders, filters, and hardware accelerations.

        Args:
            ffmpeg_path: Path to the validated FFmpeg binary.

        Returns:
            An FFmpegCapabilityInformation container.
        """
        ...


@runtime_checkable
class MediaProbeProtocol(Protocol):
    """Protocol for extracting media stream metadata using FFprobe."""

    def probe_media(self, path: Path, ffprobe_path: Path, timeout_seconds: float = 30.0) -> MediaMetadata:
        """Parse stream structure, durations, resolution, and codecs from an input file.

        Args:
            path: Path to the visual/audio asset.
            ffprobe_path: Path to the validated FFprobe binary.
            timeout_seconds: Subprocess execution timeout.

        Returns:
            A populated MediaMetadata container.
        """
        ...


@runtime_checkable
class InputValidatorProtocol(Protocol):
    """Protocol for checking if render inputs exist, are readable, and configurations are valid."""

    def validate_request(self, request: RenderRequest, capabilities: FFmpegCapabilityInformation) -> RenderValidationReport:
        """Validate request structure, path writes, trims, aspect-ratios, and capability alignments.

        Args:
            request: The RenderRequest to validate.
            capabilities: Currently detected FFmpeg capabilities.

        Returns:
            A RenderValidationReport containing is_valid, errors, and warnings.
        """
        ...


@runtime_checkable
class RenderPlanBuilderProtocol(Protocol):
    """Protocol for converting a validated RenderRequest into a deterministic RenderPlan."""

    def build_plan(
        self,
        request: RenderRequest,
        media_metadata_cache: Dict[Path, MediaMetadata],
        capabilities: FFmpegCapabilityInformation,
    ) -> RenderPlan:
        """Convert visual, audio, subtitle, overlay parameters into a structured execution roadmap.

        Args:
            request: The validated RenderRequest.
            media_metadata_cache: Pre-cached probed media attributes of referenced inputs.
            capabilities: Active FFmpeg capability profiles.

        Returns:
            A deterministic RenderPlan.
        """
        ...


@runtime_checkable
class FilterGraphBuilderProtocol(Protocol):
    """Protocol for constructing complex FFmpeg video/audio filter graphs."""

    def build_filter_graph(self, plan: RenderPlan, media_metadata_cache: Dict[Path, MediaMetadata], request: RenderRequest) -> str:
        """Compose a structured, escaped filter_complex script representing overlays and concatenations.

        Args:
            plan: The resolved RenderPlan.
            media_metadata_cache: Pre-cached probed media attributes of referenced inputs.
            request: The original RenderRequest.

        Returns:
            A fully escaped, ready-to-run FFmpeg filter_complex graph string.
        """
        ...


@runtime_checkable
class CommandBuilderProtocol(Protocol):
    """Protocol for constructing the exact immutable FFmpeg argument lists."""

    def build_command(
        self,
        ffmpeg_path: Path,
        plan: RenderPlan,
        filter_graph: str,
        request: RenderRequest,
        temp_output_path: Path,
    ) -> List[str]:
        """Combine inputs, maps, filter_complex script, and output codecs into an argument list.

        Args:
            ffmpeg_path: Absolute path to the validated FFmpeg binary.
            plan: The resolved RenderPlan.
            filter_graph: Constructed filter_complex graph string.
            request: The original RenderRequest.
            temp_output_path: Isolated destination path for staging the render.

        Returns:
            A list of command line arguments, safe for direct execution without shell=True.
        """
        ...


@runtime_checkable
class ProcessRunnerProtocol(Protocol):
    """Protocol for executing subprocesses, parsing progress lines, and handling signals."""

    def run_process(
        self,
        command: List[str],
        timeout_seconds: float,
        progress_callback: Optional[Any] = None,
        cancellation_token: Optional[Any] = None,
    ) -> Any:
        """Launch the subprocess, read machine-readable progress lines, and handle timeout/cancellation.

        Args:
            command: Fully constructed executable and arguments list.
            timeout_seconds: Hard runtime limit.
            progress_callback: Optional callback to receive periodic progress dicts or models.
            cancellation_token: Optional token supporting cooperative execution cancellation.

        Returns:
            The execution output or process result.
        """
        ...


@runtime_checkable
class TemporaryFileManagerProtocol(Protocol):
    """Protocol for managing temporary files and workspace cleanup."""

    def create_workspace(self, task_id: str) -> Path:
        """Create a dedicated workspace directory for intermediate rendering artifacts.

        Args:
            task_id: Unique task identifier.

        Returns:
            Absolute Path to the created workspace directory.
        """
        ...

    def get_temp_output_path(self, task_id: str, suffix: str = ".mp4") -> Path:
        """Generate a random, collision-free path inside the task workspace.

        Args:
            task_id: Unique task identifier.
            suffix: File extension (including dot).

        Returns:
            Absolute Path to a temporary output staging location.
        """
        ...

    def cleanup_workspace(self, task_id: str) -> None:
        """Safely delete all generated temporary files for this task.

        Args:
            task_id: Unique task identifier.
        """
        ...


@runtime_checkable
class OutputValidatorProtocol(Protocol):
    """Protocol for performing deep post-render checks on the compiled media."""

    def validate_output(self, path: Path, expected_plan: RenderPlan, ffprobe_path: Path) -> RenderValidationReport:
        """Assert file existence, readability, non-zero size, resolution, and format parameters.

        Args:
            path: Path to the generated video file.
            expected_plan: The RenderPlan used to guide the compilation.
            ffprobe_path: Absolute path to the validated FFprobe binary.

        Returns:
            A RenderValidationReport documenting integrity status, warnings, and errors.
        """
        ...


@runtime_checkable
class RenderEngineProtocol(Protocol):
    """Top-level orchestration interface representing the FFmpeg Render Engine."""

    def render(
        self,
        request: RenderRequest,
        progress_callback: Optional[Any] = None,
        cancellation_token: Optional[Any] = None,
    ) -> RenderResult:
        """Execute a single rendering request synchronously with cancellation and progress reporting.

        Args:
            request: The complete typed RenderRequest container.
            progress_callback: Callback function invoked with RenderProgress objects.
            cancellation_token: Token to request process termination mid-render.

        Returns:
            A detailed RenderResult container.
        """
        ...

    def render_batch(
        self,
        request: BatchRenderRequest,
        progress_callback: Optional[Any] = None,
        cancellation_token: Optional[Any] = None,
    ) -> BatchRenderResult:
        """Execute a batch of rendering requests sequentially.

        Args:
            request: BatchRenderRequest containing multiple requests.
            progress_callback: Callback function for individual rendering telemetries.
            cancellation_token: Token to cancel overall batch processing.

        Returns:
            A BatchRenderResult with overall status and individual outcomes.
        """
        ...

    def validate(self, request: RenderRequest) -> RenderValidationReport:
        """Perform static pre-flight validation on the request and referenced assets.

        Args:
            request: The RenderRequest to analyze.

        Returns:
            RenderValidationReport.
        """
        ...

    def health(self, deep_check: bool = False) -> RendererHealthStatus:
        """Perform a lightweight or deep diagnostic capability check of FFmpeg/FFprobe.

        Args:
            deep_check: If True, performs a minimal test render to verify drivers.

        Returns:
            A RendererHealthStatus report.
        """
        ...

    def probe(self, path: Path) -> MediaMetadata:
        """Probe technical attributes of a media file.

        Args:
            path: Path to the media file on disk.

        Returns:
            MediaMetadata description.
        """
        ...

    def cancel(self, task_id: str) -> bool:
        """Request active execution cancellation for a specific task.

        Args:
            task_id: Unique task tracking identifier.

        Returns:
            True if cancellation request was registered, False otherwise.
        """
        ...
