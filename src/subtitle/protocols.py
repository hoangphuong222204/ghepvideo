"""Structural typing protocols for Module 09: Subtitle Engine.

These protocols define standard contracts for all major subtitle sub-components,
supporting complete dependency injection, clean mock-based testing, and decoupling.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from src.subtitle.subtitle_models import (
    ASSStyle,
    BatchSubtitleGenerationResult,
    BatchSubtitleRequest,
    SubtitleCue,
    SubtitleExportResult,
    SubtitleGenerationResult,
    SubtitleHealthStatus,
    SubtitleRequest,
    SubtitleValidationReport,
)


@runtime_checkable
class TextSegmenterProtocol(Protocol):
    """Protocol for naturally segmenting spoken languages into phrase chunks."""
    
    def segment(self, text: str, language: str = "vi") -> List[str]:
        """Split or group text into natural reading phrase segments.
        
        Args:
            text: Raw input spoken script.
            language: Target ISO code (e.g., 'vi' or 'en').
            
        Returns:
            A list of naturally separated text phrases.
        """
        ...


@runtime_checkable
class LineBreakerProtocol(Protocol):
    """Protocol for splitting single subtitle cue text into individual screen lines."""
    
    def break_lines(
        self, text: str, max_chars_per_line: int = 37, max_lines: int = 2
    ) -> List[str]:
        """Break a text phrase into lines according to styling limits.
        
        Args:
            text: Input cue text.
            max_chars_per_line: Maximum character limit per line.
            max_lines: Maximum allowed rows for a single cue.
            
        Returns:
            A list of lines representing the broken cue.
        """
        ...


@runtime_checkable
class TimingAlignerProtocol(Protocol):
    """Protocol for assigning precise durations and timestamps to text segments."""
    
    def align_timings(self, request: SubtitleRequest) -> List[SubtitleCue]:
        """Align segment durations against word timings, sentence timings, or estimations.
        
        Args:
            request: The subtitle request containing configuration and raw segment/timing inputs.
            
        Returns:
            A sequential, timed list of SubtitleCues.
        """
        ...


@runtime_checkable
class KaraokeGeneratorProtocol(Protocol):
    """Protocol for embedding karaoke centisecond timing markers in ASS subtitle blocks."""
    
    def generate_karaoke_tags(self, cue: SubtitleCue, style_mode: str = "kf") -> str:
        """Inject ASS karaoke animation tags (e.g. \\k, \\kf) based on word timings.
        
        Args:
            cue: SubtitleCue containing validated word timing arrays.
            style_mode: ASS tag selection ('k', 'K', 'kf', 'ko').
            
        Returns:
            An ASS formatted dialogue text string with embedded animation tags.
        """
        ...


@runtime_checkable
class ASSStyleManagerProtocol(Protocol):
    """Protocol for resolving ASS presentation style sheets and presets."""
    
    def get_style(self, preset_name: str) -> ASSStyle:
        """Retrieve a predefined or custom registered style sheet.
        
        Args:
            preset_name: Unique identifier for a style (e.g., 'tiktok_vertical').
            
        Returns:
            The associated ASSStyle configuration.
        """
        ...
        
    def get_available_presets(self) -> List[str]:
        """Return a list of all pre-configured style names.
        
        Returns:
            List of style names.
        """
        ...


@runtime_checkable
class SubtitleValidatorProtocol(Protocol):
    """Protocol for auditing layout limits, overlaps, reading rates, and integrity."""
    
    def validate_timeline(
        self, timeline: List[SubtitleCue], strict_validation: bool = True
    ) -> SubtitleValidationReport:
        """Analyze a list of cues for semantic, formatting, and timing issues.
        
        Args:
            timeline: The sequence of SubtitleCues to analyze.
            strict_validation: If True, raises exceptions for critical errors.
            
        Returns:
            A detailed SubtitleValidationReport.
        """
        ...


@runtime_checkable
class SubtitleExporterProtocol(Protocol):
    """Protocol for serializing in-memory timelines and writing them to disk."""
    
    def export(
        self,
        timeline: List[SubtitleCue],
        output_path: Path,
        style: Optional[ASSStyle] = None,
        overwrite: bool = True,
    ) -> SubtitleExportResult:
        """Serialize timeline to file (SRT or ASS depending on target extension).
        
        Args:
            timeline: The subtitle cues to write.
            output_path: Absolute target path.
            style: Optional styling config sheet (used if format is ASS).
            overwrite: If False, errors out if file already exists.
            
        Returns:
            A SubtitleExportResult report.
        """
        ...


@runtime_checkable
class SubtitleEngineProtocol(Protocol):
    """Top-level orchestration interface representing the Subtitle Engine."""
    
    def generate(self, request: SubtitleRequest) -> SubtitleGenerationResult:
        """Orchestrate text splitting, alignment, validation, and file writing.
        
        Args:
            request: Input text and timing payload.
            
        Returns:
            A SubtitleGenerationResult payload.
        """
        ...
        
    def generate_batch(self, request: BatchSubtitleRequest) -> BatchSubtitleGenerationResult:
        """Run batch processing over multiple parallel subtitle requests.
        
        Args:
            request: Container with list of requests.
            
        Returns:
            BatchSubtitleGenerationResult.
        """
        ...
        
    def validate(self, timeline: List[SubtitleCue], strict: bool = True) -> SubtitleValidationReport:
        """Validate a timeline without generating a file.
        
        Args:
            timeline: List of subtitle cues.
            strict: If True, invalid properties raise exceptions.
            
        Returns:
            The validation report.
        """
        ...
        
    def health(self) -> SubtitleHealthStatus:
        """Return a lightweight health report of capability and dependency availability.
        
        Returns:
            SubtitleHealthStatus.
        """
        ...
