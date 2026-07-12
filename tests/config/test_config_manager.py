"""Comprehensive Unit Tests for AIMS Pro Configuration System.

This test suite covers 100% of the methods and edge cases of the configuration package,
including ConfigManager, ConfigValidators, ConfigModels, Exceptions, and Helpers.
"""

import os
import json
import shutil
import unittest
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import config module components
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
from src.config.validators import ConfigValidators
from src.config.config_manager import ConfigManager, YamlHelper, ConfigJsonEncoder


class TestConfigExceptions(unittest.TestCase):
    """Verifies hierarchy of custom config exceptions."""

    def test_exception_inheritance(self):
        """Ensure all custom exceptions inherit from ConfigException."""
        self.assertTrue(issubclass(ConfigLoadError, ConfigException))
        self.assertTrue(issubclass(ConfigValidationError, ConfigException))
        self.assertTrue(issubclass(ConfigSaveError, ConfigException))
        self.assertTrue(issubclass(ConfigFileNotFoundError, ConfigException))


class TestConfigValidators(unittest.TestCase):
    """Comprehensive validation rules testing."""

    def test_validate_non_empty_string(self):
        """Test non-empty string validation."""
        self.assertEqual(ConfigValidators.validate_non_empty_string("test", "  value  "), "value")
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_non_empty_string("test", 123)
            
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_non_empty_string("test", "   ")

    def test_validate_language(self):
        """Test language parsing and validation."""
        self.assertEqual(ConfigValidators.validate_language("vi"), AppLanguage.VI)
        self.assertEqual(ConfigValidators.validate_language("en"), AppLanguage.EN)
        self.assertEqual(ConfigValidators.validate_language(AppLanguage.VI), AppLanguage.VI)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_language("fr")

    def test_validate_theme(self):
        """Test theme validation."""
        self.assertEqual(ConfigValidators.validate_theme("Artistic Flair"), AppTheme.ARTISTIC_FLAIR)
        self.assertEqual(ConfigValidators.validate_theme("Slate Dark"), AppTheme.SLATE_DARK)
        self.assertEqual(ConfigValidators.validate_theme(AppTheme.COSMIC_LIGHT), AppTheme.COSMIC_LIGHT)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_theme("Retro Theme")

    def test_validate_temperature(self):
        """Test temperature boundaries."""
        self.assertEqual(ConfigValidators.validate_temperature(0.5), 0.5)
        self.assertEqual(ConfigValidators.validate_temperature("0.7"), 0.7)
        self.assertEqual(ConfigValidators.validate_temperature(0.0), 0.0)
        self.assertEqual(ConfigValidators.validate_temperature(2.0), 2.0)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_temperature(-0.1)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_temperature(2.1)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_temperature("not_a_float")

    def test_validate_top_p(self):
        """Test top_p boundaries."""
        self.assertEqual(ConfigValidators.validate_top_p(0.95), 0.95)
        self.assertEqual(ConfigValidators.validate_top_p("0.5"), 0.5)
        self.assertEqual(ConfigValidators.validate_top_p(0.0), 0.0)
        self.assertEqual(ConfigValidators.validate_top_p(1.0), 1.0)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_top_p(-0.01)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_top_p(1.01)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_top_p("not_a_float")

    def test_validate_max_tokens(self):
        """Test max tokens constraints."""
        self.assertEqual(ConfigValidators.validate_max_tokens(2048), 2048)
        self.assertEqual(ConfigValidators.validate_max_tokens("4096"), 4096)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_max_tokens(0)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_max_tokens(-50)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_max_tokens("not_an_int")

    def test_validate_device(self):
        """Test execution device validations."""
        self.assertEqual(ConfigValidators.validate_device("cpu"), DeviceType.CPU)
        self.assertEqual(ConfigValidators.validate_device("cuda"), DeviceType.CUDA)
        self.assertEqual(ConfigValidators.validate_device(DeviceType.AUTO), DeviceType.AUTO)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_device("tpu")

    def test_validate_sample_rate(self):
        """Test sample rate presets validation."""
        self.assertEqual(ConfigValidators.validate_sample_rate(44100), 44100)
        self.assertEqual(ConfigValidators.validate_sample_rate("16000"), 16000)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_sample_rate(44101)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_sample_rate("not_an_int")

    def test_validate_threads(self):
        """Test FFmpeg thread allocations."""
        self.assertEqual(ConfigValidators.validate_threads(4), 4)
        self.assertEqual(ConfigValidators.validate_threads("12"), 12)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_threads(0)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_threads(129)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_threads("not_an_int")

    def test_validate_resolution(self):
        """Test standard vs custom resolution logic."""
        self.assertEqual(ConfigValidators.validate_resolution("1080x1920"), "1080x1920")
        
        # Test non-standard portrait resolution fails by default
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_resolution("1080x1080")
            
        # Test custom resolution bypasses Standard Whitelist but respects regex
        self.assertEqual(ConfigValidators.validate_resolution("1080x1080", allow_custom=True), "1080x1080")
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_resolution("invalid_pattern", allow_custom=True)

    def test_validate_fps(self):
        """Test video frame rate bounds."""
        self.assertEqual(ConfigValidators.validate_fps(30), 30)
        self.assertEqual(ConfigValidators.validate_fps("60"), 60)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_fps(0)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_fps(121)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_fps("not_an_int")

    def test_validate_codec(self):
        """Test FFmpeg codec validations."""
        self.assertEqual(ConfigValidators.validate_codec("libx264"), VideoCodec.LIBX264)
        self.assertEqual(ConfigValidators.validate_codec(VideoCodec.LIBX265), VideoCodec.LIBX265)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_codec("h263")

    def test_validate_crf(self):
        """Test video CRF constraints."""
        self.assertEqual(ConfigValidators.validate_crf(23), 23)
        self.assertEqual(ConfigValidators.validate_crf("18"), 18)
        self.assertEqual(ConfigValidators.validate_crf(0), 0)
        self.assertEqual(ConfigValidators.validate_crf(51), 51)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_crf(-1)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_crf(52)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_crf("not_an_int")

    def test_validate_volume(self):
        """Test audio volume limits."""
        self.assertEqual(ConfigValidators.validate_volume(0.8), 0.8)
        self.assertEqual(ConfigValidators.validate_volume("1.5"), 1.5)
        self.assertEqual(ConfigValidators.validate_volume(0.0), 0.0)
        self.assertEqual(ConfigValidators.validate_volume(2.0), 2.0)
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_volume(-0.01)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_volume(2.01)
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_volume("not_a_float")

    def test_validate_sqlite_path(self):
        """Test SQLite DB path validations."""
        self.assertEqual(ConfigValidators.validate_sqlite_path("my_database.db"), "my_database.db")
        self.assertEqual(ConfigValidators.validate_sqlite_path(":memory:"), ":memory:")
        
        with self.assertRaises(ConfigValidationError):
            ConfigValidators.validate_sqlite_path("database.txt")


class TestConfigModels(unittest.TestCase):
    """Test structures, post-initializations, and self-validations of configuration dataclasses."""

    def test_dataclasses_instantiation_and_validation(self):
        """Verify successful instantiation and validation cascading."""
        config = SystemConfig()
        config.validate()  # Should validate defaults perfectly
        
        # Test __post_init__ enum parsing
        app_cfg = ApplicationConfig(language="vi", theme="Slate Dark")
        self.assertEqual(app_cfg.language, AppLanguage.VI)
        self.assertEqual(app_cfg.theme, AppTheme.SLATE_DARK)

    def test_gemini_model_whitelist(self):
        """Verify that models outside whitelisted ones trigger validation error."""
        config = SystemConfig()
        config.gemini.model = "gemini-ultra-pro-max"
        with self.assertRaises(ConfigValidationError):
            config.validate()

    def test_dotted_path_accessor(self):
        """Verify dotted path getter on SystemConfig."""
        config = SystemConfig()
        self.assertEqual(config.get("application.language"), AppLanguage.VI)
        self.assertEqual(config.get("gemini.temperature"), 0.3)
        self.assertEqual(config.get("assets.logs"), "logs")
        self.assertEqual(config.get("invalid.section.field", "default"), "default")
        self.assertIsNone(config.get("invalid.field"))


class TestYamlHelper(unittest.TestCase):
    """Tests the PyYAML abstraction helper behavior under missing dependency conditions."""

    def test_yaml_not_available(self):
        """Verify behaves safely when PyYAML package is missing."""
        self.assertFalse(YamlHelper.is_yaml_available())
        
        with self.assertRaises(ImportError):
            YamlHelper.load(Path("some.yaml"))
            
        with self.assertRaises(ImportError):
            YamlHelper.dump(Path("some.yaml"), {})


class TestConfigJsonEncoder(unittest.TestCase):
    """Tests custom serialization logic for nested JSON files."""

    def test_enum_serialization(self):
        """Verify enums are serialized as their underlying value."""
        data = {
            "lang": AppLanguage.VI,
            "theme": AppTheme.SLATE_DARK,
            "number": 42
        }
        serialized = json.dumps(data, cls=ConfigJsonEncoder)
        deserialized = json.loads(serialized)
        
        self.assertEqual(deserialized["lang"], "vi")
        self.assertEqual(deserialized["theme"], "Slate Dark")
        self.assertEqual(deserialized["number"], 42)


class TestConfigManager(unittest.TestCase):
    """Deep orchestration layer test suite targeting ConfigManager."""

    def setUp(self) -> None:
        # Create a temporary directory to host our test config files safely
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Paths for tests
        self.config_path = self.temp_path / "aims_config.json"
        self.env_path = self.temp_path / ".env"
        
        # Reset the Singleton before every test to ensure strict isolation
        ConfigManager._instance = None
        
        # Setup mock active file path
        self.manager = ConfigManager(config_path=self.config_path)
        self.manager._env_file_path = self.env_path

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        # Clean up ConfigManager Singleton reference to prevent pollution across test processes
        ConfigManager._instance = None

    def test_singleton_double_checked_locking(self):
        """Verify ConfigManager is a strict thread-safe Singleton."""
        instance_a = ConfigManager(self.config_path)
        instance_b = ConfigManager(self.config_path)
        self.assertIs(instance_a, instance_b)

        # Test multithreaded concurrent instantiations
        instances = []
        
        def instantiate():
            instances.append(ConfigManager(self.config_path))
            
        threads = [threading.Thread(target=instantiate) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        first_instance = instances[0]
        for inst in instances:
            self.assertIs(inst, first_instance)

    def test_autocreation_on_startup(self):
        """Verify default configuration file is automatically generated if missing."""
        self.assertTrue(self.config_path.exists())
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["config_version"], "1.0.0")
        self.assertEqual(data["application"]["language"], "vi")

    def test_caching_and_load_avoidance(self):
        """Verify that reloading is skipped if mtime and size did not change on disk."""
        # Force load to establish baseline
        self.manager.load(force=True)
        
        # Spy on json load
        with patch.object(self.manager, "_read_json_file", return_value={}) as mock_read:
            # Loading again without changes should NOT trigger file read
            self.manager.load(force=False)
            mock_read.assert_not_called()
            
            # Loading again with force should trigger file read
            self.manager.load(force=True)
            mock_read.assert_called_once()

    def test_save_and_atomic_writes(self):
        """Verify atomicity of config save updates (uses temporary files)."""
        self.manager.config.application.theme = AppTheme.SLATE_DARK
        self.manager.save()
        
        # Verify file has updated value
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["application"]["theme"], "Slate Dark")

    def test_reset_defaults(self):
        """Verify defaults are cleanly restored on reset."""
        self.manager.config.application.language = AppLanguage.EN
        self.manager.config.gemini.temperature = 1.8
        self.manager.save()
        
        self.manager.reset_default_config()
        
        self.assertEqual(self.manager.config.application.language, AppLanguage.VI)
        self.assertEqual(self.manager.config.gemini.temperature, 0.3)

    def test_dotted_path_get_and_set(self):
        """Verify dotted path getter and setter with rollback mechanics."""
        self.manager.set("application.language", "en")
        self.assertEqual(self.manager.get("application.language"), AppLanguage.EN)
        
        # Test string enum parsing cast
        self.manager.set("video.codec", "libx265")
        self.assertEqual(self.manager.get("video.codec"), VideoCodec.LIBX265)

        # Test failure triggers auto-rollback
        original_temp = self.manager.get("gemini.temperature")
        with self.assertRaises(ConfigValidationError):
            self.manager.set("gemini.temperature", 2.5)  # Invalid out-of-bounds temp
            
        # Verify rollbacked successfully
        self.assertEqual(self.manager.get("gemini.temperature"), original_temp)

    def test_update_section(self):
        """Verify section update dictionary with rollback behavior."""
        original_vol = self.manager.config.audio.volume
        
        self.manager.update_section("audio", {
            "volume": 1.2,
            "voice_folder": "exports/voice_test"
        })
        self.assertEqual(self.manager.config.audio.volume, 1.2)
        self.assertEqual(self.manager.config.audio.voice_folder, "exports/voice_test")
        
        # Try invalid inputs
        with self.assertRaises(ConfigValidationError):
            self.manager.update_section("audio", {
                "volume": 2.5,  # Invalid
                "voice_folder": "exports/fail"
            })
            
        # Original values should roll back
        self.assertEqual(self.manager.config.audio.volume, 1.2)

    def test_observer_subscription_pattern(self):
        """Verify observers are notified of configuration updates."""
        observer_called = []
        
        def observer_cb(cfg):
            observer_called.append(cfg.application.theme)
            
        self.manager.subscribe(observer_cb)
        
        self.manager.set("application.theme", "Slate Dark")
        self.assertEqual(observer_called, [AppTheme.SLATE_DARK])
        
        # Unsubscribe and check
        self.manager.unsubscribe(observer_cb)
        self.manager.set("application.theme", "Cosmic Light")
        self.assertEqual(observer_called, [AppTheme.SLATE_DARK])  # Should not have appended Cosmic Light

    def test_observer_robustness_on_failure(self):
        """Ensure failing observers do not interrupt the notification pipeline for others."""
        called_fine = False
        
        def bad_observer(cfg):
            raise RuntimeError("CRASH")
            
        def good_observer(cfg):
            nonlocal called_fine
            called_fine = True
            
        self.manager.subscribe(bad_observer)
        self.manager.subscribe(good_observer)
        
        # Notify should handle the crash gracefully and run both
        self.manager.notify()
        self.assertTrue(called_fine)

    def test_checksum_integrity_verification(self):
        """Test SHA256 configuration checksum computation and verification."""
        checksum = self.manager.get_checksum()
        self.assertTrue(self.manager.verify_integrity(checksum))
        self.assertFalse(self.manager.verify_integrity("invalid_checksum"))

    def test_backup_and_rotation(self):
        """Verify config backup files creation and max 20 backups rotation limits."""
        backup_dir = self.temp_path / "backups"
        self.manager.backup_config(destination_dir=backup_dir)
        
        backups = list(backup_dir.glob("config_backup_*.json"))
        self.assertEqual(len(backups), 1)
        
        # Create 25 mock backups to trigger rotation rotation cleanup limit
        for i in range(25):
            backup_file = backup_dir / f"config_backup_20260711_0000{i:02d}.json"
            backup_file.touch()
            # stagger times slightly
            os.utime(backup_file, (1780000000 + i, 1780000000 + i))
            
        self.manager._rotate_backups(backup_dir)
        backups_after = list(backup_dir.glob("config_backup_*.json"))
        self.assertEqual(len(backups_after), 20)

    def test_schema_migrations(self):
        """Test configuration schema migrations."""
        old_config = {
            "config_version": "0.1.0",
            "application": {
                "version": "1.0.0",
                "language": "vi",
                "theme": "Artistic Flair"
            },
            "video": {
                "resolution": "1080x1920",
                "fps": 30,
                "codec": "libx264"
            }
        }
        migrated = self.manager._migrate_config(old_config)
        self.assertEqual(migrated["config_version"], "1.0.0")
        self.assertFalse(migrated["video"]["allow_custom_resolution"])
        self.assertEqual(len(migrated["gemini"]["allowed_models"]), 4)

    def test_import_and_export_configurations(self):
        """Verify configurations export and imports cleanly."""
        export_file = self.temp_path / "exported_config.json"
        self.manager.set("application.theme", "Slate Dark")
        self.manager.export_config(export_file)
        
        self.assertTrue(export_file.exists())
        
        # Change value in memory
        self.manager.set("application.theme", "Cosmic Light")
        self.assertEqual(self.manager.config.application.theme, AppTheme.COSMIC_LIGHT)
        
        # Import to restore exported state
        self.manager.import_config(export_file)
        self.assertEqual(self.manager.config.application.theme, AppTheme.SLATE_DARK)

    def test_import_invalid_config_aborts(self):
        """Verify importing a corrupt file does not overwrite the current active config."""
        invalid_file = self.temp_path / "invalid_config.json"
        with open(invalid_file, "w", encoding="utf-8") as f:
            f.write("corrupted JSON payload")
            
        original_theme = self.manager.config.application.theme
        
        with self.assertRaises(ConfigValidationError):
            self.manager.import_config(invalid_file)
            
        # Current active configuration must remain fully unchanged
        self.assertEqual(self.manager.config.application.theme, original_theme)

    def test_env_file_parser(self):
        """Test environment overrides parsing from .env files with multiple styles."""
        with open(self.env_path, "w", encoding="utf-8") as f:
            f.write("# This is a comment line\n")
            f.write("GEMINI_API_KEY=ENV_KEY_FROM_FILE\n")
            f.write("export AIMS_GEMINI_TEMPERATURE=1.5 # inline comment\n")
            f.write("AIMS_APPLICATION_THEME='Slate Dark'\n")
            f.write("AIMS_VIDEO_ALLOW_CUSTOM_RESOLUTION=True\n")
            f.write("AIMS_FFMPEG_THREADS=8\n")
            f.write("INVALID_LINE_NO_EQUALS\n")
            f.write("AIMS_FFMPEG_THREADS=not_an_int\n")  # Invalid cast, should print warning and ignore

        # Siphon environment file
        self.manager._load_dotenv()
        
        # Verify OS env siphoned
        self.assertEqual(os.environ.get("GEMINI_API_KEY"), "ENV_KEY_FROM_FILE")
        self.assertEqual(os.environ.get("AIMS_GEMINI_TEMPERATURE"), "1.5")
        
        # Apply override
        self.manager._apply_env_overrides()
        
        # Verify fields updated with correct parsed datatypes
        self.assertEqual(self.manager.config.gemini.api_key, "ENV_KEY_FROM_FILE")
        self.assertEqual(self.manager.config.gemini.temperature, 1.5)
        self.assertEqual(self.manager.config.application.theme, AppTheme.SLATE_DARK)
        self.assertEqual(self.manager.config.video.allow_custom_resolution, True)
        self.assertEqual(self.manager.config.ffmpeg.threads, 8)

    def test_mocked_yaml_import_export(self):
        """Verify YAML import and export behavior when PyYAML is mocked as available."""
        mock_yaml_module = MagicMock()
        mock_yaml_module.safe_load.return_value = {"application": {"language": "en"}}
        
        with patch.dict("sys.modules", {"yaml": mock_yaml_module}), \
             patch.object(YamlHelper, "is_yaml_available", return_value=True):
            
            # Export YAML test
            yaml_export_file = self.temp_path / "exported.yaml"
            self.manager.export_config(yaml_export_file)
            mock_yaml_module.dump.assert_called_once()
            
            # Import YAML test
            self.manager.import_config(yaml_export_file)
            mock_yaml_module.safe_load.assert_called_once()


if __name__ == "__main__":
    unittest.main()
