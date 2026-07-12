"""Typed and validated configuration schemas for AI Marketing Studio PRO.

This module defines individual domain-specific configuration categories using standard Python
dataclasses. Each sub-config class includes a custom `validate` method that performs self-audit checks.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List
from src.config.validators import ConfigValidators


class AppLanguage(str, Enum):
    """UI language choices."""
    VI = "vi"
    EN = "en"


class AppTheme(str, Enum):
    """UI theme choices."""
    ARTISTIC_FLAIR = "Artistic Flair"
    SLATE_DARK = "Slate Dark"
    COSMIC_LIGHT = "Cosmic Light"


class VideoCodec(str, Enum):
    """Supported video codecs for FFmpeg."""
    LIBX264 = "libx264"
    LIBX265 = "libx265"
    H264 = "h264"
    HEVC = "hevc"
    VP9 = "vp9"
    MPEG4 = "mpeg4"


class DeviceType(str, Enum):
    """Execution device types."""
    CPU = "cpu"
    CUDA = "cuda"
    AUTO = "auto"


@dataclass
class ApplicationConfig:
    """Configuration for global application settings."""
    version: str = "1.0.0"
    language: AppLanguage = AppLanguage.VI
    theme: AppTheme = AppTheme.ARTISTIC_FLAIR

    def __post_init__(self) -> None:
        if isinstance(self.language, str):
            self.language = AppLanguage(self.language)
        if isinstance(self.theme, str):
            self.theme = AppTheme(self.theme)

    def validate(self) -> None:
        """Validates Application settings."""
        ConfigValidators.validate_non_empty_string("application.version", self.version)
        self.language = ConfigValidators.validate_language(self.language)
        self.theme = ConfigValidators.validate_theme(self.theme)


@dataclass
class GeminiConfig:
    """Configuration for Google Gemini API."""
    api_key: str = "MY_GEMINI_API_KEY"
    model: str = "gemini-3.5-flash"
    temperature: float = 0.3
    top_p: float = 0.95
    max_tokens: int = 4096
    allowed_models: List[str] = field(default_factory=lambda: [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash-lite",
        "gemini-3.5-flash"
    ])

    def validate(self) -> None:
        """Validates Gemini engine configurations."""
        ConfigValidators.validate_non_empty_string("gemini.api_key", self.api_key)
        ConfigValidators.validate_non_empty_string("gemini.model", self.model)
        if self.model not in self.allowed_models:
            from src.config.exceptions import ConfigValidationError
            raise ConfigValidationError(
                f"Model '{self.model}' is not in the whitelist: {self.allowed_models}"
            )
        self.temperature = ConfigValidators.validate_temperature(self.temperature)
        self.top_p = ConfigValidators.validate_top_p(self.top_p)
        self.max_tokens = ConfigValidators.validate_max_tokens(self.max_tokens)


@dataclass
class FishSpeechConfig:
    """Configuration for Fish Speech TTS Engine."""
    model_path: str = "models/fish_speech_v1"
    device: DeviceType = DeviceType.CUDA
    sample_rate: int = 44100
    output_folder: str = "exports/audio"

    def __post_init__(self) -> None:
        if isinstance(self.device, str):
            self.device = DeviceType(self.device)

    def validate(self) -> None:
        """Validates Fish Speech engine parameters."""
        ConfigValidators.validate_non_empty_string("fish_speech.model_path", self.model_path)
        self.device = ConfigValidators.validate_device(self.device)
        self.sample_rate = ConfigValidators.validate_sample_rate(self.sample_rate)
        ConfigValidators.validate_non_empty_string("fish_speech.output_folder", self.output_folder)


@dataclass
class FFmpegConfig:
    """Configuration for local FFmpeg executable and profile settings."""
    executable: str = "bin/ffmpeg.exe"
    threads: int = 4
    preset: str = "medium"

    def validate(self) -> None:
        """Validates FFmpeg runtime settings."""
        ConfigValidators.validate_non_empty_string("ffmpeg.executable", self.executable)
        self.threads = ConfigValidators.validate_threads(self.threads)
        ConfigValidators.validate_non_empty_string("ffmpeg.preset", self.preset)


@dataclass
class VideoConfig:
    """Configuration for target video composition format."""
    resolution: str = "1080x1920"
    fps: int = 30
    codec: VideoCodec = VideoCodec.LIBX264
    crf: int = 23
    allow_custom_resolution: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.codec, str):
            self.codec = VideoCodec(self.codec)

    def validate(self) -> None:
        """Validates video format schemas."""
        self.resolution = ConfigValidators.validate_resolution(
            self.resolution,
            allow_custom=self.allow_custom_resolution
        )
        self.fps = ConfigValidators.validate_fps(self.fps)
        self.codec = ConfigValidators.validate_codec(self.codec)
        self.crf = ConfigValidators.validate_crf(self.crf)


@dataclass
class AudioConfig:
    """Configuration for assets, music, voice folders, and global volume values."""
    music_folder: str = "assets/audio_templates"
    voice_folder: str = "exports/voice"
    volume: float = 0.8

    def validate(self) -> None:
        """Validates sound rendering settings."""
        ConfigValidators.validate_non_empty_string("audio.music_folder", self.music_folder)
        ConfigValidators.validate_non_empty_string("audio.voice_folder", self.voice_folder)
        self.volume = ConfigValidators.validate_volume(self.volume)


@dataclass
class DatabaseConfig:
    """Configuration for local persistence database and backup locations."""
    sqlite_path: str = "database.db"
    backup_folder: str = "backups"

    def validate(self) -> None:
        """Validates local database persistence metrics."""
        self.sqlite_path = ConfigValidators.validate_sqlite_path(self.sqlite_path)
        ConfigValidators.validate_non_empty_string("database.backup_folder", self.backup_folder)


@dataclass
class AssetsConfig:
    """Root asset mapping catalog managing folder hierarchies."""
    input: str = "assets/input"
    output: str = "exports"
    temp: str = "temp"
    logs: str = "logs"
    cache: str = "cache"
    resources: str = "resources"
    plugins: str = "plugins"

    def validate(self) -> None:
        """Validates asset folder namespaces."""
        ConfigValidators.validate_non_empty_string("assets.input", self.input)
        ConfigValidators.validate_non_empty_string("assets.output", self.output)
        ConfigValidators.validate_non_empty_string("assets.temp", self.temp)
        ConfigValidators.validate_non_empty_string("assets.logs", self.logs)
        ConfigValidators.validate_non_empty_string("assets.cache", self.cache)
        ConfigValidators.validate_non_empty_string("assets.resources", self.resources)
        ConfigValidators.validate_non_empty_string("assets.plugins", self.plugins)


@dataclass
class SystemConfig:
    """Root configuration aggregator dataclass mapping out all domain-specific categories."""
    config_version: str = "1.0.0"
    application: ApplicationConfig = field(default_factory=ApplicationConfig)
    gemini: GeminiConfig = field(default_factory=GeminiConfig)
    fish_speech: FishSpeechConfig = field(default_factory=FishSpeechConfig)
    ffmpeg: FFmpegConfig = field(default_factory=FFmpegConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    assets: AssetsConfig = field(default_factory=AssetsConfig)

    def validate(self) -> None:
        """Fires cascading audits across all categories recursively."""
        self.application.validate()
        self.gemini.validate()
        self.fish_speech.validate()
        self.ffmpeg.validate()
        self.video.validate()
        self.audio.validate()
        self.database.validate()
        self.assets.validate()

    def get(self, path: str, default: Any = None) -> Any:
        """Gets a configuration value using a dotted path notation."""
        parts = path.split(".")
        current: Any = self
        if not parts or parts == [""]:
            return default
            
        try:
            for part in parts:
                if hasattr(current, part):
                    current = getattr(current, part)
                elif isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return default
            return current
        except Exception:
            return default

