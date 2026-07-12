# AI Marketing Studio PRO - Configuration System Package

An enterprise-grade, thread-safe, validated configuration management engine built specifically for **AI Marketing Studio PRO**.

---

## 🛠 Project Structure

The configuration module is contained within a self-sufficient package:

```text
src/
└── config/
    ├── __init__.py           # Package entrypoint and clean import aliases
    ├── config_manager.py     # Singleton thread-safe controller managing IO pipelines
    ├── config_models.py      # Declarative and typed configuration category models (dataclasses)
    ├── validators.py         # Dynamic boundary-checking rules (temperatures, frame rates, path suffixes)
    ├── exceptions.py         # Custom professional error hierarchy for clean exception handling
    ├── default_config.json   # Template JSON config file 
    └── README.md             # This document
```

---

## 🌟 Key Features

1. **Singleton Pattern**: Instantiated once system-wide via double-checked thread-safe locks.
2. **Cascading Validation**: Each dataclass has self-auditing boundary checks ensuring bad parameters (like negative frames or out-of-bounds temperatures) are rejected early.
3. **Multi-Source Configuration**:
   - Standard defaults.
   - External JSON/YAML config files.
   - Sourcing parameters from local `.env` files.
   - Dynamic operating-system level environment variables with prefixed matching `AIMS_`.
4. **Auto-Directory Provisioning**: Automatically verifies and creates folder directories on disk as specified in settings.
5. **Robust State Safeguards**: Complete backups, restores, exports, imports, and state-reloading capabilities.
6. **Extensible Architecture**: Fully type-hinted and structured to natively accommodate future YAML additions.

---

## 🚀 Code Examples

### 1. Basic Initialization & Configuration Access

```python
from src.config import ConfigManager

# Instantiate the thread-safe configuration singleton
config_manager = ConfigManager()

# Access active configurations
app_version = config_manager.config.application.version
gemini_model = config_manager.config.gemini.model
output_folder = config_manager.config.assets.output

print(f"Running AIMS Pro version: {app_version}")
```

### 2. Sourcing Environment Overrides

You can set values either inside a `.env` file or directly inside your active terminal process:

```bash
# Sourcing environment file values
export GEMINI_API_KEY="my-secret-gemini-key"
export AIMS_GEMINI_MODEL="gemini-1.5-pro"
export AIMS_VIDEO_FPS=60
```

The system will auto-apply these values on load and correctly typecast them (e.g., `AIMS_VIDEO_FPS` will be parsed as an integer value `60`).

### 3. Slicing-Updates & Modifying Values Programmatically

You can update single properties safely. The manager validates changes automatically and saves them to disk:

```python
from src.config import ConfigManager, ConfigValidationError

config_manager = ConfigManager()

try:
    # Update properties in a specific section
    config_manager.update_section("gemini", {
        "temperature": 0.7,
        "max_tokens": 2048
    })
except ConfigValidationError as e:
    print(f"Validation failed: {e}")
```

### 4. Backup & Restore Lifecycles

```python
from src.config import ConfigManager

config_manager = ConfigManager()

# Create a backup
backup_filepath = config_manager.backup_config()
print(f"Backup created at: {backup_filepath}")

# Revert back to original factory defaults
config_manager.reset_default_config()

# Reload config state manually
config_manager.reload()
```

---

## 🔒 Configuration Spec Fields

| Field Category | Key | Datatype | Standard Default |
| :--- | :--- | :--- | :--- |
| **Application** | `version` | string | `1.0.0` |
| | `language` | string (vi, en) | `vi` |
| | `theme` | string | `Artistic Flair` |
| **Gemini** | `api_key` | string | `MY_GEMINI_API_KEY` |
| | `model` | string | `gemini-3.5-flash` |
| | `temperature` | float [0.0 - 2.0] | `0.3` |
| | `top_p` | float [0.0 - 1.0] | `0.95` |
| | `max_tokens` | integer | `4096` |
| **Fish Speech** | `model_path` | string | `models/fish_speech_v1` |
| | `device` | string | `cuda` |
| | `sample_rate` | integer | `44100` |
| | `output_folder` | string | `exports/audio` |
| **FFmpeg** | `executable` | string | `bin/ffmpeg.exe` |
| | `threads` | integer [1 - 128] | `4` |
| | `preset` | string | `medium` |
| **Video** | `resolution` | string (`{W}x{H}`) | `1080x1920` |
| | `fps` | integer [1 - 120] | `30` |
| | `codec` | string | `libx264` |
| | `crf` | integer [0 - 51] | `23` |
| **Audio** | `music_folder` | string | `assets/audio_templates` |
| | `voice_folder` | string | `exports/voice` |
| | `volume` | float [0.0 - 2.0] | `0.8` |
| **Database** | `sqlite_path` | string | `database.db` |
| | `backup_folder` | string | `backups` |
| **Assets** | `input` | string | `assets/input` |
| | `output` | string | `exports` |
| | `temp` | string | `temp` |
| | `logs` | string | `logs` |
| | `cache` | string | `cache` |
| | `resources` | string | `resources` |
| | `plugins` | string | `plugins` |
