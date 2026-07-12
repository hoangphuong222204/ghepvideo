"""Exception hierarchy for Module 09: Subtitle Engine.

This module defines all custom exceptions raised by the Subtitle Engine
to ensure clean error handling, strict validation, and professional exception chaining.
"""

class SubtitleEngineError(Exception):
    """Base exception class for all errors originating in the Subtitle Engine (Module 09)."""
    pass


# Configuration & Environment Errors
class SubtitleConfigError(SubtitleEngineError):
    """Raised when there is an invalid configuration for the subtitle engine or its components."""
    pass


class SubtitleDependencyError(SubtitleEngineError):
    """Raised when an optional or required external dependency or file is missing or unavailable."""
    pass


class UnsupportedFormatError(SubtitleEngineError):
    """Raised when a requested subtitle output format is not supported by the system."""
    pass


# Request & Input Validation Errors
class InvalidRequestError(SubtitleEngineError):
    """Raised when a subtitle generation request contains invalid, contradictory, or empty parameters."""
    pass


class InvalidTextError(InvalidRequestError):
    """Raised when input text is empty, malformed, or cannot be processed."""
    pass


class InvalidLanguageError(InvalidRequestError):
    """Raised when the specified language is empty, unsupported, or mismatched with input."""
    pass


class InvalidTimingError(InvalidRequestError):
    """Raised when timing parameters (e.g., word/sentence timing, duration) are invalid or negative."""
    pass


class InsufficientTimingError(InvalidTimingError):
    """Raised when the provided timing data is insufficient or contradictory to the requested mode."""
    pass


class WordTimingError(InvalidTimingError):
    """Raised when word-level timing arrays contain malformed or out-of-bounds timestamps."""
    pass


class SentenceTimingError(InvalidTimingError):
    """Raised when sentence-level timing arrays contain malformed or out-of-bounds timestamps."""
    pass


# Text Processing, Line Breaking & Timing Alignment Errors
class SubtitleSegmentationError(SubtitleEngineError):
    """Raised when splitting or chunking long text segments into subtitle lines fails."""
    pass


class LineBreakingError(SubtitleEngineError):
    """Raised when a subtitle block's lines cannot be formatted within character/line limits."""
    pass


class SubtitleAlignmentError(SubtitleEngineError):
    """Raised when aligning generated subtitle blocks to audio timing or word timestamps fails."""
    pass


class KaraokeGenerationError(SubtitleEngineError):
    """Raised when word-by-word karaoke highlighting or tag generation fails."""
    pass


# Timeline Validation Errors
class SubtitleValidationError(SubtitleEngineError):
    """Base exception for subtitle timeline validation failures under strict validation."""
    pass


class SubtitleOverlapError(SubtitleValidationError):
    """Raised when two or more subtitle cues overlap in time on a non-layering timeline."""
    pass


class InvalidDurationError(SubtitleValidationError):
    """Raised when a subtitle cue has a negative duration, zero duration, or exceeds limits."""
    pass


class ReadingSpeedViolationError(SubtitleValidationError):
    """Raised when reading speed exceeds or falls below configured characters-per-second thresholds."""
    pass


class InvalidCueError(SubtitleValidationError):
    """Raised when a single subtitle cue contains invalid characters, empty texts, or malformed indices."""
    pass


class SubtitleStyleError(SubtitleEngineError):
    """Raised when an ASS style preset name or custom style configuration is invalid or missing."""
    pass


# Export & Output File Errors
class SubtitleExportError(SubtitleEngineError):
    """Raised when formatting, encoding, or exporting subtitle files (SRT, ASS) fails."""
    pass


class SubtitleSerializationError(SubtitleExportError):
    """Raised when formatting or converting the in-memory timeline into a standard string payload fails."""
    pass


class FileOutputError(SubtitleExportError):
    """Raised when writing the final subtitle asset file to disk fails."""
    pass


class AtomicWriteError(FileOutputError):
    """Raised when executing an atomic write swap using temporary file commits fails."""
    pass


class OutputValidationError(SubtitleExportError):
    """Raised when the exported file fails post-write syntax or structural integrity checks."""
    pass


# Lifecycle and Flow Errors
class GenerationCancelledError(SubtitleEngineError):
    """Raised when the subtitle generation process is stopped by a cooperative cancellation request."""
    pass
