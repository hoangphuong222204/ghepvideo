"""Tests for Module 09 public foundations, models, exceptions, and serialization."""

import math
from pathlib import Path
import unittest

from src.subtitle import (
    # Exceptions
    SubtitleEngineError,
    SubtitleConfigError,
    SubtitleDependencyError,
    UnsupportedFormatError,
    InvalidRequestError,
    InvalidTextError,
    InvalidLanguageError,
    InvalidTimingError,
    InsufficientTimingError,
    WordTimingError,
    SentenceTimingError,
    SubtitleSegmentationError,
    LineBreakingError,
    SubtitleAlignmentError,
    KaraokeGenerationError,
    SubtitleValidationError,
    SubtitleOverlapError,
    InvalidDurationError,
    ReadingSpeedViolationError,
    InvalidCueError,
    SubtitleStyleError,
    SubtitleExportError,
    SubtitleSerializationError,
    FileOutputError,
    AtomicWriteError,
    OutputValidationError,
    GenerationCancelledError,
    
    # Enums
    TimingMode,
    SubtitleFormat,
    TaskStatus,
    HealthStatus,
    AudioChannelMode,
    
    # Models
    WordTiming,
    SentenceTiming,
    SubtitleCue,
    ASSStyle,
    SubtitleValidationReport,
    SubtitleRequest,
    BatchSubtitleRequest,
    SubtitleGenerationResult,
    BatchSubtitleGenerationResult,
    SubtitleExportResult,
    SubtitleHealthStatus,
    
    # Protocols
    TextSegmenterProtocol,
    LineBreakerProtocol,
    TimingAlignerProtocol,
    KaraokeGeneratorProtocol,
    ASSStyleManagerProtocol,
    SubtitleValidatorProtocol,
    SubtitleExporterProtocol,
    SubtitleEngineProtocol,
)


class TestPublicImports(unittest.TestCase):
    """Verify that all elements in __all__ are successfully imported and correct types."""

    def test_imports_presence(self) -> None:
        """Check presence of core classes and verify they are callable/types."""
        self.assertTrue(issubclass(SubtitleEngineError, Exception))
        self.assertTrue(issubclass(SubtitleValidationError, SubtitleEngineError))
        self.assertIsInstance(TimingMode.PROVIDED_WORD_TIMING, TimingMode)
        self.assertIs(SubtitleFormat.SRT, SubtitleFormat("srt"))


class TestExceptionHierarchy(unittest.TestCase):
    """Verify the structured exception hierarchy of Module 09."""

    def test_hierarchy_relationships(self) -> None:
        """Assert exception classes inherit from appropriate bases."""
        # Config & Styles
        self.assertTrue(issubclass(SubtitleConfigError, SubtitleEngineError))
        self.assertTrue(issubclass(SubtitleStyleError, SubtitleEngineError))
        self.assertTrue(issubclass(SubtitleDependencyError, SubtitleEngineError))
        self.assertTrue(issubclass(UnsupportedFormatError, SubtitleEngineError))

        # Request & Input
        self.assertTrue(issubclass(InvalidRequestError, SubtitleEngineError))
        self.assertTrue(issubclass(InvalidTextError, InvalidRequestError))
        self.assertTrue(issubclass(InvalidLanguageError, InvalidRequestError))
        self.assertTrue(issubclass(InvalidTimingError, InvalidRequestError))
        self.assertTrue(issubclass(InsufficientTimingError, InvalidTimingError))
        self.assertTrue(issubclass(WordTimingError, InvalidTimingError))
        self.assertTrue(issubclass(SentenceTimingError, InvalidTimingError))

        # Text Process & Align
        self.assertTrue(issubclass(SubtitleSegmentationError, SubtitleEngineError))
        self.assertTrue(issubclass(LineBreakingError, SubtitleEngineError))
        self.assertTrue(issubclass(SubtitleAlignmentError, SubtitleEngineError))
        self.assertTrue(issubclass(KaraokeGenerationError, SubtitleEngineError))

        # Validation
        self.assertTrue(issubclass(SubtitleValidationError, SubtitleEngineError))
        self.assertTrue(issubclass(SubtitleOverlapError, SubtitleValidationError))
        self.assertTrue(issubclass(InvalidDurationError, SubtitleValidationError))
        self.assertTrue(issubclass(ReadingSpeedViolationError, SubtitleValidationError))
        self.assertTrue(issubclass(InvalidCueError, SubtitleValidationError))

        # Export & Output
        self.assertTrue(issubclass(SubtitleExportError, SubtitleEngineError))
        self.assertTrue(issubclass(SubtitleSerializationError, SubtitleExportError))
        self.assertTrue(issubclass(FileOutputError, SubtitleExportError))
        self.assertTrue(issubclass(AtomicWriteError, FileOutputError))
        self.assertTrue(issubclass(OutputValidationError, SubtitleExportError))

        # Flow
        self.assertTrue(issubclass(GenerationCancelledError, SubtitleEngineError))

    def test_exception_chaining(self) -> None:
        """Test exception raising and standard string descriptions."""
        with self.assertRaises(SubtitleEngineError) as context:
            raise SubtitleEngineError("Test base error")
        self.assertEqual(str(context.exception), "Test base error")


class TestEnumStability(unittest.TestCase):
    """Verify that Enum keys and database/API-facing string values are stable."""

    def test_timing_mode_values(self) -> None:
        """Verify TimingMode values are exactly as specified."""
        self.assertEqual(TimingMode.PROVIDED_WORD_TIMING.value, "provided_word_timing")
        self.assertEqual(TimingMode.PROVIDED_SENTENCE_TIMING.value, "provided_sentence_timing")
        self.assertEqual(TimingMode.ESTIMATED_FROM_AUDIO_DURATION.value, "estimated_from_audio_duration")
        self.assertEqual(TimingMode.ESTIMATED_FROM_TEXT.value, "estimated_from_text")

    def test_subtitle_format_values(self) -> None:
        """Verify SubtitleFormat values are exactly as specified."""
        self.assertEqual(SubtitleFormat.SRT.value, "srt")
        self.assertEqual(SubtitleFormat.ASS.value, "ass")

    def test_task_status_values(self) -> None:
        """Verify TaskStatus values are exactly as specified."""
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.RUNNING.value, "running")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        self.assertEqual(TaskStatus.FAILED.value, "failed")
        self.assertEqual(TaskStatus.CANCELLED.value, "cancelled")

    def test_health_status_values(self) -> None:
        """Verify HealthStatus values are exactly as specified."""
        self.assertEqual(HealthStatus.READY.value, "ready")
        self.assertEqual(HealthStatus.DEGRADED.value, "degraded")
        self.assertEqual(HealthStatus.NOT_CONFIGURED.value, "not_configured")
        self.assertEqual(HealthStatus.DEPENDENCY_MISSING.value, "dependency_missing")
        self.assertEqual(HealthStatus.ERROR.value, "error")


class TestWordTimingValidation(unittest.TestCase):
    """Verify strict validation boundaries for single-word timings."""

    def test_valid_word_timing(self) -> None:
        """Verify creation of a perfect WordTiming record."""
        wt = WordTiming(text="Xin_chào", start_seconds=1.5, end_seconds=2.2, confidence=0.98)
        self.assertEqual(wt.text, "Xin_chào")
        self.assertEqual(wt.start_seconds, 1.5)
        self.assertEqual(wt.end_seconds, 2.2)
        self.assertEqual(wt.confidence, 0.98)

    def test_invalid_text_raise(self) -> None:
        """Verify blank or empty text throws exception."""
        with self.assertRaises(InvalidTextError):
            WordTiming(text="", start_seconds=1.0, end_seconds=2.0)
        with self.assertRaises(InvalidTextError):
            WordTiming(text="   ", start_seconds=1.0, end_seconds=2.0)

    def test_invalid_timestamps_raise(self) -> None:
        """Verify negative starts, backwards ranges, and nan/inf are rejected."""
        with self.assertRaises(InvalidTimingError):
            WordTiming(text="test", start_seconds=-0.5, end_seconds=1.0)
        with self.assertRaises(InvalidTimingError):
            WordTiming(text="test", start_seconds=2.0, end_seconds=1.5)
        with self.assertRaises(InvalidTimingError):
            WordTiming(text="test", start_seconds=math.nan, end_seconds=1.0)
        with self.assertRaises(InvalidTimingError):
            WordTiming(text="test", start_seconds=1.0, end_seconds=math.inf)

    def test_invalid_confidence_raise(self) -> None:
        """Verify confidence boundary enforcement."""
        with self.assertRaises(InvalidTimingError):
            WordTiming(text="test", start_seconds=1.0, end_seconds=2.0, confidence=-0.1)
        with self.assertRaises(InvalidTimingError):
            WordTiming(text="test", start_seconds=1.0, end_seconds=2.0, confidence=1.01)


class TestSentenceTimingValidation(unittest.TestCase):
    """Verify strict validation boundaries for sentence/phrase timings."""

    def test_valid_sentence_timing(self) -> None:
        """Verify creation of a perfect SentenceTiming record."""
        wt1 = WordTiming(text="Xin", start_seconds=1.0, end_seconds=1.5)
        wt2 = WordTiming(text="chào", start_seconds=1.5, end_seconds=2.0)
        st = SentenceTiming(text="Xin chào", start_seconds=1.0, end_seconds=2.0, word_timings=[wt1, wt2])
        self.assertEqual(st.text, "Xin chào")
        self.assertEqual(st.start_seconds, 1.0)
        self.assertEqual(st.end_seconds, 2.0)
        self.assertEqual(len(st.word_timings), 2)

    def test_word_timings_exceeding_sentence_bounds(self) -> None:
        """Verify child word timings cannot escape sentence boundaries."""
        wt_out = WordTiming(text="ngoài", start_seconds=0.5, end_seconds=1.2)
        with self.assertRaises(InvalidTimingError):
            SentenceTiming(text="Xin chào", start_seconds=1.0, end_seconds=2.0, word_timings=[wt_out])


class TestSubtitleCueValidation(unittest.TestCase):
    """Verify strict validation boundaries for SubtitleCue displays."""

    def test_valid_subtitle_cue(self) -> None:
        """Verify creation of a standard validated SubtitleCue."""
        wt = WordTiming(text="Hello", start_seconds=0.0, end_seconds=1.0)
        cue = SubtitleCue(
            cue_id="cue_001",
            index=1,
            start_seconds=0.0,
            end_seconds=1.0,
            text="Hello",
            lines=["Hello"],
            word_timings=[wt],
        )
        self.assertEqual(cue.cue_id, "cue_001")
        self.assertEqual(cue.index, 1)
        self.assertEqual(cue.start_seconds, 0.0)
        self.assertEqual(cue.end_seconds, 1.0)

    def test_invalid_cue_parameters(self) -> None:
        """Verify that negative indices, empty ids, and empty lines are rejected."""
        with self.assertRaises(InvalidRequestError):
            SubtitleCue(cue_id="", index=1, start_seconds=0.0, end_seconds=1.0, text="H", lines=["H"])
        with self.assertRaises(InvalidRequestError):
            SubtitleCue(cue_id="id", index=-1, start_seconds=0.0, end_seconds=1.0, text="H", lines=["H"])
        with self.assertRaises(InvalidTextError):
            SubtitleCue(cue_id="id", index=1, start_seconds=0.0, end_seconds=1.0, text="H", lines=[])


class TestASSStyleValidation(unittest.TestCase):
    """Verify boundaries for ASS formatting styles."""

    def test_valid_style(self) -> None:
        """Verify default and customized style creation."""
        style = ASSStyle(style_name="TikTok", font_family="Arial", font_size=24.0)
        self.assertEqual(style.style_name, "TikTok")
        self.assertEqual(style.font_family, "Arial")
        self.assertEqual(style.font_size, 24.0)
        self.assertEqual(style.alignment, 2)

    def test_invalid_style_parameters(self) -> None:
        """Verify negative outline, size and incorrect alignment raise."""
        with self.assertRaises(InvalidRequestError):
            ASSStyle(style_name="TikTok", font_family="Arial", font_size=-10.0)
        with self.assertRaises(InvalidRequestError):
            ASSStyle(style_name="TikTok", font_family="Arial", font_size=24.0, outline_width=-1.0)
        with self.assertRaises(InvalidRequestError):
            ASSStyle(style_name="TikTok", font_family="Arial", font_size=24.0, alignment=10)


class TestSubtitleRequestValidation(unittest.TestCase):
    """Verify strict validation and cross-parameter checks in requests."""

    def test_valid_request(self) -> None:
        """Verify default standard request creation is valid."""
        req = SubtitleRequest(text="Xin chào Việt Nam.")
        self.assertEqual(req.text, "Xin chào Việt Nam.")
        self.assertEqual(req.timing_mode, TimingMode.ESTIMATED_FROM_TEXT)

    def test_request_mode_validation(self) -> None:
        """Verify timing mode specific dependency checks."""
        # PROVIDED_WORD_TIMING without word timings should fail
        with self.assertRaises(InsufficientTimingError):
            SubtitleRequest(text="Hello", timing_mode=TimingMode.PROVIDED_WORD_TIMING)
            
        # PROVIDED_SENTENCE_TIMING without sentence timings should fail
        with self.assertRaises(InsufficientTimingError):
            SubtitleRequest(text="Hello", timing_mode=TimingMode.PROVIDED_SENTENCE_TIMING)
            
        # ESTIMATED_FROM_AUDIO_DURATION without audio_duration should fail
        with self.assertRaises(InsufficientTimingError):
            SubtitleRequest(text="Hello", timing_mode=TimingMode.ESTIMATED_FROM_AUDIO_DURATION)

    def test_invalid_structural_bounds(self) -> None:
        """Verify logical configuration values boundary enforcement."""
        with self.assertRaises(InvalidRequestError):
            SubtitleRequest(text="Hello", max_chars_per_line=0)
        with self.assertRaises(InvalidRequestError):
            SubtitleRequest(text="Hello", max_lines=0)
        with self.assertRaises(InvalidRequestError):
            SubtitleRequest(text="Hello", min_cue_duration=-0.1)


class TestSerialization(unittest.TestCase):
    """Verify clean, complete, recursive JSON-safe serialization for all models."""

    def test_word_timing_serialization(self) -> None:
        """Word timing dictionary formatting."""
        wt = WordTiming("Hello", 0.0, 1.0, confidence=0.95, source_metadata={"voice": "A"})
        d = wt.to_dict()
        self.assertEqual(d["text"], "Hello")
        self.assertEqual(d["start_seconds"], 0.0)
        self.assertEqual(d["end_seconds"], 1.0)
        self.assertEqual(d["confidence"], 0.95)
        self.assertEqual(d["source_metadata"]["voice"], "A")

    def test_subtitle_cue_serialization(self) -> None:
        """SubtitleCue dictionary formatting including sub-timings."""
        wt = WordTiming("Hello", 0.0, 1.0, confidence=0.95)
        cue = SubtitleCue(
            cue_id="id_1",
            index=1,
            start_seconds=0.0,
            end_seconds=1.0,
            text="Hello",
            lines=["Hello"],
            word_timings=[wt],
        )
        d = cue.to_dict()
        self.assertEqual(d["cue_id"], "id_1")
        self.assertEqual(d["lines"], ["Hello"])
        self.assertIsInstance(d["word_timings"], list)
        self.assertEqual(d["word_timings"][0]["text"], "Hello")

    def test_request_serialization(self) -> None:
        """Verify SubtitleRequest serializes pathlib.Path and Enums to safe types."""
        req = SubtitleRequest(
            text="Hello",
            output_path=Path("/tmp/sub.srt"),
            output_dir=Path("/tmp"),
            timing_mode=TimingMode.ESTIMATED_FROM_TEXT,
            output_format=SubtitleFormat.SRT,
        )
        d = req.to_dict()
        self.assertEqual(d["output_path"], "/tmp/sub.srt")
        self.assertEqual(d["output_dir"], "/tmp")
        self.assertEqual(d["timing_mode"], "estimated_from_text")
        self.assertEqual(d["output_format"], "srt")

    def test_generation_result_serialization(self) -> None:
        """Verify full hierarchy serialization of SubtitleGenerationResult."""
        report = SubtitleValidationReport(errors=[], warnings=["Small gap detected"])
        cue = SubtitleCue("cue_1", 1, 0.0, 2.0, "Hello World", ["Hello", "World"])
        result = SubtitleGenerationResult(
            task_id="task_abc",
            status=TaskStatus.COMPLETED,
            subtitle_path=Path("/tmp/sub.srt"),
            subtitle_format=SubtitleFormat.SRT,
            timeline=[cue],
            cue_count=1,
            total_duration_seconds=2.0,
            timing_mode_used=TimingMode.ESTIMATED_FROM_TEXT,
            estimated_timing=True,
            karaoke_enabled=False,
            validation_report=report,
            warnings=["Warn"],
            generation_duration_seconds=0.15,
        )
        d = result.to_dict()
        self.assertEqual(d["task_id"], "task_abc")
        self.assertEqual(d["status"], "completed")
        self.assertEqual(d["subtitle_path"], "/tmp/sub.srt")
        self.assertEqual(d["timeline"][0]["text"], "Hello World")
        self.assertEqual(d["validation_report"]["warnings"], ["Small gap detected"])
        self.assertEqual(d["validation_report"]["is_valid"], True)


if __name__ == "__main__":
    unittest.main()
