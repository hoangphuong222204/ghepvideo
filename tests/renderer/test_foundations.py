"""Unit tests for the foundations of Module 10: FFmpeg Render Engine.

This suite validates model initialization, post-init constraints, serialization behavior,
enum stability, exception hierarchy, and package-level public exports.
"""

import json
import unittest
from datetime import datetime
from pathlib import Path

# Import package-level public API to test exports
import src.renderer as renderer


class TestFoundations(unittest.TestCase):
    """Foundational test suite for Module 10 exceptions, models, and protocols."""

    def test_public_imports(self) -> None:
        """Verify all major foundations, exceptions, models, and protocols are exported."""
        # Exceptions
        self.assertTrue(hasattr(renderer, "RenderEngineError"))
        self.assertTrue(hasattr(renderer, "FFmpegNotFoundError"))
        self.assertTrue(hasattr(renderer, "RenderCancelledError"))
        self.assertTrue(hasattr(renderer, "OutputValidationError"))

        # Models
        self.assertTrue(hasattr(renderer, "RenderTaskStatus"))
        self.assertTrue(hasattr(renderer, "VideoCodec"))
        self.assertTrue(hasattr(renderer, "RenderRequest"))
        self.assertTrue(hasattr(renderer, "RenderResult"))
        self.assertTrue(hasattr(renderer, "RenderValidationReport"))

        # Protocols
        self.assertTrue(hasattr(renderer, "RenderEngineProtocol"))
        self.assertTrue(hasattr(renderer, "MediaProbeProtocol"))

    def test_exception_hierarchy(self) -> None:
        """Verify the custom exception class inheritance structure matches design spec."""
        # Core base
        self.assertTrue(issubclass(renderer.RenderEngineError, Exception))

        # Config hierarchy
        self.assertTrue(issubclass(renderer.RenderConfigError, renderer.RenderEngineError))
        self.assertTrue(issubclass(renderer.FFmpegNotFoundError, renderer.RenderConfigError))
        self.assertTrue(issubclass(renderer.FFprobeNotFoundError, renderer.RenderConfigError))
        self.assertTrue(issubclass(renderer.UnsupportedFFmpegVersionError, renderer.RenderConfigError))

        # Capability hierarchy
        self.assertTrue(issubclass(renderer.CapabilityDetectionError, renderer.RenderEngineError))
        self.assertTrue(issubclass(renderer.UnsupportedEncoderError, renderer.CapabilityDetectionError))

        # Input hierarchy
        self.assertTrue(issubclass(renderer.InvalidRenderRequestError, renderer.RenderEngineError))
        self.assertTrue(issubclass(renderer.InvalidMediaInputError, renderer.RenderEngineError))
        self.assertTrue(issubclass(renderer.MissingInputFileError, renderer.InvalidMediaInputError))
        self.assertTrue(issubclass(renderer.CorruptedMediaError, renderer.InvalidMediaInputError))
        self.assertTrue(issubclass(renderer.UnsupportedMediaFormatError, renderer.InvalidMediaInputError))

        # Process/Execution hierarchy
        self.assertTrue(issubclass(renderer.RenderFailureError, renderer.RenderEngineError))
        self.assertTrue(issubclass(renderer.RenderTimeoutError, renderer.RenderFailureError))
        self.assertTrue(issubclass(renderer.RenderCancelledError, renderer.RenderFailureError))
        self.assertTrue(issubclass(renderer.GPUEncoderError, renderer.RenderFailureError))
        self.assertTrue(issubclass(renderer.GPUOutOfMemoryError, renderer.GPUEncoderError))

    def test_enum_stability(self) -> None:
        """Ensure all domain enums are stable and map to expected wire strings/values."""
        self.assertEqual(renderer.RenderTaskStatus.PENDING.value, "pending")
        self.assertEqual(renderer.RenderTaskStatus.RUNNING.value, "running")
        self.assertEqual(renderer.RenderTaskStatus.COMPLETED.value, "completed")
        self.assertEqual(renderer.RenderTaskStatus.FAILED.value, "failed")
        self.assertEqual(renderer.RenderTaskStatus.CANCELLED.value, "cancelled")

        self.assertEqual(renderer.MediaType.VIDEO.value, "video")
        self.assertEqual(renderer.MediaType.AUDIO.value, "audio")
        self.assertEqual(renderer.MediaType.IMAGE.value, "image")
        self.assertEqual(renderer.MediaType.SUBTITLE.value, "subtitle")

        self.assertEqual(renderer.VideoCodec.H264.value, "h264")
        self.assertEqual(renderer.VideoCodec.COPY.value, "copy")

        self.assertEqual(renderer.AudioCodec.AAC.value, "aac")
        self.assertEqual(renderer.AudioCodec.COPY.value, "copy")

        self.assertEqual(renderer.ContainerFormat.MP4.value, "mp4")
        self.assertEqual(renderer.ScalingMode.PAD.value, "pad")
        self.assertEqual(renderer.ImageFitMode.COVER.value, "cover")
        self.assertEqual(renderer.AudioMixMode.MIX.value, "mix")
        self.assertEqual(renderer.SubtitleRenderMode.BURN_IN.value, "burn_in")
        self.assertEqual(renderer.OverlayPosition.TOP_RIGHT.value, "top_right")
        self.assertEqual(renderer.TransitionType.FADE.value, "fade")
        self.assertEqual(renderer.RenderStage.ENCODING.value, "encoding_video")

        # Prioritization values must be correct integers
        self.assertEqual(renderer.RenderPriority.LOW.value, 10)
        self.assertEqual(renderer.RenderPriority.MEDIUM.value, 20)
        self.assertEqual(renderer.RenderPriority.HIGH.value, 30)

    def test_image_input_validation(self) -> None:
        """Verify ImageInput constraints are enforced on initialization."""
        # Valid initialization
        img = renderer.ImageInput(path=Path("/some/image.png"), duration_seconds=5.0)
        self.assertEqual(img.duration_seconds, 5.0)
        self.assertEqual(img.fit_mode, renderer.ImageFitMode.COVER)

        # Invalid duration should raise
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.ImageInput(path=Path("/some/image.png"), duration_seconds=0.0)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.ImageInput(path=Path("/some/image.png"), duration_seconds=-1.5)

    def test_video_input_validation(self) -> None:
        """Verify VideoInput constraints are enforced on initialization."""
        # Valid initialization
        vid = renderer.VideoInput(path=Path("/some/video.mp4"), start_offset=1.5, duration_seconds=10.0, volume=0.8)
        self.assertEqual(vid.start_offset, 1.5)
        self.assertEqual(vid.duration_seconds, 10.0)
        self.assertEqual(vid.volume, 0.8)

        # Invalid offsets/durations/volumes
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.VideoInput(path=Path("/some/video.mp4"), start_offset=-0.1)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.VideoInput(path=Path("/some/video.mp4"), duration_seconds=0.0)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.VideoInput(path=Path("/some/video.mp4"), volume=-0.5)

    def test_audio_input_validation(self) -> None:
        """Verify AudioInput constraints are enforced on initialization."""
        # Valid initialization
        aud = renderer.AudioInput(path=Path("/some/voice.wav"), start_offset=0.0, duration_seconds=3.2, volume=1.2)
        self.assertEqual(aud.volume, 1.2)

        # Invalid constraints
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.AudioInput(path=Path("/some/voice.wav"), start_offset=-1.0)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.AudioInput(path=Path("/some/voice.wav"), duration_seconds=-0.5)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.AudioInput(path=Path("/some/voice.wav"), volume=-0.1)

    def test_bgm_input_validation(self) -> None:
        """Verify BackgroundMusicInput constraints are enforced on initialization."""
        # Valid initialization
        bgm = renderer.BackgroundMusicInput(path=Path("/some/bg.mp3"), volume=0.1, loop=True, ducking_enabled=True, ducking_level=0.05)
        self.assertEqual(bgm.ducking_level, 0.05)

        # Invalid volume/ducking level
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.BackgroundMusicInput(path=Path("/some/bg.mp3"), volume=-0.01)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.BackgroundMusicInput(path=Path("/some/bg.mp3"), ducking_level=-0.1)

    def test_subtitle_input_validation(self) -> None:
        """Verify SubtitleInput constraints are enforced on initialization."""
        sub = renderer.SubtitleInput(path=Path("/some/subs.srt"), font_size=24)
        self.assertEqual(sub.font_size, 24)

        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.SubtitleInput(path=Path("/some/subs.srt"), font_size=0)

    def test_logo_input_validation(self) -> None:
        """Verify LogoInput constraints are enforced on initialization."""
        logo = renderer.LogoInput(path=Path("/some/logo.png"), scale=0.2, opacity=0.9, start_time=2.0, end_time=5.0)
        self.assertEqual(logo.scale, 0.2)

        # Negative offset
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.LogoInput(path=Path("/some/logo.png"), x_offset=-10)

        # Invalid scale/opacity boundaries
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.LogoInput(path=Path("/some/logo.png"), scale=1.1)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.LogoInput(path=Path("/some/logo.png"), opacity=-0.1)

        # Start/End timing consistency
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.LogoInput(path=Path("/some/logo.png"), start_time=-1.0)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.LogoInput(path=Path("/some/logo.png"), start_time=5.0, end_time=4.0)

    def test_watermark_input_validation(self) -> None:
        """Verify WatermarkInput constraints are enforced on initialization."""
        watermark = renderer.WatermarkInput(path=Path("/some/wm.png"), scale=2.5, opacity=0.15)
        self.assertEqual(watermark.scale, 2.5)

        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.WatermarkInput(path=Path("/some/wm.png"), scale=5.1)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.WatermarkInput(path=Path("/some/wm.png"), opacity=1.5)

    def test_audio_settings_sample_rate(self) -> None:
        """Verify AudioSettings only accepts supported sample rates."""
        # Valid
        self.assertEqual(renderer.AudioSettings(sample_rate=44100).sample_rate, 44100)
        self.assertEqual(renderer.AudioSettings(sample_rate=48000).sample_rate, 48000)

        # Invalid
        with self.assertRaises(renderer.UnsupportedMediaFormatError):
            renderer.AudioSettings(sample_rate=16000)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.AudioSettings(original_audio_volume=-0.1)

    def test_video_settings_constraints(self) -> None:
        """Verify VideoSettings rejects invalid frame rates."""
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.VideoSettings(frame_rate=0)
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.VideoSettings(frame_rate=-30)

    def test_render_settings_timeout(self) -> None:
        """Verify RenderSettings enforces positive timeouts."""
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.RenderSettings(timeout_seconds=0.0)

    def test_render_request_consistency(self) -> None:
        """Verify RenderRequest ensures task ID is non-empty and has at least one visual input."""
        # Valid request
        req = renderer.RenderRequest(
            task_id="task-123",
            image_inputs=[renderer.ImageInput(path=Path("/img.jpg"), duration_seconds=4.0)],
        )
        self.assertEqual(req.task_id, "task-123")

        # Empty task_id
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.RenderRequest(task_id="", image_inputs=[renderer.ImageInput(path=Path("/img.jpg"), duration_seconds=4.0)])
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.RenderRequest(task_id="   ", image_inputs=[renderer.ImageInput(path=Path("/img.jpg"), duration_seconds=4.0)])

        # Missing all visual inputs
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.RenderRequest(task_id="task-123", video_inputs=[], image_inputs=[])

    def test_render_plan_validation(self) -> None:
        """Verify RenderPlan constraints."""
        # Valid plan
        plan = renderer.RenderPlan(
            task_id="plan-123",
            ordered_inputs=[Path("/img.jpg")],
            duration_seconds=5.0,
            encoder_to_use="libx264",
            stages=[renderer.RenderStage.INIT],
            estimated_size_bytes=100000,
        )
        self.assertEqual(plan.task_id, "plan-123")

        # Invalid task_id or duration
        with self.assertRaises(renderer.InvalidRenderPlanError):
            renderer.RenderPlan(
                task_id="",
                ordered_inputs=[Path("/img.jpg")],
                duration_seconds=5.0,
                encoder_to_use="libx264",
                stages=[],
                estimated_size_bytes=100000,
            )
        with self.assertRaises(renderer.InvalidRenderRequestError):
            renderer.RenderPlan(
                task_id="plan-123",
                ordered_inputs=[Path("/img.jpg")],
                duration_seconds=-1.0,
                encoder_to_use="libx264",
                stages=[],
                estimated_size_bytes=100000,
            )

    def test_render_progress_clamping(self) -> None:
        """Verify percentage progress is strictly clamped between 0.0 and 100.0."""
        # Underflow percentage
        p1 = renderer.RenderProgress(
            task_id="task-123", stage=renderer.RenderStage.ENCODING, percentage=-15.5, processed_duration=0.0, total_duration=10.0
        )
        self.assertEqual(p1.percentage, 0.0)

        # Overflow percentage
        p2 = renderer.RenderProgress(
            task_id="task-123", stage=renderer.RenderStage.ENCODING, percentage=125.0, processed_duration=10.0, total_duration=10.0
        )
        self.assertEqual(p2.percentage, 100.0)

    def test_render_result_serialization(self) -> None:
        """Verify RenderResult and BatchRenderResult serialization behavior and JSON safety."""
        warn = renderer.RenderWarning(code="W_SAMPLE_RATE_ADJUST", message="Audio sample rate adjusted.")
        res = renderer.RenderResult(
            task_id="task-123",
            status=renderer.RenderTaskStatus.COMPLETED,
            output_path=Path("/exports/video.mp4"),
            container="mp4",
            video_codec="h264",
            audio_codec="aac",
            resolution="1080x1920",
            frame_rate=30.0,
            duration_seconds=15.5,
            file_size_bytes=5000000,
            encoder_used="libx264",
            hardware_acceleration_used="none",
            render_time_seconds=22.4,
            average_render_speed=1.5,
            warnings=[warn],
        )

        d = res.to_dict()
        self.assertEqual(d["task_id"], "task-123")
        self.assertEqual(d["status"], "completed")
        self.assertEqual(d["output_path"], "/exports/video.mp4")
        self.assertEqual(d["warnings"][0]["code"], "W_SAMPLE_RATE_ADJUST")

        # Test JSON serialization of the dict
        json_str = json.dumps(d)
        self.assertTrue(isinstance(json_str, str))

        # Batch Result Serialization
        batch_res = renderer.BatchRenderResult(
            batch_id="batch-999",
            overall_status=renderer.RenderTaskStatus.COMPLETED,
            results=[res],
            success_count=1,
            failure_count=0,
            cancelled_count=0,
            total_render_time=22.4,
        )

        bd = batch_res.to_dict()
        self.assertEqual(bd["batch_id"], "batch-999")
        self.assertEqual(bd["overall_status"], "completed")
        self.assertEqual(len(bd["results"]), 1)
        self.assertEqual(bd["results"][0]["task_id"], "task-123")

        # Test JSON serialization of the batch dict
        batch_json_str = json.dumps(bd)
        self.assertTrue(isinstance(batch_json_str, str))


if __name__ == "__main__":
    unittest.main()
