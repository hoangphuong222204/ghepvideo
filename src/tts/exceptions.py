"""Exception hierarchy for Module 08: Fish Speech Engine.

This module defines all custom exceptions raised by the Text-to-Speech system
to ensure robust error propagation and professional exception chaining.
"""

class TTSEngineError(Exception):
    """Base exception class for all errors originating in the TTS Engine (Module 08)."""
    pass


# Configuration & Device Errors
class TTSConfigError(TTSEngineError):
    """Raised when there is an invalid configuration for the TTS engine or its sub-components."""
    pass


class UnsupportedDeviceError(TTSConfigError):
    """Raised when the requested execution device (e.g., CUDA) is unavailable or unsupported."""
    pass


class GPUOutOfMemoryError(TTSEngineError):
    """Raised when a GPU out-of-memory (OOM) condition is detected or encountered."""
    pass


# Model Lifecycle Errors
class ModelLoadError(TTSEngineError):
    """Raised when loading or preparing the TTS model fails."""
    pass


class ModelNotLoadedError(TTSEngineError):
    """Raised when an operation is requested on a model that has not been loaded yet."""
    pass


# Request Validation Errors
class InvalidRequestError(TTSEngineError):
    """Base exception for all invalid input or parameters in a generation request."""
    pass


class InvalidTextError(InvalidRequestError):
    """Raised when input text is empty, malformed, or exceeds supported limits."""
    pass


class InvalidVoiceError(InvalidRequestError):
    """Raised when the requested voice ID is invalid, missing, or unavailable."""
    pass


# Voice Cloning & Reference Audio Errors
class ReferenceAudioError(TTSEngineError):
    """Raised when reference audio for voice cloning is missing, corrupt, or improper."""
    pass


class VoiceCloningError(TTSEngineError):
    """Raised when voice cloning processing, reference transcript parsing, or prompt conditioning fails."""
    pass


# Generation Execution Errors
class GenerationError(TTSEngineError):
    """Raised when the low-level model inference fails to generate speech waveform."""
    pass


class GenerationTimeoutError(GenerationError):
    """Raised when generation execution exceeds the configured timeout limit."""
    pass


class GenerationCancelledError(GenerationError):
    """Raised when a generation task is explicitly and cooperatively cancelled by the caller."""
    pass


# Queue & Cache Errors
class QueueError(TTSEngineError):
    """Raised when a task cannot be queued, scheduled, or executed concurrently."""
    pass


class CacheError(TTSEngineError):
    """Raised when reading, writing, or cleaning the generated audio cache fails."""
    pass


# Audio Processing & Output Errors
class AudioProcessingError(TTSEngineError):
    """Raised when waveform manipulation, resampling, or format conversion fails."""
    pass


class InvalidGeneratedAudioError(AudioProcessingError):
    """Raised when the output of the generation process is empty, silent, or corrupt."""
    pass


class UnsupportedAudioFormatError(AudioProcessingError):
    """Raised when the requested output channels, bit-rate, or sample rate are unsupported."""
    pass


class FileOutputError(TTSEngineError):
    """Raised when writing the final audio asset or WAV file to disk fails."""
    pass
