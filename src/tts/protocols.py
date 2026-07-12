"""Stable contracts using typing.Protocol for Module 08 (Fish Speech Engine).

This module defines decoupled interfaces for TTS models, voice profiling, caching,
and scheduling subsystems to ensure high testability and architectural flexibility.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable

from src.tts.tts_models import (
    DeviceType,
    GenerationProgress,
    GenerationResult,
    ModelStatus,
    QueueTaskInfo,
    TTSRequest,
    VoiceMetadata,
    VoiceType,
)


@runtime_checkable
class TTSModelRunner(Protocol):
    """Protocol for the low-level neural net wrapper (Fish Speech model loader & inferrer)."""

    def load_model(self, device: Optional[DeviceType] = None) -> None:
        """Asynchronously or synchronously load and compile weights into active memory.

        Args:
            device: Optional target device. Defaults to AUTO/CUDA if available.

        Raises:
            ModelLoadError: If loading or compiling weights fails.
            UnsupportedDeviceError: If target device is not supported on host.
        """
        ...

    def unload_model(self) -> None:
        """Safely release GPU memory allocations and model weights."""
        ...

    def generate(
        self,
        request: TTSRequest,
        progress_callback: Optional[Callable[[GenerationProgress], None]] = None,
    ) -> GenerationResult:
        """Run speech generation inference for a single normalized text.

        Args:
            request: Validated speech synthesis request configuration.
            progress_callback: Optional webhook for micro-progress state updates.

        Returns:
            The immutable generation result.

        Raises:
            ModelNotLoadedError: If invoked before load_model has successfully completed.
            GenerationError: If neural generation fails.
            GPUOutOfMemoryError: If VRAM limit is hit during model execution.
        """
        ...

    def get_status(self) -> ModelStatus:
        """Retrieve diagnostic parameters of the loaded model runner.

        Returns:
            ModelStatus snapshot object.
        """
        ...


@runtime_checkable
class VoiceRegistry(Protocol):
    """Protocol managing voice catalogs, reference audio, and cloning metadata."""

    def get_voice(self, voice_id: str) -> Optional[VoiceMetadata]:
        """Fetch descriptive metadata of a registered voice by its ID.

        Args:
            voice_id: Stable identifier of the voice.

        Returns:
            VoiceMetadata object if found, otherwise None.
        """
        ...

    def list_voices(self, voice_type: Optional[VoiceType] = None) -> List[VoiceMetadata]:
        """Retrieve all registered voices, optionally filtered by type.

        Args:
            voice_type: Optional classification filter (e.g., Preset, Cloned).

        Returns:
            List of matching VoiceMetadata objects.
        """
        ...

    def register_cloned_voice(
        self,
        voice_id: str,
        display_name: str,
        audio_path: Path,
        transcript: Optional[str] = None,
        language: str = "vi",
    ) -> VoiceMetadata:
        """Register a new cloned voice using clean reference audio.

        Args:
            voice_id: Stable identifier for the voice profile.
            display_name: Descriptive user-facing label.
            audio_path: Location of clean 16-bit reference WAV file.
            transcript: Exact transcript of words spoken in the audio file.
            language: ISO language code.

        Returns:
            The newly created VoiceMetadata record.

        Raises:
            InvalidVoiceError: If the voice ID is already in use.
            ReferenceAudioError: If reference audio is missing or corrupt.
        """
        ...

    def delete_cloned_voice(self, voice_id: str) -> None:
        """Remove a cloned voice and its reference metadata from disk.

        Args:
            voice_id: Identifies the cloned voice to delete.

        Raises:
            InvalidVoiceError: If voice ID is not found or is a preset voice.
        """
        ...


@runtime_checkable
class TTSCache(Protocol):
    """Protocol for local WAV caching layers to bypass repetitive computation."""

    def get(self, request: TTSRequest) -> Optional[Path]:
        """Query cache to locate pre-generated WAV files matching the request.

        Args:
            request: The TTS generation request to query against.

        Returns:
            Path to the cached WAV file if hit, otherwise None.
        """
        ...

    def put(self, request: TTSRequest, source_path: Path) -> Path:
        """Store a newly generated WAV file into the cache directory.

        Args:
            request: The source TTS request payload used to compute the cache key.
            source_path: Path to the generated WAV on disk.

        Returns:
            The new stable Path inside the cache directory.

        Raises:
            CacheError: If writing or renaming the cached file fails.
        """
        ...

    def clear(self) -> None:
        """Purge all files and clear the cache tracking state.

        Raises:
            CacheError: If file deletion fails.
        """
        ...

    def get_size(self) -> int:
        """Retrieve the cumulative size of cached files in bytes."""
        ...


@runtime_checkable
class TTSQueue(Protocol):
    """Protocol managing priority scheduling and concurrency of TTS generation requests."""

    def enqueue(self, request: TTSRequest) -> str:
        """Submit a new synthesis task to the scheduling queue.

        Args:
            request: The TTSRequest containing texts and settings.

        Returns:
            A unique task ID representing the queued item.

        Raises:
            QueueError: If task cannot be enqueued or queue is full.
        """
        ...

    def get_task_info(self, task_id: str) -> Optional[QueueTaskInfo]:
        """Fetch tracking details of a queued or completed task.

        Args:
            task_id: Unique identifier string.

        Returns:
            QueueTaskInfo object if found, otherwise None.
        """
        ...

    def cancel_task(self, task_id: str) -> None:
        """Mark a pending or running task as cancelled.

        Args:
            task_id: Unique task identifier.

        Raises:
            QueueError: If task is already completed or cannot be cancelled.
        """
        ...
