"""Exception hierarchy for Module 10: FFmpeg Render Engine.

This module defines all custom exceptions raised by the video composition and
rendering pipeline to ensure robust error handling, process monitoring,
and professional exception chaining.
"""

class RenderEngineError(Exception):
    """Base exception class for all errors originating in the FFmpeg Render Engine (Module 10)."""
    pass


# Configuration & Executable Locator Errors
class RenderConfigError(RenderEngineError):
    """Raised when there is an invalid configuration for the render engine or its sub-components."""
    pass


class FFmpegNotFoundError(RenderConfigError):
    """Raised when the FFmpeg executable cannot be located or is inaccessible."""
    pass


class FFprobeNotFoundError(RenderConfigError):
    """Raised when the FFprobe executable cannot be located or is inaccessible."""
    pass


class UnsupportedFFmpegVersionError(RenderConfigError):
    """Raised when the detected FFmpeg version lacks required features or is too old."""
    pass


# Capability Detection Errors
class CapabilityDetectionError(RenderEngineError):
    """Raised when probing FFmpeg capabilities (encoders, decoders, filters) fails."""
    pass


class UnsupportedEncoderError(CapabilityDetectionError):
    """Raised when a requested hardware or software encoder is unavailable in the FFmpeg build."""
    pass


class UnsupportedDecoderError(CapabilityDetectionError):
    """Raised when a requested hardware or software decoder is unavailable in the FFmpeg build."""
    pass


# Input Validation & Probing Errors
class InvalidRenderRequestError(RenderEngineError):
    """Raised when a render request has missing, contradictory, or invalid parameter inputs."""
    pass


class InvalidMediaInputError(RenderEngineError):
    """Base exception for invalid, corrupt, or unsupported input media assets."""
    pass


class MissingInputFileError(InvalidMediaInputError):
    """Raised when a specified input media, audio, subtitle, logo, or watermark file is missing."""
    pass


class CorruptedMediaError(InvalidMediaInputError):
    """Raised when an input file is corrupted and cannot be decoded or processed by FFprobe/FFmpeg."""
    pass


class UnsupportedMediaFormatError(InvalidMediaInputError):
    """Raised when an input file format, codec, or container is unsupported."""
    pass


class MediaProbeError(RenderEngineError):
    """Raised when querying file metadata or analyzing streams via FFprobe fails."""
    pass


# Planning & Command Construction Errors
class InvalidRenderPlanError(RenderEngineError):
    """Raised when a render request cannot be resolved into a logical, coherent execution plan."""
    pass


class FilterGraphConstructionError(RenderEngineError):
    """Raised when assembling or parsing complex filter graph strings fails."""
    pass


class CommandConstructionError(RenderEngineError):
    """Raised when generating FFmpeg command line arguments fails."""
    pass


# Process Execution & Runtime Errors
class ProcessStartError(RenderEngineError):
    """Raised when starting the FFmpeg or FFprobe child subprocess fails."""
    pass


class RenderFailureError(RenderEngineError):
    """Raised when the FFmpeg rendering subprocess terminates with a non-zero exit code or runtime failure."""
    pass


class RenderTimeoutError(RenderFailureError):
    """Raised when rendering execution exceeds the configured timeout threshold."""
    pass


class RenderCancelledError(RenderFailureError):
    """Raised when a rendering task is explicitly and cooperatively cancelled by the user."""
    pass


# Hardware Acceleration & GPU-Specific Errors
class GPUEncoderError(RenderFailureError):
    """Raised when a hardware encoder (e.g., NVENC, QSV, AMF) fails or crashes during execution."""
    pass


class GPUOutOfMemoryError(GPUEncoderError):
    """Raised when the GPU runs out of memory during hardware-accelerated rendering."""
    pass


class CPUFallbackError(RenderFailureError):
    """Raised when falling back from a failed GPU execution to CPU software rendering fails."""
    pass


# Subtitle & Audio Mixing Errors
class SubtitleOverlayError(RenderFailureError):
    """Raised when burning or overlaying subtitles (ASS/SRT) onto the video track fails."""
    pass


class AudioMixingError(RenderFailureError):
    """Raised when combining, delaying, trimming, or ducking audio streams fails."""
    pass


# Output Verification & File Errors
class OutputFileError(RenderEngineError):
    """Raised when writing, renaming, or saving the final rendered video to disk fails."""
    pass


class OutputValidationError(RenderEngineError):
    """Raised when the rendered video fails post-generation integrity or quality checks."""
    pass


# Temporary Workspace Errors
class TemporaryFileError(RenderEngineError):
    """Raised when managing, creating, or tracking intermediate rendering workspaces fails."""
    pass


class CleanupError(TemporaryFileError):
    """Raised when deleting temporary intermediate files or cleaning up the workspace fails."""
    pass
