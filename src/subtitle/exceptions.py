"""Exception hierarchy for Module 09: Subtitle Engine.

This module defines all custom exceptions raised by the Subtitle Engine
to ensure clean error handling, strict validation, and professional exception chaining.
"""

class SubtitleEngineError(Exception):
    """Base exception class for all errors originating in the Subtitle Engine (Module 09)."""
    pass


# Configuration & Style Errors
class SubtitleConfigError(SubtitleEngineError):
    """Raised when there is an invalid configuration for the subtitle engine or its components."""
    pass


class SubtitleStyleError(SubtitleEngineError):
    """Raised when there is an error managing, loading, or applying ASS or custom style presets."""
    pass


# Text Segmentation & Timing Errors
class SubtitleSegmentationError(SubtitleEngineError):
    """Raised when splitting or chunking long text segments into subtitle lines fails."""
    pass


class SubtitleAlignmentError(SubtitleEngineError):
    """Raised when aligning generated subtitle blocks to audio timing or word timestamps fails."""
    pass


class KaraokeGenerationError(SubtitleEngineError):
    """Raised when word-by-word karaoke highlighting or tag generation fails."""
    pass


# Validation Errors
class SubtitleValidationError(SubtitleEngineError):
    """Base exception for subtitle validation failures."""
    pass


class SubtitleOverlapError(SubtitleValidationError):
    """Raised when two or more subtitle blocks overlap in time."""
    pass


class InvalidDurationError(SubtitleValidationError):
    """Raised when a subtitle block has a negative duration, zero duration, or is otherwise broken."""
    pass


class ReadingSpeedViolationError(SubtitleValidationError):
    """Raised when reading speed exceeds or falls below configured characters-per-second thresholds."""
    pass


class BrokenBlockError(SubtitleValidationError):
    """Raised when a subtitle block has malformed structural properties (e.g. empty text, excess lines)."""
    pass


# Export & Output Errors
class SubtitleExportError(SubtitleEngineError):
    """Raised when formatting, encoding, or exporting subtitle files (SRT, ASS, TXT) fails."""
    pass


class FileOutputError(SubtitleExportError):
    """Raised when writing the final subtitle asset file to disk fails."""
    pass
