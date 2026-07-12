"""Public data models, configurations, and result types for Module 09.

This module contains strongly-typed structures for requesting subtitle generation,
tracking process results, managing styling, validating timings, and reporting health.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.subtitle.exceptions import (
    InvalidRequestError,
    InvalidTextError,
    InvalidTimingError,
    InsufficientTimingError,
    UnsupportedFormatError,
)


class TimingMode(Enum):
    """Supported alignment and timing source modes."""
    PROVIDED_WORD_TIMING = "provided_word_timing"
    PROVIDED_SENTENCE_TIMING = "provided_sentence_timing"
    ESTIMATED_FROM_AUDIO_DURATION = "estimated_from_audio_duration"
    ESTIMATED_FROM_TEXT = "estimated_from_text"


class SubtitleFormat(Enum):
    """Exporters and targets output subtitle formats."""
    SRT = "srt"
    ASS = "ass"


class TaskStatus(Enum):
    """Lifecycle states of subtitle tasks."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class HealthStatus(Enum):
    """Structural health status values of the Subtitle Engine."""
    READY = "ready"
    DEGRADED = "degraded"
    NOT_CONFIGURED = "not_configured"
    DEPENDENCY_MISSING = "dependency_missing"
    ERROR = "error"


class AudioChannelMode(Enum):
    """Audio channels configuration."""
    MONO = "mono"
    STEREO = "stereo"


@dataclass
class WordTiming:
    """Strongly-typed, single-word timing structure."""
    text: str
    start_seconds: float
    end_seconds: float
    confidence: Optional[float] = None
    source_metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise InvalidTextError("WordTiming text cannot be empty or blank whitespace.")
        
        if not math.isfinite(self.start_seconds) or not math.isfinite(self.end_seconds):
            raise InvalidTimingError("WordTiming start and end seconds must be finite floating points.")
        
        if self.start_seconds < 0:
            raise InvalidTimingError(f"WordTiming start_seconds cannot be negative, got {self.start_seconds}")
            
        if self.end_seconds < self.start_seconds:
            raise InvalidTimingError(
                f"WordTiming end_seconds ({self.end_seconds}) cannot be less than start_seconds ({self.start_seconds})"
            )
            
        if self.confidence is not None:
            if not math.isfinite(self.confidence) or not (0.0 <= self.confidence <= 1.0):
                raise InvalidTimingError(f"WordTiming confidence must be between 0.0 and 1.0, got {self.confidence}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize dataclass to dictionary cleanly."""
        return {
            "text": self.text,
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "confidence": self.confidence,
            "source_metadata": self.source_metadata,
        }


@dataclass
class SentenceTiming:
    """Strongly-typed sentence, chunk, or scene timing structure."""
    text: str
    start_seconds: float
    end_seconds: float
    word_timings: Optional[List[WordTiming]] = None

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise InvalidTextError("SentenceTiming text cannot be empty or blank whitespace.")
            
        if not math.isfinite(self.start_seconds) or not math.isfinite(self.end_seconds):
            raise InvalidTimingError("SentenceTiming start and end seconds must be finite floating points.")
            
        if self.start_seconds < 0:
            raise InvalidTimingError(f"SentenceTiming start_seconds cannot be negative, got {self.start_seconds}")
            
        if self.end_seconds < self.start_seconds:
            raise InvalidTimingError(
                f"SentenceTiming end_seconds ({self.end_seconds}) cannot be less than start_seconds ({self.start_seconds})"
            )
            
        # Ensure child word timings are consistent with sentence bounds
        if self.word_timings:
            for wt in self.word_timings:
                if wt.start_seconds < self.start_seconds or wt.end_seconds > self.end_seconds:
                    raise InvalidTimingError(
                        f"Word timing ({wt.text}: {wt.start_seconds}-{wt.end_seconds}) exceeds sentence boundaries "
                        f"({self.start_seconds}-{self.end_seconds})"
                    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize dataclass to dictionary cleanly."""
        return {
            "text": self.text,
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "word_timings": [wt.to_dict() for wt in self.word_timings] if self.word_timings is not None else None,
        }


@dataclass
class SubtitleCue:
    """Single, validated subtitle display block containing formatted lines and timings."""
    cue_id: str
    index: int
    start_seconds: float
    end_seconds: float
    text: str
    lines: List[str]
    word_timings: Optional[List[WordTiming]] = None
    style_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.cue_id or not self.cue_id.strip():
            raise InvalidRequestError("SubtitleCue cue_id cannot be empty.")
            
        if self.index < 0:
            raise InvalidRequestError(f"SubtitleCue index cannot be negative, got {self.index}")
            
        if not math.isfinite(self.start_seconds) or not math.isfinite(self.end_seconds):
            raise InvalidTimingError("SubtitleCue start and end seconds must be finite floating points.")
            
        if self.start_seconds < 0:
            raise InvalidTimingError(f"SubtitleCue start_seconds cannot be negative, got {self.start_seconds}")
            
        if self.end_seconds < self.start_seconds:
            raise InvalidTimingError(
                f"SubtitleCue end_seconds ({self.end_seconds}) cannot be less than start_seconds ({self.start_seconds})"
            )
            
        if not self.text or not self.text.strip():
            raise InvalidTextError("SubtitleCue text content cannot be empty.")
            
        if not self.lines:
            raise InvalidTextError("SubtitleCue lines list cannot be empty.")
            
        # Verify word timings are within cue boundaries
        if self.word_timings:
            for wt in self.word_timings:
                # Allow a tiny floating-point tolerance of 1e-5
                if wt.start_seconds < (self.start_seconds - 1e-5) or wt.end_seconds > (self.end_seconds + 1e-5):
                    raise InvalidTimingError(
                        f"Word timing ({wt.text}: {wt.start_seconds}-{wt.end_seconds}) exceeds subtitle cue bounds "
                        f"({self.start_seconds}-{self.end_seconds})"
                    )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize dataclass to dictionary cleanly."""
        return {
            "cue_id": self.cue_id,
            "index": self.index,
            "start_seconds": self.start_seconds,
            "end_seconds": self.end_seconds,
            "text": self.text,
            "lines": self.lines,
            "word_timings": [wt.to_dict() for wt in self.word_timings] if self.word_timings is not None else None,
            "style_name": self.style_name,
            "metadata": self.metadata,
        }


@dataclass
class ASSStyle:
    """Parameters representing an ASS (Advanced Substation Alpha) styling record."""
    style_name: str
    font_family: str
    font_size: float
    bold: bool = False
    italic: bool = False
    primary_color: str = "&H00FFFFFF"      # Format: &H[AA][BB][GG][RR]
    secondary_color: str = "&H000000FF"
    outline_color: str = "&H00000000"
    background_color: str = "&H00000000"
    outline_width: float = 2.0
    shadow_depth: float = 0.0
    alignment: int = 2                       # 2 = centered bottom
    margin_left: int = 10
    margin_right: int = 10
    margin_vertical: int = 10
    scale_x: float = 100.0
    scale_y: float = 100.0
    spacing: float = 0.0
    angle: float = 0.0
    border_style: int = 1                    # 1: standard outline+shadow, 3: opaque box background

    def __post_init__(self) -> None:
        if not self.style_name or not self.style_name.strip():
            raise InvalidRequestError("ASSStyle style_name cannot be empty.")
            
        if not self.font_family or not self.font_family.strip():
            raise InvalidRequestError("ASSStyle font_family cannot be empty.")
            
        if self.font_size <= 0:
            raise InvalidRequestError(f"ASSStyle font_size must be positive, got {self.font_size}")
            
        if self.outline_width < 0:
            raise InvalidRequestError(f"ASSStyle outline_width cannot be negative, got {self.outline_width}")
            
        if self.shadow_depth < 0:
            raise InvalidRequestError(f"ASSStyle shadow_depth cannot be negative, got {self.shadow_depth}")
            
        if not (1 <= self.alignment <= 9):
            raise InvalidRequestError(f"ASSStyle alignment must be between 1 and 9 inclusive, got {self.alignment}")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize style fields as a dictionary."""
        return asdict(self)


@dataclass
class SubtitleValidationReport:
    """Results of a comprehensive layout, sequence, speed, and timing analysis."""
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info_issues: List[str] = field(default_factory=list)
    repair_actions_performed: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if there are no errors on the report."""
        return len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize report lists to dict."""
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "info_issues": self.info_issues,
            "repair_actions_performed": self.repair_actions_performed,
            "is_valid": self.is_valid,
        }


@dataclass
class SubtitleRequest:
    """Configuration package defining text, timing inputs, constraints, and styling targets."""
    text: str
    language: str = "vi"
    output_format: SubtitleFormat = SubtitleFormat.SRT
    output_path: Optional[Path] = None
    output_dir: Optional[Path] = None
    sentence_timing: Optional[List[SentenceTiming]] = None
    word_timing: Optional[List[WordTiming]] = None
    audio_duration: Optional[float] = None
    timing_mode: TimingMode = TimingMode.ESTIMATED_FROM_TEXT
    target_platform: Optional[str] = None
    max_chars_per_line: int = 37
    max_lines: int = 2
    min_cue_duration: float = 0.5
    max_cue_duration: float = 7.0
    max_reading_speed: float = 15.0  # characters per second (CPS)
    min_gap: float = 0.05
    karaoke_enabled: bool = False
    ass_style_preset: Optional[str] = None
    custom_ass_style: Optional[ASSStyle] = None
    estimated_timing_enabled: bool = False
    strict_validation: bool = True

    def __post_init__(self) -> None:
        if not self.text or not self.text.strip():
            raise InvalidTextError("SubtitleRequest text cannot be empty or whitespace.")
            
        if not self.language or not self.language.strip():
            raise InvalidRequestError("SubtitleRequest language cannot be empty.")
            
        if self.max_chars_per_line <= 0:
            raise InvalidRequestError("max_chars_per_line must be greater than zero.")
            
        if self.max_lines <= 0:
            raise InvalidRequestError("max_lines must be greater than zero.")
            
        if self.min_cue_duration <= 0:
            raise InvalidRequestError("min_cue_duration must be greater than zero.")
            
        if self.max_cue_duration < self.min_cue_duration:
            raise InvalidRequestError("max_cue_duration must be greater than or equal to min_cue_duration.")
            
        if self.max_reading_speed <= 0:
            raise InvalidRequestError("max_reading_speed must be positive.")
            
        if self.min_gap < 0:
            raise InvalidRequestError("min_gap cannot be negative.")

        # Specific constraints depending on TimingMode
        if self.timing_mode == TimingMode.PROVIDED_WORD_TIMING:
            if not self.word_timing:
                raise InsufficientTimingError(
                    "PROVIDED_WORD_TIMING requested but no word_timing data was supplied."
                )
        elif self.timing_mode == TimingMode.PROVIDED_SENTENCE_TIMING:
            if not self.sentence_timing:
                raise InsufficientTimingError(
                    "PROVIDED_SENTENCE_TIMING requested but no sentence_timing data was supplied."
                )
        elif self.timing_mode == TimingMode.ESTIMATED_FROM_AUDIO_DURATION:
            if self.audio_duration is None or self.audio_duration <= 0:
                raise InsufficientTimingError(
                    "ESTIMATED_FROM_AUDIO_DURATION requested but valid audio_duration was not provided."
                )

        if self.output_path:
            self.output_path = Path(self.output_path)
        if self.output_dir:
            self.output_dir = Path(self.output_dir)

    def to_dict(self) -> Dict[str, Any]:
        """Convert request to a serializable dictionary representation."""
        return {
            "text": self.text,
            "language": self.language,
            "output_format": self.output_format.value,
            "output_path": str(self.output_path) if self.output_path else None,
            "output_dir": str(self.output_dir) if self.output_dir else None,
            "sentence_timing": [st.to_dict() for st in self.sentence_timing] if self.sentence_timing else None,
            "word_timing": [wt.to_dict() for wt in self.word_timing] if self.word_timing else None,
            "audio_duration": self.audio_duration,
            "timing_mode": self.timing_mode.value,
            "target_platform": self.target_platform,
            "max_chars_per_line": self.max_chars_per_line,
            "max_lines": self.max_lines,
            "min_cue_duration": self.min_cue_duration,
            "max_cue_duration": self.max_cue_duration,
            "max_reading_speed": self.max_reading_speed,
            "min_gap": self.min_gap,
            "karaoke_enabled": self.karaoke_enabled,
            "ass_style_preset": self.ass_style_preset,
            "custom_ass_style": self.custom_ass_style.to_dict() if self.custom_ass_style else None,
            "estimated_timing_enabled": self.estimated_timing_enabled,
            "strict_validation": self.strict_validation,
        }


@dataclass
class BatchSubtitleRequest:
    """Group of subtitle configurations processed in one operation."""
    requests: List[SubtitleRequest]
    batch_id: str

    def __post_init__(self) -> None:
        if not self.requests:
            raise InvalidRequestError("BatchSubtitleRequest requests list cannot be empty.")
        if not self.batch_id or not self.batch_id.strip():
            raise InvalidRequestError("BatchSubtitleRequest batch_id cannot be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requests": [req.to_dict() for req in self.requests],
            "batch_id": self.batch_id,
        }


@dataclass
class SubtitleGenerationResult:
    """The final completed output state of a single Subtitle Request."""
    task_id: str
    status: TaskStatus
    subtitle_path: Optional[Path]
    subtitle_format: SubtitleFormat
    timeline: List[SubtitleCue]
    cue_count: int
    total_duration_seconds: float
    timing_mode_used: TimingMode
    estimated_timing: bool
    karaoke_enabled: bool
    validation_report: SubtitleValidationReport
    warnings: List[str]
    generation_duration_seconds: float
    error_info: Optional[str] = None

    def __post_init__(self) -> None:
        if self.subtitle_path:
            self.subtitle_path = Path(self.subtitle_path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to a serializable dictionary representation."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "subtitle_path": str(self.subtitle_path) if self.subtitle_path else None,
            "subtitle_format": self.subtitle_format.value,
            "timeline": [cue.to_dict() for cue in self.timeline],
            "cue_count": self.cue_count,
            "total_duration_seconds": self.total_duration_seconds,
            "timing_mode_used": self.timing_mode_used.value,
            "estimated_timing": self.estimated_timing,
            "karaoke_enabled": self.karaoke_enabled,
            "validation_report": self.validation_report.to_dict(),
            "warnings": self.warnings,
            "generation_duration_seconds": self.generation_duration_seconds,
            "error_info": self.error_info,
        }


@dataclass
class BatchSubtitleGenerationResult:
    """The final aggregate outcomes of a batch process."""
    batch_id: str
    overall_status: TaskStatus
    results: List[SubtitleGenerationResult]
    success_count: int
    failure_count: int
    cancelled_count: int
    total_generation_time: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch result to serializable dict."""
        return {
            "batch_id": self.batch_id,
            "overall_status": self.overall_status.value,
            "results": [res.to_dict() for res in self.results],
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "cancelled_count": self.cancelled_count,
            "total_generation_time": self.total_generation_time,
        }


@dataclass
class SubtitleExportResult:
    """Successful payload describing a written SRT or ASS file's properties."""
    output_path: Path
    format: SubtitleFormat
    encoding: str
    file_size_bytes: int
    cue_count: int
    duration_seconds: float
    validation_report: SubtitleValidationReport
    warnings: List[str]

    def __post_init__(self) -> None:
        self.output_path = Path(self.output_path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert export result to dictionary."""
        return {
            "output_path": str(self.output_path),
            "format": self.format.value,
            "encoding": self.encoding,
            "file_size_bytes": self.file_size_bytes,
            "cue_count": self.cue_count,
            "duration_seconds": self.duration_seconds,
            "validation_report": self.validation_report.to_dict(),
            "warnings": self.warnings,
        }


@dataclass
class SubtitleHealthStatus:
    """Diagnostics indicating available features, encoders, and styles."""
    status: HealthStatus
    srt_supported: bool
    ass_supported: bool
    karaoke_supported: bool
    word_timing_supported: bool
    estimated_timing_supported: bool
    available_style_presets: List[str]
    optional_dependency_availability: Dict[str, bool]
    default_encoding: str
    last_error_summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert health status to dict."""
        return {
            "status": self.status.value,
            "srt_supported": self.srt_supported,
            "ass_supported": self.ass_supported,
            "karaoke_supported": self.karaoke_supported,
            "word_timing_supported": self.word_timing_supported,
            "estimated_timing_supported": self.estimated_timing_supported,
            "available_style_presets": self.available_style_presets,
            "optional_dependency_availability": self.optional_dependency_availability,
            "default_encoding": self.default_encoding,
            "last_error_summary": self.last_error_summary,
        }
