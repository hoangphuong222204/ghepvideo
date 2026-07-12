"""Strongly typed domain models for Module 08: Fish Speech Engine.

This module provides all Enums and Dataclasses representing device configuration,
task status, request parameters, metadata, generation progress, results, queue tasks,
cache information, and system health status.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from src.tts.exceptions import InvalidRequestError, UnsupportedAudioFormatError


class DeviceType(str, Enum):
    """Supported hardware execution devices."""
    CPU = "cpu"
    CUDA = "cuda"
    AUTO = "auto"


class TaskStatus(str, Enum):
    """Execution status for TTS generation tasks."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VoiceType(str, Enum):
    """Classification of voice profiles."""
    PRESET = "preset"
    CLONED = "cloned"
    CUSTOM = "custom"


class AudioChannelMode(str, Enum):
    """Audio output channel configuration."""
    MONO = "mono"
    STEREO = "stereo"


class AudioFormat(str, Enum):
    """Supported audio container formats."""
    WAV = "wav"


class GenerationPriority(int, Enum):
    """Priority level for queued TTS tasks."""
    LOW = 10
    MEDIUM = 20
    HIGH = 30


@dataclass(frozen=True)
class ReferenceVoiceInfo:
    """Inputs required for reference voice cloning and prompt conditioning.

    Attributes:
        voice_id: Stable identifier of the base custom voice.
        audio_path: Filesystem path to the clean 16-bit reference WAV audio.
        transcript: Text transcript corresponding exactly to the reference audio.
    """
    voice_id: str
    audio_path: Path
    transcript: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.voice_id.strip():
            raise InvalidRequestError("ReferenceVoiceInfo voice_id cannot be empty.")
        if not self.audio_path:
            raise InvalidRequestError("ReferenceVoiceInfo audio_path must be specified.")


@dataclass(frozen=True)
class TTSPostProcessingSettings:
    """Configurable audio post-processing pipelines.

    Attributes:
        normalize_loudness: Whether to apply LUFS-based peak loudness normalization.
        trim_silence: Whether to remove leading and trailing absolute silence.
        fade_in_ms: Duration in milliseconds for a linear volume fade-in.
        fade_out_ms: Duration in milliseconds for a linear volume fade-out.
        volume_adjustment: Linear scale multiplier applied to the final waveform.
    """
    normalize_loudness: bool = True
    trim_silence: bool = True
    fade_in_ms: float = 0.0
    fade_out_ms: float = 0.0
    volume_adjustment: float = 1.0

    def __post_init__(self) -> None:
        if self.fade_in_ms < 0:
            raise InvalidRequestError("fade_in_ms must be non-negative.")
        if self.fade_out_ms < 0:
            raise InvalidRequestError("fade_out_ms must be non-negative.")
        if self.volume_adjustment < 0:
            raise InvalidRequestError("volume_adjustment multiplier must be non-negative.")


@dataclass(frozen=True)
class TTSGenerationSettings:
    """Inference parameters passed directly to the TTS generator.

    Attributes:
        speaking_speed: Speaking rate multiplier (e.g. 1.0 is normal).
        pitch: Fundamental frequency multiplier where supported (default 1.0).
        volume: Baseline volume coefficient (default 1.0).
        emotion: Speaking style or emotional direction label if supported.
        sample_rate: Target sample rate in Hz.
        channel_mode: Target channel layout (Mono or Stereo).
        cache_enabled: Whether to check or store results in the cache.
        priority: Scheduling weight when submitted through the queue.
        timeout_seconds: Hard execution threshold before cancelling.
        post_processing: Chain of audio post-processing steps.
    """
    speaking_speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    emotion: Optional[str] = None
    sample_rate: int = 44100
    channel_mode: AudioChannelMode = AudioChannelMode.MONO
    cache_enabled: bool = True
    priority: GenerationPriority = GenerationPriority.MEDIUM
    timeout_seconds: float = 60.0
    post_processing: TTSPostProcessingSettings = field(default_factory=TTSPostProcessingSettings)

    def __post_init__(self) -> None:
        if self.speaking_speed <= 0:
            raise InvalidRequestError("speaking_speed must be strictly positive.")
        if self.pitch <= 0:
            raise InvalidRequestError("pitch must be strictly positive.")
        if self.volume < 0:
            raise InvalidRequestError("volume coefficient cannot be negative.")
        if self.sample_rate not in (22050, 24000, 44100):
            raise UnsupportedAudioFormatError(
                f"Unsupported sample rate: {self.sample_rate}. Supported: 22050, 24000, 44100."
            )
        if self.timeout_seconds <= 0:
            raise InvalidRequestError("timeout_seconds must be strictly positive.")


@dataclass(frozen=True)
class TTSRequest:
    """A formal request payload for single TTS speech generation.

    Attributes:
        text: The source text script to turn into speech.
        voice_id: Targeted preset or cloned voice identifier.
        settings: Operational settings controlling model execution and post-processing.
        output_directory: Directory where the final output file is generated.
        output_filename: Filename of the target output asset (excluding extensions).
        reference_voice: Optional voice cloning parameters if synthesizing cloned voices.
    """
    text: str
    voice_id: str
    settings: TTSGenerationSettings = field(default_factory=TTSGenerationSettings)
    output_directory: Path = field(default_factory=lambda: Path("./exports/audio"))
    output_filename: Optional[str] = None
    reference_voice: Optional[ReferenceVoiceInfo] = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise InvalidRequestError("Request script text cannot be empty or whitespaces.")
        if not self.voice_id.strip():
            raise InvalidRequestError("Request voice_id cannot be empty.")


@dataclass(frozen=True)
class BatchTTSRequest:
    """A batch collection representing multiple standalone generation items.

    Attributes:
        requests: List of individual request entries.
        batch_id: Unique string tracking the lifecycle of the entire batch.
    """
    requests: List[TTSRequest]
    batch_id: str

    def __post_init__(self) -> None:
        if not self.requests:
            raise InvalidRequestError("BatchTTSRequest must contain at least one TTSRequest.")
        if not self.batch_id.strip():
            raise InvalidRequestError("BatchTTSRequest batch_id cannot be empty.")


@dataclass(frozen=True)
class VoiceMetadata:
    """Detailed structural information cataloging a specific voice asset.

    Attributes:
        voice_id: Unique stable identifier for voice selection.
        display_name: User-facing name of the voice.
        voice_type: Classification (Preset, Cloned, or Custom).
        language: Language spoken primarily by the voice (e.g. 'vi', 'en').
        gender: Optional description of vocal characteristics.
        description: Brief editorial text about the tone or voice context.
        reference_audio_path: Local path to the reference source WAV if cloned.
        reference_transcript: Absolute reference text if required by the model.
        creation_timestamp: Datetime of cloning or voice profile addition.
        availability_status: Current readiness state ('active', 'inactive').
    """
    voice_id: str
    display_name: str
    voice_type: VoiceType
    language: str
    gender: Optional[str] = None
    description: Optional[str] = None
    reference_audio_path: Optional[Path] = None
    reference_transcript: Optional[str] = None
    creation_timestamp: datetime = field(default_factory=datetime.utcnow)
    availability_status: str = "active"

    def __post_init__(self) -> None:
        if not self.voice_id.strip():
            raise InvalidRequestError("VoiceMetadata voice_id cannot be empty.")
        if not self.display_name.strip():
            raise InvalidRequestError("VoiceMetadata display_name cannot be empty.")


@dataclass(frozen=True)
class GenerationProgress:
    """Snapshot tracking safe progress details for execution monitoring.

    Attributes:
        task_id: Active task tracking identifier.
        status: Current state of the pipeline stage.
        progress_percent: Execution progress mapped from 0.0 to 100.0.
        message: Descriptive string outlining current activity.
        current_chunk: Index of the text segment currently running.
        total_chunks: Count of all split segments inside the prompt payload.
    """
    task_id: str
    status: TaskStatus
    progress_percent: float = 0.0
    message: str = ""
    current_chunk: int = 0
    total_chunks: int = 0


@dataclass(frozen=True)
class GenerationResult:
    """Immutable data record returning complete generated audio details.

    Attributes:
        task_id: Identifier of the processed generation task.
        status: Result status indicating success, failure, or cancellation.
        audio_path: Safe filesystem path to the compiled WAV asset.
        duration_seconds: True playback duration of the output audio file.
        generation_time_seconds: Compute execution latency in seconds.
        cache_hit: True if loaded from local caching, False if fully generated.
        voice_id: Voice profile utilized for this execution.
        device_used: CPU, CUDA or hardware mapping that handled the model.
        sample_rate: Actual sample rate of the generated audio in Hz.
        channels: Output layout mode (Mono or Stereo).
        file_size_bytes: Final size of the compiled asset on disk.
        warnings: Optional list of warnings generated during processing.
        error_message: System error traceback or description on failure.
    """
    task_id: str
    status: TaskStatus
    audio_path: Optional[Path] = None
    duration_seconds: float = 0.0
    generation_time_seconds: float = 0.0
    cache_hit: bool = False
    voice_id: str = ""
    device_used: str = "unknown"
    sample_rate: int = 44100
    channels: AudioChannelMode = AudioChannelMode.MONO
    file_size_bytes: int = 0
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Provides a safe dictionary representation for JSON serialization."""
        data = asdict(self)
        if data["audio_path"]:
            data["audio_path"] = str(data["audio_path"])
        data["channels"] = data["channels"].value
        data["status"] = data["status"].value
        return data


@dataclass(frozen=True)
class BatchGenerationResult:
    """Summary of batch generation pipelines.

    Attributes:
        batch_id: Targeted batch tracking identifier.
        overall_status: Aggregate outcome status.
        results: Collection of individual GenerationResult models.
        success_count: Number of successfully compiled elements.
        failure_count: Number of failed generation items.
        cancelled_count: Number of items cancelled before or during processing.
        total_generation_time: Cumulative elapsed process time in seconds.
    """
    batch_id: str
    overall_status: TaskStatus
    results: List[GenerationResult]
    success_count: int
    failure_count: int
    cancelled_count: int
    total_generation_time: float

    def to_dict(self) -> Dict[str, Any]:
        """Provides a safe dictionary representation for serialization."""
        return {
            "batch_id": self.batch_id,
            "overall_status": self.overall_status.value,
            "results": [r.to_dict() for r in self.results],
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "cancelled_count": self.cancelled_count,
            "total_generation_time": self.total_generation_time,
        }


@dataclass(frozen=True)
class QueueTaskInfo:
    """structural details tracing a task inside the QueueManager.

    Attributes:
        task_id: Unique task tracker.
        request: The initial generation request payload.
        status: Queue execution tracking state.
        priority: Priority tier of the task.
        submitted_at: Timestamp when task entered queue.
        started_at: Timestamp when worker activated generation.
        completed_at: Timestamp when output writing completed.
        retry_count: Number of retries executed after failure encounters.
    """
    task_id: str
    request: TTSRequest
    status: TaskStatus
    priority: GenerationPriority
    submitted_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0


@dataclass(frozen=True)
class CacheInfo:
    """Structural metadata associated with a stored audio cache entry.

    Attributes:
        cache_key: Deterministic hash computed from text and configurations.
        audio_path: Location of cached WAV on physical disk.
        created_at: Datetime tracking storage insertion.
        expires_at: Optional expiration date for cache policies.
        file_size_bytes: Size of stored WAV file.
        text_hash: Hash tracking prompt text specifically.
    """
    cache_key: str
    audio_path: Path
    created_at: datetime
    expires_at: Optional[datetime] = None
    file_size_bytes: int = 0
    text_hash: str = ""


@dataclass(frozen=True)
class ModelStatus:
    """Active diagnostic status of the Fish Speech model runner.

    Attributes:
        device_type: Target hardware mapping (e.g. CUDA, CPU).
        is_loaded: True if model weights are primed and ready for inference.
        memory_allocated_bytes: VRAM active allocation on GPU.
        memory_reserved_bytes: VRAM active cache reserve on GPU.
        last_used_at: Datetime monitoring model idle durations.
    """
    device_type: DeviceType
    is_loaded: bool
    memory_allocated_bytes: int = 0
    memory_reserved_bytes: int = 0
    last_used_at: Optional[datetime] = None


@dataclass(frozen=True)
class HealthStatus:
    """Structural report analyzing system-wide component operational health.

    Attributes:
        is_healthy: Cumulative operational status.
        status_message: Informational summary log message.
        last_checked_at: Datetime recording active checking session.
    """
    is_healthy: bool
    status_message: str
    last_checked_at: datetime = field(default_factory=datetime.utcnow)
