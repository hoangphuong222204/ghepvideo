"""Strongly typed domain and operational models for Module 10: FFmpeg Render Engine.

This module provides all Enums and Dataclasses representing execution status,
media types, input formats, video/audio configurations, render settings, requests,
execution plans, progress telemetry, and rendering results.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.renderer.exceptions import InvalidRenderRequestError, UnsupportedMediaFormatError, InvalidRenderPlanError


class RenderTaskStatus(str, Enum):
    """Execution status for render tasks."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MediaType(str, Enum):
    """Classification of media files."""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    SUBTITLE = "subtitle"


class VideoCodec(str, Enum):
    """Supported video codecs and encoders."""
    H264 = "h264"
    HEVC = "hevc"
    VP9 = "vp9"
    AV1 = "av1"
    COPY = "copy"


class AudioCodec(str, Enum):
    """Supported audio codecs and encoders."""
    AAC = "aac"
    MP3 = "mp3"
    OPUS = "opus"
    AC3 = "ac3"
    COPY = "copy"


class ContainerFormat(str, Enum):
    """Supported media container formats."""
    MP4 = "mp4"
    MKV = "mkv"
    MOV = "mov"
    WEBM = "webm"
    WAV = "wav"


class PixelFormat(str, Enum):
    """Supported color spaces and pixel formats."""
    YUV420P = "yuv420p"
    YUV420P10LE = "yuv420p10le"
    NV12 = "nv12"


class HardwareAccelerationType(str, Enum):
    """Supported hardware acceleration types."""
    NONE = "none"
    NVENC = "nvenc"
    QSV = "qsv"
    AMF = "amf"
    VIDEOTOOLBOX = "videotoolbox"


class EncoderPreference(str, Enum):
    """Target preference for selecting encoders."""
    CPU = "cpu"
    GPU = "gpu"
    AUTO = "auto"


class AspectRatioPreset(str, Enum):
    """Pre-configured target aspect ratios."""
    LANDSCAPE_16_9 = "16:9"
    VERTICAL_9_16 = "9:16"
    SQUARE_1_1 = "1:1"
    PORTRAIT_4_5 = "4:5"


class ResolutionPreset(str, Enum):
    """Pre-configured target frame dimensions."""
    FHD_1080P = "1920x1080"
    HD_720P = "1280x720"
    VERTICAL_1080P = "1080x1920"
    VERTICAL_720P = "720x1280"
    SQUARE_1080 = "1080x1080"


class ScalingMode(str, Enum):
    """Handling strategy for resolving source-destination aspect ratio mismatches."""
    STRETCH = "stretch"
    PAD = "pad"
    CROP = "crop"


class ImageFitMode(str, Enum):
    """Sizing behavior for static image inputs."""
    CONTAIN = "contain"
    COVER = "cover"
    FILL = "fill"


class AudioMixMode(str, Enum):
    """Mixing strategy for combining concurrent audio tracks."""
    SEQUENCE = "sequence"
    MIX = "mix"
    REPLACE = "replace"


class SubtitleRenderMode(str, Enum):
    """Burning or packaging options for subtitle overlay."""
    BURN_IN = "burn_in"
    SOFT_SUB = "soft_sub"
    NONE = "none"


class OverlayPosition(str, Enum):
    """Visual anchor positions for watermark and logo overlays."""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    CUSTOM = "custom"


class TransitionType(str, Enum):
    """Types of visual transitions between sequential timeline tracks."""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    NONE = "none"


class RenderPriority(int, Enum):
    """Priority level for queued rendering tasks."""
    LOW = 10
    MEDIUM = 20
    HIGH = 30


class RenderStage(str, Enum):
    """Discrete milestones inside the rendering process."""
    INIT = "initializing"
    PROBING = "probing_inputs"
    PLANNING = "building_render_plan"
    PROCESSING = "processing_filters"
    ENCODING = "encoding_video"
    VALIDATING = "validating_output"
    COMPLETED = "completed"


# Media Stream Probing Models
@dataclass(frozen=True)
class VideoStreamMetadata:
    """Probed metadata describing a specific video stream.

    Attributes:
        codec: Decoder name.
        width: Width in pixels.
        height: Height in pixels.
        r_frame_rate: Frame rate as a fraction string (e.g., '30000/1001').
        duration_seconds: True playback length.
        bit_rate: Stream transfer rate in bits/second.
        pixel_format: Pixel mapping layout name (e.g. 'yuv420p').
    """
    codec: str
    width: int
    height: int
    r_frame_rate: str
    duration_seconds: float
    bit_rate: Optional[int] = None
    pixel_format: Optional[str] = None


@dataclass(frozen=True)
class AudioStreamMetadata:
    """Probed metadata describing a specific audio stream.

    Attributes:
        codec: Decoder name.
        sample_rate: Frequency in Hz.
        channels: Channel layout count.
        duration_seconds: True playback length.
        bit_rate: Stream transfer rate in bits/second.
    """
    codec: str
    sample_rate: int
    channels: int
    duration_seconds: float
    bit_rate: Optional[int] = None


@dataclass(frozen=True)
class SubtitleStreamMetadata:
    """Probed metadata describing a specific subtitle stream embedded in a container.

    Attributes:
        codec: Decoder name.
        language: ISO-639 language code if present.
    """
    codec: str
    language: Optional[str] = None


@dataclass(frozen=True)
class MediaMetadata:
    """Complete diagnostic properties of a media asset parsed by FFprobe.

    Attributes:
        path: Path to the scanned file.
        media_type: Detected primary type of asset.
        duration_seconds: Aggregate file length.
        file_size_bytes: True file size on disk.
        video_streams: Found video tracks.
        audio_streams: Found audio tracks.
        subtitle_streams: Found subtitle tracks.
    """
    path: Path
    media_type: MediaType
    duration_seconds: float
    file_size_bytes: int
    video_streams: List[VideoStreamMetadata] = field(default_factory=list)
    audio_streams: List[AudioStreamMetadata] = field(default_factory=list)
    subtitle_streams: List[SubtitleStreamMetadata] = field(default_factory=list)


# Input Layout Models
@dataclass(frozen=True)
class ImageInput:
    """Settings required to parse static images into timed video chunks.

    Attributes:
        path: Source file path.
        duration_seconds: Screen time length.
        fit_mode: Canvas scale/fill adaptation model.
    """
    path: Path
    duration_seconds: float
    fit_mode: ImageFitMode = ImageFitMode.COVER

    def __post_init__(self) -> None:
        if self.duration_seconds <= 0:
            raise InvalidRenderRequestError("ImageInput duration_seconds must be positive.")


@dataclass(frozen=True)
class VideoInput:
    """Target settings for processing a video clip.

    Attributes:
        path: Source file path.
        start_offset: Start trimming offset in seconds.
        duration_seconds: Dynamic cut length. If None, reads to end of clip.
        volume: Volume multiplier coefficient for its audio track.
    """
    path: Path
    start_offset: float = 0.0
    duration_seconds: Optional[float] = None
    volume: float = 1.0

    def __post_init__(self) -> None:
        if self.start_offset < 0:
            raise InvalidRenderRequestError("VideoInput start_offset must be non-negative.")
        if self.duration_seconds is not None and self.duration_seconds <= 0:
            raise InvalidRenderRequestError("VideoInput duration_seconds must be positive.")
        if self.volume < 0:
            raise InvalidRenderRequestError("VideoInput volume coefficient cannot be negative.")


@dataclass(frozen=True)
class AudioInput:
    """General target settings for processing an audio track.

    Attributes:
        path: Source file path.
        start_offset: Trim start offset in seconds.
        duration_seconds: Dynamic playback length. If None, reads to end of file.
        volume: Baseline volume multiplier coefficient.
    """
    path: Path
    start_offset: float = 0.0
    duration_seconds: Optional[float] = None
    volume: float = 1.0

    def __post_init__(self) -> None:
        if self.start_offset < 0:
            raise InvalidRenderRequestError("AudioInput start_offset must be non-negative.")
        if self.duration_seconds is not None and self.duration_seconds <= 0:
            raise InvalidRenderRequestError("AudioInput duration_seconds must be positive.")
        if self.volume < 0:
            raise InvalidRenderRequestError("AudioInput volume coefficient cannot be negative.")


@dataclass(frozen=True)
class BackgroundMusicInput:
    """Background soundtrack mixing configurations.

    Attributes:
        path: Soundtrack source file path.
        volume: Baseline soundtrack volume coefficient (typically low).
        loop: Loop music track continuously to fit output timeline duration.
        ducking_enabled: Enable smart voice-over relative audio ducking.
        ducking_level: Target volume ratio during vocal occurrences.
    """
    path: Path
    volume: float = 0.2
    loop: bool = True
    ducking_enabled: bool = True
    ducking_level: float = 0.1

    def __post_init__(self) -> None:
        if self.volume < 0:
            raise InvalidRenderRequestError("BackgroundMusicInput volume coefficient cannot be negative.")
        if self.ducking_level < 0:
            raise InvalidRenderRequestError("BackgroundMusicInput ducking_level coefficient cannot be negative.")


@dataclass(frozen=True)
class SubtitleInput:
    """Parameters directing subtitle rendering and burn-in overlays.

    Attributes:
        path: Source subtitles file path (SRT or ASS).
        render_mode: Overlay mode (e.g., Burn-in, Soft, None).
        font_name: Override system font family path.
        font_size: Override font scale size in points.
        primary_color: ASS hexadecimal color override (e.g., '&H00FFFFFF').
    """
    path: Path
    render_mode: SubtitleRenderMode = SubtitleRenderMode.BURN_IN
    font_name: Optional[str] = None
    font_size: Optional[int] = None
    primary_color: Optional[str] = None

    def __post_init__(self) -> None:
        if self.font_size is not None and self.font_size <= 0:
            raise InvalidRenderRequestError("SubtitleInput font_size override must be positive.")


@dataclass(frozen=True)
class LogoInput:
    """Visual configurations for static logo overlay watermark.

    Attributes:
        path: Transparent logo PNG/JPG path.
        position: Anchor corner mapping.
        x_offset: Horizontal margin pixels.
        y_offset: Vertical margin pixels.
        scale: Resize multiplier relative to video height (e.g., 0.15 is 15%).
        opacity: Layer blend transparency (0.0 to 1.0).
        start_time: Timeline onset moment in seconds.
        end_time: Timeline termination moment in seconds. None displays to end.
    """
    path: Path
    position: OverlayPosition = OverlayPosition.TOP_RIGHT
    x_offset: int = 20
    y_offset: int = 20
    scale: float = 0.15
    opacity: float = 0.8
    start_time: float = 0.0
    end_time: Optional[float] = None

    def __post_init__(self) -> None:
        if self.x_offset < 0 or self.y_offset < 0:
            raise InvalidRenderRequestError("Logo offsets must be non-negative.")
        if not (0.0 <= self.scale <= 1.0):
            raise InvalidRenderRequestError("Logo scale must fall between 0.0 and 1.0.")
        if not (0.0 <= self.opacity <= 1.0):
            raise InvalidRenderRequestError("Logo opacity must fall between 0.0 and 1.0.")
        if self.start_time < 0:
            raise InvalidRenderRequestError("Logo start_time must be non-negative.")
        if self.end_time is not None and self.end_time <= self.start_time:
            raise InvalidRenderRequestError("Logo end_time must be strictly after start_time.")


@dataclass(frozen=True)
class WatermarkInput:
    """Visual configurations for a central, translucent watermark overlay.

    Attributes:
        path: Image overlay path.
        position: Overlay anchor alignment.
        scale: Scale multiplier relative to target height.
        opacity: Layer transparency factor (0.0 to 1.0).
    """
    path: Path
    position: OverlayPosition = OverlayPosition.CENTER
    scale: float = 1.0
    opacity: float = 0.2

    def __post_init__(self) -> None:
        if not (0.0 <= self.scale <= 5.0):
            raise InvalidRenderRequestError("Watermark scale multiplier must fall within 0.0 and 5.0.")
        if not (0.0 <= self.opacity <= 1.0):
            raise InvalidRenderRequestError("Watermark opacity must fall between 0.0 and 1.0.")


# Settings Groups
@dataclass(frozen=True)
class OverlaySettings:
    """Aggregated brand and layout overlays settings.

    Attributes:
        logo: Corner brand logo overlay.
        watermark: Full-screen translucent watermark overlay.
    """
    logo: Optional[LogoInput] = None
    watermark: Optional[WatermarkInput] = None


@dataclass(frozen=True)
class AudioSettings:
    """Aggregate soundtrack mixing settings.

    Attributes:
        voice_over: Principal commentary or narration voice asset.
        background_music: Background soundtrack parameters.
        original_audio_volume: Multiplier for original video clips' sound.
        mix_mode: Layout arrangement for overlaying or sequencing.
        normalize_loudness: Apply targeted volume normalization policies.
        sample_rate: Mixdown resampling output frequency.
    """
    voice_over: Optional[AudioInput] = None
    background_music: Optional[BackgroundMusicInput] = None
    original_audio_volume: float = 1.0
    mix_mode: AudioMixMode = AudioMixMode.MIX
    normalize_loudness: bool = True
    sample_rate: int = 44100

    def __post_init__(self) -> None:
        if self.original_audio_volume < 0:
            raise InvalidRenderRequestError("original_audio_volume must be non-negative.")
        if self.sample_rate not in (22050, 24000, 44100, 48000):
            raise UnsupportedMediaFormatError(
                f"Unsupported audio sample rate: {self.sample_rate}. Supported: 22050, 24000, 44100, 48000"
            )


@dataclass(frozen=True)
class VideoSettings:
    """Aggregate target encoding and packaging parameters.

    Attributes:
        aspect_ratio: Target aspect ratio layout preset.
        resolution: Target frame scaling dimension.
        frame_rate: Frame rate count per second.
        codec: Compression video codec output target.
        pixel_format: Target color workspace encoding profile.
        scaling_mode: Cropping, padding, or stretching handling strategy.
        hardware_acceleration: Intended GPU hardware encoders acceleration scheme.
    """
    aspect_ratio: AspectRatioPreset = AspectRatioPreset.VERTICAL_9_16
    resolution: ResolutionPreset = ResolutionPreset.VERTICAL_1080P
    frame_rate: int = 30
    codec: VideoCodec = VideoCodec.H264
    pixel_format: PixelFormat = PixelFormat.YUV420P
    scaling_mode: ScalingMode = ScalingMode.PAD
    hardware_acceleration: HardwareAccelerationType = HardwareAccelerationType.NONE

    def __post_init__(self) -> None:
        if self.frame_rate <= 0:
            raise InvalidRenderRequestError("Target frame_rate must be strictly positive.")


@dataclass(frozen=True)
class OutputSettings:
    """Target folder and container write settings.

    Attributes:
        output_path: Final target destination path on physical disk.
        overwrite: Overwrite preexisting files safely.
        container_format: Output extension type format.
    """
    output_path: Path
    overwrite: bool = True
    container_format: ContainerFormat = ContainerFormat.MP4


@dataclass(frozen=True)
class RenderSettings:
    """Consolidated orchestration package configuring every stream dimension.

    Attributes:
        video: Configurations of target video canvas and codec properties.
        audio: Narrative and soundtrack blending properties.
        overlay: Watermarking brand settings.
        priority: Process priority in queue scheduling.
        timeout_seconds: Subprocess process termination timeout.
    """
    video: VideoSettings = field(default_factory=VideoSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    overlay: OverlaySettings = field(default_factory=OverlaySettings)
    priority: RenderPriority = RenderPriority.MEDIUM
    timeout_seconds: float = 300.0

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise InvalidRenderRequestError("timeout_seconds must be positive.")


# Orchestration Payload Models
@dataclass(frozen=True)
class RenderRequest:
    """Standard, strongly typed request payload for executing a single render.

    Attributes:
        task_id: Unique identifier tracking this task lifecycle.
        video_inputs: Collection of sequential video source clips.
        image_inputs: Collection of sequential static slides.
        output: target output location write parameters.
        subtitle_input: Optional subtitles timeline burn-in settings.
        settings: Render processing configuration parameters.
    """
    task_id: str
    video_inputs: List[VideoInput] = field(default_factory=list)
    image_inputs: List[ImageInput] = field(default_factory=list)
    output: OutputSettings = field(default_factory=lambda: OutputSettings(Path("./exports/video/output.mp4")))
    subtitle_input: Optional[SubtitleInput] = None
    settings: RenderSettings = field(default_factory=RenderSettings)

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise InvalidRenderRequestError("task_id cannot be empty.")
        if not self.video_inputs and not self.image_inputs:
            raise InvalidRenderRequestError("RenderRequest must provide at least one image or video input.")


@dataclass(frozen=True)
class RenderPlan:
    """The resolved execution layout representing exactly how to render.

    Attributes:
        task_id: Active task tracking identifier.
        ordered_inputs: Full resolved list of media file sources.
        duration_seconds: Predicted final duration of output.
        encoder_to_use: Specific FFmpeg codec identifier (e.g. 'h264_nvenc').
        stages: Full mapped listing of active render phases.
        estimated_size_bytes: Approximated target file footprint.
    """
    task_id: str
    ordered_inputs: List[Path]
    duration_seconds: float
    encoder_to_use: str
    stages: List[RenderStage]
    estimated_size_bytes: int

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise InvalidRenderPlanError("task_id inside RenderPlan cannot be empty.")
        if self.duration_seconds <= 0:
            raise InvalidRenderRequestError("RenderPlan expected output duration must be positive.")


# Operational Progress Tracking Models
@dataclass(frozen=True)
class RenderProgress:
    """Realtime rendering telemetry updates emitted during FFmpeg compilation.

    Attributes:
        task_id: Unique task identifier.
        stage: Current rendering phase.
        percentage: Percent progress clamped between 0.0 and 100.0.
        processed_duration: Cumulative duration rendered in seconds.
        total_duration: Target output duration in seconds.
        current_frame: Count of frame loops compiled.
        current_speed: Multiplier tracking real-time rendering velocity (e.g., 2.5x).
        current_bitrate: Immediate stream write speed in kbits/s.
        status_message: Accompanying verbose informational string.
        timestamp: Time tracking timestamp.
    """
    task_id: str
    stage: RenderStage
    percentage: float
    processed_duration: float
    total_duration: float
    current_frame: int = 0
    current_speed: float = 0.0
    current_bitrate: float = 0.0
    status_message: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        # Clamp progress percent strictly between 0 and 100
        object.__setattr__(self, "percentage", max(0.0, min(100.0, self.percentage)))


@dataclass(frozen=True)
class RenderWarning:
    """System-level warning encountered during timeline composition or render encoding."""
    code: str
    message: str


# Compilation Return Result Models
@dataclass(frozen=True)
class RenderResult:
    """Structural response documenting the output details of a rendering task.

    Attributes:
        task_id: Unique task tracking identifier.
        status: Core result outcome status.
        output_path: Path location of the generated asset file.
        container: File container extension (e.g. 'mp4').
        video_codec: Concrete video compressor encoder used.
        audio_codec: Concrete audio compressor encoder used.
        resolution: Text dimensions string (e.g., '1080x1920').
        frame_rate: Frame count per second compiled.
        duration_seconds: Playback length of compiled file.
        file_size_bytes: Size of compiled asset written on disk.
        encoder_used: Name of the FFmpeg encoder executable driver.
        hardware_acceleration_used: Acceleration model applied.
        render_time_seconds: Processing runtime cost duration.
        average_render_speed: Aggregated process speed multiplier.
        warnings: Captured non-fatal pipeline anomalies.
        error_message: Error diagnostics trace on crash or failures.
    """
    task_id: str
    status: RenderTaskStatus
    output_path: Optional[Path] = None
    container: str = ""
    video_codec: str = ""
    audio_codec: str = ""
    resolution: str = ""
    frame_rate: float = 0.0
    duration_seconds: float = 0.0
    file_size_bytes: int = 0
    encoder_used: str = ""
    hardware_acceleration_used: str = ""
    render_time_seconds: float = 0.0
    average_render_speed: float = 0.0
    warnings: List[RenderWarning] = field(default_factory=list)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Provides a dictionary mapping of outputs safe for JSON serializers."""
        data = asdict(self)
        if data["output_path"]:
            data["output_path"] = str(data["output_path"])
        data["status"] = data["status"].value
        return data


@dataclass(frozen=True)
class BatchRenderRequest:
    """Consolidated submission package for multiple sequential rendering operations."""
    batch_id: str
    requests: List[RenderRequest]

    def __post_init__(self) -> None:
        if not self.batch_id.strip():
            raise InvalidRenderRequestError("BatchRenderRequest batch_id cannot be empty.")
        if not self.requests:
            raise InvalidRenderRequestError("BatchRenderRequest requests sequence cannot be empty.")


@dataclass(frozen=True)
class BatchRenderResult:
    """Outcome report describing overall execution properties of a rendering batch."""
    batch_id: str
    overall_status: RenderTaskStatus
    results: List[RenderResult]
    success_count: int
    failure_count: int
    cancelled_count: int
    total_render_time: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch results payload into serializable map structure."""
        return {
            "batch_id": self.batch_id,
            "overall_status": self.overall_status.value,
            "results": [r.to_dict() for r in self.results],
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "cancelled_count": self.cancelled_count,
            "total_render_time": self.total_render_time,
        }


# System Capabilities & Health Models
@dataclass(frozen=True)
class RendererHealthStatus:
    """Structural diagnostic integrity check on local environment.

    Attributes:
        is_healthy: Cumulative readiness status of binaries.
        status_message: Detailed message reporting path checks and versions.
        last_checked_at: Precise checking timestamp.
    """
    is_healthy: bool
    status_message: str
    last_checked_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class FFmpegCapabilityInformation:
    """Supported encoders, decoders, and custom hardware accelerators detected.

    Attributes:
        version: Full FFmpeg build version string.
        available_encoders: System supported encoder strings sequence.
        available_decoders: System supported decoder strings sequence.
        available_filters: System supported filter graph filter names.
        hwaccel_methods: Accelerated API drivers available.
    """
    version: str
    available_encoders: List[str]
    available_decoders: List[str]
    available_filters: List[str]
    hwaccel_methods: List[str]


@dataclass(frozen=True)
class EncoderCapabilityInformation:
    """Individual encoder parameters probed for safety.

    Attributes:
        encoder_name: Name identifier of the encoder.
        is_hardware_accelerated: Runs using graphics cards processor resources.
        supported_pixel_formats: Valid pixel mappings supported.
    """
    encoder_name: str
    is_hardware_accelerated: bool
    supported_pixel_formats: List[str]


@dataclass(frozen=True)
class RenderValidationReport:
    """Report detailing the validation outcome of a RenderRequest or RenderResult output.

    Attributes:
        is_valid: Cumulative correctness status of the validation.
        errors: List of fatal validation error messages.
        warnings: List of non-fatal validation warning messages.
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

