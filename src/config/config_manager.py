"""Thread-safe Singleton ConfigManager for AI Marketing Studio PRO.

This module acts as the central orchestration controller of the configuration system,
managing load/save pipelines, data validation, auto-directory provisioning, configuration backup,
exporting, importing, environment overrides, observer patterns, and configuration version migrations.
"""

import os
import json
import shutil
import logging
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable, Set
from dataclasses import asdict
from enum import Enum

# Import exceptions, models and validators
from src.config.exceptions import (
    ConfigException,
    ConfigLoadError,
    ConfigSaveError,
    ConfigValidationError,
    ConfigFileNotFoundError,
)
from src.config.config_models import (
    SystemConfig,
    ApplicationConfig,
    GeminiConfig,
    FishSpeechConfig,
    FFmpegConfig,
    VideoConfig,
    AudioConfig,
    DatabaseConfig,
    AssetsConfig,
    AppLanguage,
    AppTheme,
    VideoCodec,
    DeviceType,
)

logger = logging.getLogger("AIMSPro.ConfigManager")


class YamlHelper:
    """Dedicated helper for YAML reading and writing to abstract PyYAML dependencies."""
    
    @staticmethod
    def is_yaml_available() -> bool:
        """Checks if PyYAML library is installed."""
        try:
            import yaml  # type: ignore
            return True
        except ImportError:
            return False

    @staticmethod
    def load(path: Path) -> Dict[str, Any]:
        """Loads a YAML file into a dictionary."""
        import yaml  # type: ignore
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @staticmethod
    def dump(path: Path, data: Dict[str, Any]) -> None:
        """Writes a dictionary to a YAML file atomically."""
        import yaml  # type: ignore
        temp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            os.replace(temp_path, path)
        except Exception as e:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise ConfigSaveError(f"Error writing YAML atomically to '{path}': {e}") from e


class ConfigJsonEncoder(json.JSONEncoder):
    """Custom JSON encoder to automatically handle Python Enums during serialization."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


class ConfigManager:
    """Thread-safe Singleton Configuration Manager.

    Handles loading, saving, backup, importing, and exporting configurations
    while maintaining application-wide consistency and robustness.
    """

    _instance: Optional["ConfigManager"] = None
    _lock: threading.RLock = threading.RLock()

    def __new__(cls, *args: Any, **kwargs: Any) -> "ConfigManager":
        """Enforces a strict Singleton pattern using double-checked locking."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ConfigManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Initializes the ConfigManager instance exactly once.

        Args:
            config_path: Custom configuration path. If omitted, falls back to the
                directory where this manager lives with file name 'default_config.json'.
        """
        if getattr(self, "_initialized", False):
            return

        with self._lock:
            if getattr(self, "_initialized", False):
                return

            self._initialized = True
            self._config: SystemConfig = SystemConfig()
            self._load_lock = threading.RLock()
            self._subscribers: Set[Callable[[SystemConfig], None]] = set()

            # Define default config location relative to this file
            base_dir = Path(__file__).resolve().parent
            self._default_path = base_dir / "default_config.json"

            # Active runtime config path
            if config_path is None:
                self._config_file_path = self._default_path
            else:
                self._config_file_path = Path(config_path)

            # Auto-detect local .env file in parent directories
            self._env_file_path: Path = base_dir.parents[1] / ".env"
            if not self._env_file_path.exists():
                # Fallback to current directory of the workspace
                self._env_file_path = Path.cwd() / ".env"

            # Cache validation fields
            self._last_loaded_mtime: Optional[float] = None
            self._last_loaded_size: Optional[int] = None

            # Auto-run bootstrap load
            self.load()

    @property
    def config(self) -> SystemConfig:
        """Accesses the active in-memory root configuration."""
        return self._config

    @property
    def config_path(self) -> Path:
        """Returns the file path of the current active configuration file."""
        return self._config_file_path

    # --- Observer Pattern ---

    def subscribe(self, callback: Callable[[SystemConfig], None]) -> None:
        """Subscribes an observer callback to be notified upon configuration updates."""
        with self._lock:
            self._subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[SystemConfig], None]) -> None:
        """Unsubscribes an observer callback from configuration updates."""
        with self._lock:
            self._subscribers.discard(callback)

    def notify(self) -> None:
        """Notifies all registered observers of a configuration change."""
        with self._lock:
            subscribers = list(self._subscribers)
        for callback in subscribers:
            try:
                callback(self._config)
            except Exception as e:
                logger.error(f"Error during observer notification: {e}")

    # --- Core Configuration Interface ---

    def load(self, force: bool = False) -> None:
        """Loads configuration from JSON file, merges defaults, and resolves environment overrides.

        Caching is supported; reload is bypassed if the file has not changed on disk unless forced.

        Raises:
            ConfigLoadError: If loading or parsing fails.
        """
        with self._load_lock:
            try:
                # 1. Evaluate cache unless forced reload requested
                if not force and self._config_file_path.exists():
                    stat = self._config_file_path.stat()
                    mtime = stat.st_mtime
                    size = stat.st_size
                    if (
                        self._last_loaded_mtime == mtime
                        and self._last_loaded_size == size
                        and getattr(self, "_config", None) is not None
                    ):
                        logger.debug("Configuration file unchanged on disk. Bypassing load from disk.")
                        return

                # 2. Load raw defaults dictionary
                default_dict = self._get_default_dict()
                file_dict: Dict[str, Any] = {}

                # 3. Create file if missing or read existing JSON
                if not self._config_file_path.exists():
                    logger.warning(f"Config file not found. Creating default configuration file at {self._config_file_path}")
                    self._config_file_path.parent.mkdir(parents=True, exist_ok=True)
                    self._write_json_file(self._config_file_path, default_dict)
                    file_dict = default_dict
                else:
                    logger.info(f"Loading configuration from: {self._config_file_path}")
                    file_dict = self._read_json_file(self._config_file_path)

                # 4. Run automatic, extensible schema migration
                file_dict = self._migrate_config(file_dict)

                # 5. Deep merge to handle missing configuration properties elegantly
                merged_dict = self._deep_merge(default_dict, file_dict)

                # 6. Instantiate structured models hierarchy
                self._config = SystemConfig(
                    config_version=merged_dict.get("config_version", "1.0.0"),
                    application=ApplicationConfig(**merged_dict["application"]),
                    gemini=GeminiConfig(**merged_dict["gemini"]),
                    fish_speech=FishSpeechConfig(**merged_dict["fish_speech"]),
                    ffmpeg=FFmpegConfig(**merged_dict["ffmpeg"]),
                    video=VideoConfig(**merged_dict["video"]),
                    audio=AudioConfig(**merged_dict["audio"]),
                    database=DatabaseConfig(**merged_dict["database"]),
                    assets=AssetsConfig(**merged_dict["assets"])
                )

                # 7. Siphon environment variables from .env file
                self._load_dotenv()

                # 8. Apply active shell environment overrides
                self._apply_env_overrides()

                # 9. cascading full schema audit validation
                self.validate()

                # 10. Bootstrap RotatingFileHandler logging system
                self._setup_logging()

                # 11. Auto-create declared directory folders structure
                self.create_missing_folders()

                # 12. Update active mtime and size tracker fields
                if self._config_file_path.exists():
                    updated_stat = self._config_file_path.stat()
                    self._last_loaded_mtime = updated_stat.st_mtime
                    self._last_loaded_size = updated_stat.st_size

            except Exception as e:
                logger.error(f"Failed to bootstrap configuration: {e}")
                raise ConfigLoadError(f"Could not load configuration system: {e}") from e

    def save(self) -> None:
        """Saves current active configuration to the active file path atomically.

        Raises:
            ConfigSaveError: If saving fails.
        """
        with self._load_lock:
            try:
                # Pre-save cascading validations
                self._config.validate()

                config_dict = self._config_to_dict()
                self._write_json_file(self._config_file_path, config_dict)
                
                # Sync cache details
                if self._config_file_path.exists():
                    stat = self._config_file_path.stat()
                    self._last_loaded_mtime = stat.st_mtime
                    self._last_loaded_size = stat.st_size
                
                logger.info(f"Configuration successfully saved to {self._config_file_path}")
            except Exception as e:
                logger.error(f"Failed to save configuration state: {e}")
                raise ConfigSaveError(f"Failed to save configuration file: {e}") from e

    def reload(self) -> None:
        """Forces a clean reload of the configuration from disk, discarding in-memory changes."""
        logger.info("Reloading configuration from disk...")
        self.load(force=True)

    def reset_default_config(self) -> None:
        """Resets active configuration back to default values and commits to disk."""
        logger.warning("Resetting configuration to original default values.")
        with self._load_lock:
            try:
                default_dict = self._read_json_file(self._default_path) if self._default_path.exists() else self._get_default_dict()
                
                # Re-instantiate models
                self._config = SystemConfig(
                    config_version=default_dict.get("config_version", "1.0.0"),
                    application=ApplicationConfig(**default_dict.get("application", {})),
                    gemini=GeminiConfig(**default_dict.get("gemini", {})),
                    fish_speech=FishSpeechConfig(**default_dict.get("fish_speech", {})),
                    ffmpeg=FFmpegConfig(**default_dict.get("ffmpeg", {})),
                    video=VideoConfig(**default_dict.get("video", {})),
                    audio=AudioConfig(**default_dict.get("audio", {})),
                    database=DatabaseConfig(**default_dict.get("database", {})),
                    assets=AssetsConfig(**default_dict.get("assets", {}))
                )
                
                # Save to active file path
                config_dict = self._config_to_dict()
                self._write_json_file(self._config_file_path, config_dict)
                logger.info(f"Defaults successfully restored onto {self._config_file_path}")
                
                self.create_missing_folders()
                self.notify()
            except Exception as e:
                logger.error(f"Failed to reset default config: {e}")
                raise ConfigSaveError(f"Could not reset config to default: {e}") from e

    def backup_config(self, destination_dir: Optional[Union[str, Path]] = None) -> Path:
        """Creates a timestamped backup of the current active config file.

        Limits total backups to the latest 20, automatically removing older backups.

        Args:
            destination_dir: Folder to place the backup. Defaults to the configured backup folder.

        Returns:
            The Path of the newly created backup file.
        """
        with self._load_lock:
            try:
                # Resolve directory
                if destination_dir is None:
                    dest_dir = Path(self._config.database.backup_folder)
                else:
                    dest_dir = Path(destination_dir)

                dest_dir.mkdir(parents=True, exist_ok=True)

                # Format name with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"config_backup_{timestamp}.json"
                backup_path = dest_dir / backup_filename

                shutil.copy2(self._config_file_path, backup_path)
                logger.info(f"Configuration backup completed: {backup_path}")
                
                # Rotate backups (keep only 20 latest)
                self._rotate_backups(dest_dir)
                
                return backup_path
            except Exception as e:
                logger.error(f"Failed to create config backup: {e}")
                raise ConfigSaveError(f"Backup operation failed: {e}") from e

    def validate(self) -> None:
        """Validates the entire active configuration.

        Raises:
            ConfigValidationError: If validation fails.
        """
        try:
            self._config.validate()
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ConfigValidationError(f"Configuration validation failed: {e}") from e

    def get(self, path: str, default: Any = None) -> Any:
        """Gets a configuration value using dotted path notation."""
        return self._config.get(path, default)

    def set(self, path: str, value: Any) -> None:
        """Sets a configuration value using dotted path notation and validates the update."""
        parts = path.split(".")
        if len(parts) < 2:
            raise ConfigValidationError(f"Invalid path notation: '{path}'. Path must have 'section.field' format.")
            
        section_name = parts[0]
        if not hasattr(self._config, section_name):
            raise ConfigValidationError(f"Configuration section '{section_name}' does not exist.")
            
        section = getattr(self._config, section_name)
        target = section
        sub_parts = parts[1:]
        
        for part in sub_parts[:-1]:
            if hasattr(target, part):
                target = getattr(target, part)
            else:
                raise ConfigValidationError(f"Invalid path '{path}': attribute '{part}' does not exist.")
                
        final_key = sub_parts[-1]
        if not hasattr(target, final_key):
            raise ConfigValidationError(f"Invalid path '{path}': attribute '{final_key}' does not exist.")
            
        original_value = getattr(target, final_key)
        
        with self._load_lock:
            try:
                expected_type = type(original_value)
                if issubclass(expected_type, Enum) and isinstance(value, str):
                    value = expected_type(value)
                    
                setattr(target, final_key, value)
                
                # cascading validations
                self.validate()
                
                # Persist change atomically
                self.save()
                
                # Notify observers
                self.notify()
            except Exception as e:
                # Rollback state on failure
                setattr(target, final_key, original_value)
                raise ConfigValidationError(f"Failed to set '{path}' to {value}: {e}") from e

    def get_checksum(self) -> str:
        """Generates a SHA256 integrity checksum hash of the active configuration."""
        config_dict = self._config_to_dict()
        serialized = json.dumps(config_dict, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def verify_integrity(self, expected_checksum: str) -> bool:
        """Verifies that the configuration integrity hash matches an expected value."""
        return self.get_checksum() == expected_checksum

    def create_missing_folders(self) -> None:
        """Safely creates all directories declared in the active config."""
        # Collect paths to create
        folders = [
            Path(self._config.fish_speech.output_folder),
            Path(self._config.audio.music_folder),
            Path(self._config.audio.voice_folder),
            Path(self._config.database.backup_folder),
            Path(self._config.assets.input),
            Path(self._config.assets.output),
            Path(self._config.assets.temp),
            Path(self._config.assets.logs),
            Path(self._config.assets.cache),
            Path(self._config.assets.resources),
        ]

        # Extract parent path of database file if it is an actual file
        sqlite_file = self._config.database.sqlite_path
        if sqlite_file != ":memory:":
            sqlite_parent = Path(sqlite_file).parent
            if sqlite_parent and sqlite_parent != Path("."):
                folders.append(sqlite_parent)

        for folder in folders:
            try:
                folder.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Verified directory exists: {folder}")
            except Exception as e:
                logger.warning(f"Could not auto-create workspace folder '{folder}': {e}")

    def export_config(self, export_path: Union[str, Path]) -> None:
        """Exports active configurations to a custom target file.

        Args:
            export_path: Destination path. Supports .json and .yaml/.yml formats.
        """
        path = Path(export_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        config_dict = self._config_to_dict()

        if path.suffix in {".yaml", ".yml"}:
            if YamlHelper.is_yaml_available():
                YamlHelper.dump(path, config_dict)
                logger.info(f"Exported configuration in YAML format to: {path}")
                return
            else:
                logger.warning("YAML library is missing. Falling back to JSON export format.")
        
        self._write_json_file(path, config_dict)
        logger.info(f"Exported configuration in JSON format to: {path}")

    def import_config(self, import_path: Union[str, Path]) -> None:
        """Imports and validates config from an external file, then makes it the active config.

        Args:
            import_path: External path containing the new config payload.
        """
        path = Path(import_path)
        if not path.exists():
            raise ConfigFileNotFoundError(f"Import file does not exist: {path}")

        logger.info(f"Importing configuration file from: {path}")
        try:
            imported_dict: Dict[str, Any] = {}
            if path.suffix in {".yaml", ".yml"}:
                if YamlHelper.is_yaml_available():
                    imported_dict = YamlHelper.load(path)
                else:
                    raise ConfigLoadError("YAML library missing. Unable to parse imported YAML file.")
            else:
                imported_dict = self._read_json_file(path)

            # Apply migrations to raw imported dict
            imported_dict = self._migrate_config(imported_dict)

            # Deep merge with defaults to safeguard integrity of missing fields
            default_dict = self._get_default_dict()
            merged_dict = self._deep_merge(default_dict, imported_dict)

            # Build test config instance
            test_config = SystemConfig(
                config_version=merged_dict.get("config_version", "1.0.0"),
                application=ApplicationConfig(**merged_dict["application"]),
                gemini=GeminiConfig(**merged_dict["gemini"]),
                fish_speech=FishSpeechConfig(**merged_dict["fish_speech"]),
                ffmpeg=FFmpegConfig(**merged_dict["ffmpeg"]),
                video=VideoConfig(**merged_dict["video"]),
                audio=AudioConfig(**merged_dict["audio"]),
                database=DatabaseConfig(**merged_dict["database"]),
                assets=AssetsConfig(**merged_dict["assets"])
            )

            # cascades audit checks
            test_config.validate()

            # Adopt verified state
            with self._load_lock:
                self._config = test_config
                self.save()
                
                # Notify observers
                self.notify()

            logger.info("External configuration successfully verified and loaded as active config.")
        except Exception as e:
            logger.error(f"Import operation aborted due to integrity failures: {e}")
            raise ConfigValidationError(f"Aborted configuration import. Validation failed: {e}") from e

    def update_section(self, section_name: str, updates: Dict[str, Any]) -> None:
        """Thread-safely updates attributes within a given configuration section.

        Args:
            section_name: Target dataclass section name.
            updates: Dictionary containing property-value mappings.
        """
        if not hasattr(self._config, section_name):
            raise ConfigValidationError(f"Configuration has no section named '{section_name}'")

        with self._load_lock:
            section = getattr(self._config, section_name)
            
            # Verify keys exist first
            for k in updates.keys():
                if not hasattr(section, k):
                    raise ConfigValidationError(f"Invalid configuration key '{k}' for section '{section_name}'")
                    
            # Create backup to rollback in case of validation failure
            backup_dict = {k: getattr(section, k) for k in updates.keys()}

            try:
                for k, v in updates.items():
                    expected_type = type(getattr(section, k))
                    # Auto-cast Enum string values
                    if issubclass(expected_type, Enum) and isinstance(v, str):
                        v = expected_type(v)
                    setattr(section, k, v)

                # Validate updated system config state
                self._config.validate()
                
                # Save changes atomically
                config_dict = self._config_to_dict()
                self._write_json_file(self._config_file_path, config_dict)
                logger.info(f"Updated config section '{section_name}' and saved to disk.")
                
                # Notify observers
                self.notify()
            except Exception as e:
                # Rollback to original state
                logger.error(f"Validation failed for updates on '{section_name}'. Rolling back updates.")
                for k, v in backup_dict.items():
                    setattr(section, k, v)
                raise ConfigValidationError(f"Failed to update section '{section_name}': {e}") from e

    # --- Internal Helpers ---

    def _get_default_dict(self) -> Dict[str, Any]:
        """Provides raw dictionary fallback equivalents of standard system templates."""
        return self._config_to_dict(SystemConfig())

    def _serialize_value(self, val: Any) -> Any:
        """Helper to serialize complex types (like Enums, Paths, Sets) to primitive values."""
        if isinstance(val, Enum):
            return val.value
        elif isinstance(val, Path):
            return str(val)
        elif isinstance(val, (set, tuple)):
            return [self._serialize_value(item) for item in val]
        elif isinstance(val, dict):
            return {k: self._serialize_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [self._serialize_value(v) for v in val]
        else:
            return val

    def _config_to_dict(self, cfg_instance: Optional[SystemConfig] = None) -> Dict[str, Any]:
        """Converts SystemConfig instance to raw dictionary structure using asdict()."""
        instance = cfg_instance or self._config
        raw_dict = asdict(instance)
        return self._serialize_value(raw_dict)

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merges override dictionary into base dictionary structure safely."""
        merged = base.copy()
        for k, v in override.items():
            if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
                merged[k] = self._deep_merge(merged[k], v)
            else:
                merged[k] = v
        return merged

    def _read_json_file(self, path: Path) -> Dict[str, Any]:
        """Reads JSON file safely."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ConfigLoadError(f"Error parsing file '{path}': {e}") from e

    def _write_json_file(self, path: Path, data: Dict[str, Any]) -> None:
        """Writes dictionary to file in JSON format atomically using a temporary file."""
        temp_path = path.with_suffix(path.suffix + ".tmp")
        try:
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, cls=ConfigJsonEncoder)
            os.replace(temp_path, path)
        except Exception as e:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise ConfigSaveError(f"Error writing file atomically to '{path}': {e}") from e

    def _apply_single_override(self, env_k: str, env_v: str) -> None:
        """Applies a single environment variable override to config."""
        if env_k == "GEMINI_API_KEY":
            self._config.gemini.api_key = env_v
            logger.debug("Applied environment override: GEMINI_API_KEY")
            return

        prefix = "AIMS_"
        if not env_k.startswith(prefix):
            return

        parts = env_k[len(prefix):].lower().split("_")
        if len(parts) < 2:
            return

        section_name = parts[0]
        attr_name = "_".join(parts[1:])

        if hasattr(self._config, section_name):
            section = getattr(self._config, section_name)
            if hasattr(section, attr_name):
                curr_val = getattr(section, attr_name)
                try:
                    # Attempt to dynamically typecast to original field datatype
                    if isinstance(curr_val, bool):
                        typed_val: Any = env_v.lower() in {"true", "1", "yes"}
                    elif isinstance(curr_val, int):
                        typed_val = int(env_v)
                    elif isinstance(curr_val, float):
                        typed_val = float(env_v)
                    elif isinstance(curr_val, Enum):
                        typed_val = type(curr_val)(env_v)
                    else:
                        typed_val = str(env_v)

                    setattr(section, attr_name, typed_val)
                    logger.debug(f"Environment override matched: {env_k} -> {section_name}.{attr_name} = {typed_val}")
                except ValueError:
                    logger.warning(f"Failed to cast environment override value for '{env_k}' to type '{type(curr_val).__name__}'")

    def _load_dotenv(self) -> None:
        """Parses a local .env file manual parser line-by-line supporting multiple quote styles."""
        if not self._env_file_path.exists():
            return

        logger.info(f"Sourcing environment variables from {self._env_file_path}")
        try:
            with open(self._env_file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 1. Ignore blank lines and comment blocks
                    if not line or line.startswith("#"):
                        continue
                    
                    # 2. Support export KEY=value prefix strip
                    if line.startswith("export "):
                        line = line[7:].strip()
                    
                    # 3. Strip inline comments outside of quotes
                    if "#" in line:
                        parts = line.split("#", 1)
                        before_comment = parts[0].strip()
                        if before_comment:
                            # Verify quote balance
                            if before_comment.count('"') % 2 == 0 and before_comment.count("'") % 2 == 0:
                                line = before_comment
                    
                    if "=" not in line:
                        continue
                    
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    
                    # Strip wrapping quotes if any
                    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                        v = v[1:-1]
                    
                    # Set into active OS environment variables and apply immediately
                    os.environ[k] = v
                    self._apply_single_override(k, v)
        except Exception as e:
            logger.warning(f"Error reading local environment file '{self._env_file_path}': {e}")

    def _apply_env_overrides(self) -> None:
        """Applies configuration parameter overrides from environment variables."""
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if gemini_api_key:
            self._apply_single_override("GEMINI_API_KEY", gemini_api_key)

        for env_k, env_v in os.environ.items():
            if env_k.startswith("AIMS_"):
                self._apply_single_override(env_k, env_v)

    def _rotate_backups(self, dest_dir: Path) -> None:
        """Keeps only the 20 most recent config backups, deleting older ones."""
        try:
            backups = sorted(
                list(dest_dir.glob("config_backup_*.json")),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if len(backups) > 20:
                for old_backup in backups[20:]:
                    try:
                        old_backup.unlink()
                        logger.info(f"Rotated old backup file: {old_backup}")
                    except OSError as e:
                        logger.warning(f"Failed to delete old backup {old_backup}: {e}")
        except Exception as e:
            logger.warning(f"Error during backup rotation: {e}")

    def _migrate_config(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrates older configuration dictionaries to the latest schema version."""
        target_version = "1.0.0"
        loaded_version = raw_data.get("config_version", "0.0.0")
        
        if loaded_version == target_version:
            return raw_data
            
        logger.info(f"Migrating config from version {loaded_version} to {target_version}")
        
        # Extensible migration step
        if loaded_version < "1.0.0":
            raw_data["config_version"] = "1.0.0"
            if "video" not in raw_data:
                raw_data["video"] = {}
            if "allow_custom_resolution" not in raw_data["video"]:
                raw_data["video"]["allow_custom_resolution"] = False
            if "gemini" not in raw_data:
                raw_data["gemini"] = {}
            if "allowed_models" not in raw_data["gemini"]:
                raw_data["gemini"]["allowed_models"] = [
                    "gemini-2.5-flash",
                    "gemini-2.5-pro",
                    "gemini-2.5-flash-lite",
                    "gemini-3.5-flash"
                ]
                    
        return raw_data

    def _setup_logging(self) -> None:
        """Sets up a RotatingFileHandler for the application logger based on configured log path."""
        try:
            log_dir = Path(self._config.assets.logs)
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "aimspro.log"
            
            root_logger = logging.getLogger("AIMSPro")
            root_logger.setLevel(logging.INFO)
            
            # Prevent adding duplicate handlers
            has_rotating_handler = any(
                isinstance(h, logging.handlers.RotatingFileHandler) if hasattr(logging.handlers, "RotatingFileHandler") else False
                for h in root_logger.handlers
            )
            
            if not has_rotating_handler:
                from logging.handlers import RotatingFileHandler
                handler = RotatingFileHandler(
                    log_file,
                    maxBytes=10 * 1024 * 1024,  # 10 MB
                    backupCount=5,
                    encoding="utf-8"
                )
                formatter = logging.Formatter(
                    "[%(asctime)s] %(levelname)s [%(name)s] - %(message)s"
                )
                handler.setFormatter(formatter)
                root_logger.addHandler(handler)
                logger.info(f"Logging RotatingFileHandler initialized at: {log_file}")
        except Exception as e:
            import sys
            sys.stderr.write(f"Warning: Failed to setup rotating file logging: {e}\n")

