"""Comprehensive Unit Tests for Module 08 TTS Foundations.

This module validates the exception hierarchy, model validation, serialization paths,
enum stability, and clean public imports for the Text-to-Speech system.
"""

import json
import unittest
from datetime import datetime
from pathlib import Path

# Verify public imports from the root package
from src.tts import (
    AudioChannelMode,
    AudioFormat,
    BatchGenerationResult,
    BatchTTSRequest,
    CacheInfo,
    DeviceType,
    FileOutputError,
    GenerationCancelledError,
    GenerationError,
    GenerationPriority,
    GenerationProgress,
    GenerationResult,
    GPUOutOfMemoryError,
    HealthStatus,
    InvalidGeneratedAudioError,
    InvalidRequestError,
    InvalidTextError,
    InvalidVoiceError,
    ModelLoadError,
    ModelNotLoadedError,
    ModelStatus,
    QueueError,
    QueueTaskInfo,
    ReferenceAudioError,
    ReferenceVoiceInfo,
    TaskStatus,
    TTSCache,
    TTSConfigError,
    TTSEngineError,
    TTSGenerationSettings,
    TTSModelRunner,
    TTSPostProcessingSettings,
    TTSQueue,
    TTSRequest,
    UnsupportedAudioFormatError,
    UnsupportedDeviceError,
    VoiceCloningError,
    VoiceMetadata,
    VoiceRegistry,
    VoiceType,
)


class TestPublicImports(unittest.TestCase):
    """Verifies that the public API exposed under `src.tts` is correct and available."""

    def test_all_imports_available(self):
        # We verify that standard symbols can be referenced and are not None
        self.assertIsNotNone(TTSEngineError)
        self.assertIsNotNone(TTSRequest)
        self.assertIsNotNone(TTSModelRunner)
        self.assertIsNotNone(DeviceType)


class TestExceptionHierarchy(unittest.TestCase):
    """Verifies that the exception hierarchy is structured correctly."""

    def test_base_class(self):
        # All exceptions must inherit from TTSEngineError
        self.assertTrue(issubclass(TTSEngineError, Exception))
        self.assertTrue(issubclass(TTSConfigError, TTSEngineError))
        self.assertTrue(issubclass(UnsupportedDeviceError, TTSConfigError))
        self.assertTrue(issubclass(GPUOutOfMemoryError, TTSEngineError))
        self.assertTrue(issubclass(ModelLoadError, TTSEngineError))
        self.assertTrue(issubclass(ModelNotLoadedError, TTSEngineError))
        self.assertTrue(issubclass(InvalidRequestError, TTSEngineError))
        self.assertTrue(issubclass(InvalidTextError, InvalidRequestError))
        self.assertTrue(issubclass(InvalidVoiceError, InvalidRequestError))
        self.assertTrue(issubclass(ReferenceAudioError, TTSEngineError))
        self.assertTrue(issubclass(VoiceCloningError, TTSEngineError))
        self.assertTrue(issubclass(GenerationError, TTSEngineError))
        self.assertTrue(issubclass(GenerationCancelledError, GenerationError))
        self.assertTrue(issubclass(QueueError, TTSEngineError))
        self.assertTrue(issubclass(FileOutputError, TTSEngineError))

    def test_polymorphic_catch(self):
        # Raising a specific error should be catchable by TTSEngineError
        try:
            raise UnsupportedDeviceError("CUDA not supported")
        except TTSEngineError as err:
            self.assertEqual(str(err), "CUDA not supported")


class TestEnumStability(unittest.TestCase):
    """Verifies that core enums remain stable and map to proper raw values."""

    def test_device_type(self):
        self.assertEqual(DeviceType.CPU.value, "cpu")
        self.assertEqual(DeviceType.CUDA.value, "cuda")
        self.assertEqual(DeviceType.AUTO.value, "auto")

    def test_task_status(self):
        self.assertEqual(TaskStatus.PENDING.value, "pending")
        self.assertEqual(TaskStatus.RUNNING.value, "running")
        self.assertEqual(TaskStatus.COMPLETED.value, "completed")
        self.assertEqual(TaskStatus.FAILED.value, "failed")
        self.assertEqual(TaskStatus.CANCELLED.value, "cancelled")

    def test_voice_type(self):
        self.assertEqual(VoiceType.PRESET.value, "preset")
        self.assertEqual(VoiceType.CLONED.value, "cloned")
        self.assertEqual(VoiceType.CUSTOM.value, "custom")

    def test_audio_channel_mode(self):
        self.assertEqual(AudioChannelMode.MONO.value, "mono")
        self.assertEqual(AudioChannelMode.STEREO.value, "stereo")

    def test_audio_format(self):
        self.assertEqual(AudioFormat.WAV.value, "wav")

    def test_generation_priority(self):
        self.assertEqual(GenerationPriority.LOW.value, 10)
        self.assertEqual(GenerationPriority.MEDIUM.value, 20)
        self.assertEqual(GenerationPriority.HIGH.value, 30)


class TestModelValidation(unittest.TestCase):
    """Verifies dataclass input validation constraints and constructor exceptions."""

    def test_reference_voice_info_validation(self):
        # Empty voice_id
        with self.assertRaises(InvalidRequestError):
            ReferenceVoiceInfo(voice_id="", audio_path=Path("ref.wav"))
        with self.assertRaises(InvalidRequestError):
            ReferenceVoiceInfo(voice_id="  ", audio_path=Path("ref.wav"))

    def test_tts_post_processing_settings_validation(self):
        # Negative fade_in
        with self.assertRaises(InvalidRequestError):
            TTSPostProcessingSettings(fade_in_ms=-1.0)
        # Negative fade_out
        with self.assertRaises(InvalidRequestError):
            TTSPostProcessingSettings(fade_out_ms=-5.0)
        # Negative volume multiplier
        with self.assertRaises(InvalidRequestError):
            TTSPostProcessingSettings(volume_adjustment=-0.1)

    def test_tts_generation_settings_validation(self):
        # Invalid speaking speed (<= 0)
        with self.assertRaises(InvalidRequestError):
            TTSGenerationSettings(speaking_speed=0.0)
        with self.assertRaises(InvalidRequestError):
            TTSGenerationSettings(speaking_speed=-1.5)

        # Invalid pitch (<= 0)
        with self.assertRaises(InvalidRequestError):
            TTSGenerationSettings(pitch=0.0)
        with self.assertRaises(InvalidRequestError):
            TTSGenerationSettings(pitch=-0.2)

        # Invalid volume (< 0)
        with self.assertRaises(InvalidRequestError):
            TTSGenerationSettings(volume=-0.5)

        # Unsupported sample rate
        with self.assertRaises(UnsupportedAudioFormatError):
            TTSGenerationSettings(sample_rate=16000)

        # Invalid timeout (<= 0)
        with self.assertRaises(InvalidRequestError):
            TTSGenerationSettings(timeout_seconds=0)

    def test_tts_request_validation(self):
        # Empty text
        with self.assertRaises(InvalidRequestError):
            TTSRequest(text="", voice_id="viet_voice")
        with self.assertRaises(InvalidRequestError):
            TTSRequest(text="   ", voice_id="viet_voice")

        # Empty voice_id
        with self.assertRaises(InvalidRequestError):
            TTSRequest(text="Xin chào", voice_id="")

    def test_batch_tts_request_validation(self):
        req = TTSRequest(text="Xin chào", voice_id="viet_voice")
        # Empty requests list
        with self.assertRaises(InvalidRequestError):
            BatchTTSRequest(requests=[], batch_id="batch_001")
        # Empty batch_id
        with self.assertRaises(InvalidRequestError):
            BatchTTSRequest(requests=[req], batch_id="  ")

    def test_voice_metadata_validation(self):
        # Empty voice_id
        with self.assertRaises(InvalidRequestError):
            VoiceMetadata(voice_id="", display_name="Nam", voice_type=VoiceType.PRESET, language="vi")
        # Empty display name
        with self.assertRaises(InvalidRequestError):
            VoiceMetadata(voice_id="nam_01", display_name="  ", voice_type=VoiceType.PRESET, language="vi")


class TestSerialization(unittest.TestCase):
    """Verifies that data models serialize to dict and JSON cleanly without raising exceptions."""

    def test_generation_result_serialization(self):
        res = GenerationResult(
            task_id="task_123",
            status=TaskStatus.COMPLETED,
            audio_path=Path("/tmp/output.wav"),
            duration_seconds=3.5,
            generation_time_seconds=0.45,
            cache_hit=False,
            voice_id="premium_vi",
            device_used="cuda:0",
            sample_rate=44100,
            channels=AudioChannelMode.STEREO,
            file_size_bytes=10240,
            warnings=["Loudness exceeded safe limit"],
        )

        d = res.to_dict()
        self.assertEqual(d["task_id"], "task_123")
        self.assertEqual(d["status"], "completed")
        self.assertEqual(d["audio_path"], "/tmp/output.wav")
        self.assertEqual(d["channels"], "stereo")
        self.assertEqual(d["file_size_bytes"], 10240)
        self.assertIn("Loudness exceeded safe limit", d["warnings"])

        # Test valid JSON dump of serialized result
        json_str = json.dumps(d)
        self.assertIsInstance(json_str, str)

    def test_batch_generation_result_serialization(self):
        res = GenerationResult(
            task_id="task_123",
            status=TaskStatus.COMPLETED,
            audio_path=Path("/tmp/output.wav"),
            duration_seconds=3.5,
            generation_time_seconds=0.45,
            cache_hit=False,
            voice_id="premium_vi",
            device_used="cuda:0",
            sample_rate=44100,
            channels=AudioChannelMode.STEREO,
            file_size_bytes=10240,
        )
        batch_res = BatchGenerationResult(
            batch_id="batch_001",
            overall_status=TaskStatus.COMPLETED,
            results=[res],
            success_count=1,
            failure_count=0,
            cancelled_count=0,
            total_generation_time=0.45,
        )

        d = batch_res.to_dict()
        self.assertEqual(d["batch_id"], "batch_001")
        self.assertEqual(d["overall_status"], "completed")
        self.assertEqual(len(d["results"]), 1)
        self.assertEqual(d["results"][0]["task_id"], "task_123")
        self.assertEqual(d["success_count"], 1)

        # Test valid JSON dump
        json_str = json.dumps(d)
        self.assertIsInstance(json_str, str)
