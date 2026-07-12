# AI Marketing Studio PRO: Enterprise Desktop Application Architecture & Project Structure Specification
**Document Code:** AIMS-PRO-PSS-002  
**Version:** 1.0.0-Draft  
**Author:** Principal Software Architect  
**Status:** Approved for Engineering & System Bootstrapping  

---

## Table of Contents
1. [Executive Architectural Summary](#1-executive-architectural-summary)
2. [Unified Technical Stack](#2-unified-technical-stack)
3. [Enterprise Project Directory Tree](#3-enterprise-project-directory-tree)
4. [Folder-by-Folder Architectural Breakdown](#4-folder-by-folder-architectural-breakdown)
5. [Dependency Rules & Inter-Module Communication](#5-dependency-rules---inter-module-communication)
6. [Enterprise Coding Standards & Naming Conventions](#6-enterprise-coding-standards---naming-conventions)
7. [Comprehensive Module Design Specifications](#7-comprehensive-module-design-specifications)
8. [Cross-Platform (Windows-First) Packaging Strategy](#8-cross-platform-windows-first-packaging-strategy)
9. [Operational & Cross-Cutting Strategies](#9-operational---cross-cutting-strategies)
10. [Plugin & Modular Expansion Strategy](#10-plugin---modular-expansion-strategy)

---

## 1. Executive Architectural Summary

**AI Marketing Studio PRO** is a highly optimized, professional desktop application designed to run locally on creators' computers, with a "Free-First" architecture. 

To achieve professional-grade desktop performance with dynamic web technologies, the application employs a **Hybrid Client-Server Desktop Monolith** architecture:
*   **The Backend (Local Core API Server):** Built using **Python 3.11+** and **FastAPI**, serving as the high-throughput local engine managing system processes (FFmpeg, OpenCV), local database storage (SQLite), and external APIs (Google Gemini, Local Fish Speech server).
*   **The Frontend (Adaptive Web UI Framework):** Built using **NiceGUI**, driving a responsive, elegant, modern dashboard that renders seamlessly inside a native PyWebView or system browser wrapper. NiceGUI interacts with the FastAPI backend via high-speed asynchronous websockets and local loopback API requests.

### Core Architectural Principles
1.  **Local-First & Resource-Safe:** Heavy processing (such as image filtering, video rendering with FFmpeg, and database queries) must prioritize local CPU/GPU execution without locking the primary user interface thread.
2.  **Strict Layer Separation:** The visual interface layer (NiceGUI views) must never contain direct business logic, SQL queries, or file I/O operations. It communicates exclusively with the controller layer via asynchronous service calls.
3.  **Single-Request AI Optimizations:** The cloud-facing AI script generator (Gemini) must only be called once per pipeline run. All structural segmentation, phonetic vietnamese sanitizations, and layout formatting are managed locally.
4.  **Plugin-Driven Extensibility:** All future features (e.g., automated Shopee/TikTok publishing, background removal models, and proprietary local image generator layers) must register as self-contained plugins that hook into defined abstract lifecycles.

---

## 2. Unified Technical Stack

| System Layer | Technology | Reason for Selection |
| :--- | :--- | :--- |
| **Language Runtime** | Python 3.11+ | Native library support for OpenCV, AI wrappers, subprocess control, and fast enterprise prototyping. |
| **UI Presentation** | NiceGUI + Tailwind CSS | Eliminates electron/node_modules overhead, offers rich Python-native reactive binding, and is easily styled with custom Tailwind themes. |
| **Local Web Server**| FastAPI + Uvicorn | High-performance ASGI server supporting asynchronous task queues, native Pydantic typing, and automatic OpenAPI generation. |
| **Local Database**   | SQLite + SQLAlchemy (Async) | Zero-configuration, file-based database capable of handling rich relational structures, history logs, and preset libraries locally. |
| **AI Script Layer**  | Google Gemini API (`@google/genai`) | Low latency, deep Vietnamese vocabulary, and cost-effective structured JSON schema enforcement. |
| **TTS Synthesis**    | Fish Speech Engine (Local REST API) | Industry-leading Vietnamese voice cloning that runs offline on consumer-grade gaming GPUs or CPU threads. |
| **Video Compositor** | FFmpeg (Local Subprocess) | Low-level, high-speed, zero-cost video stitching, subtitle burning, and multi-channel audio mixing. |
| **Image Engine**     | OpenCV & Pillow | Fast pixel-level cropping, keyframe extraction, watermark analysis, and video aspect-ratio conversions. |
| **Local Packaging**  | PyInstaller + Briefcase | Standardizes compilation into a self-contained `.exe` binary package for Windows platforms, embedding FFmpeg binaries safely. |

---

## 3. Enterprise Project Directory Tree

The directory tree is structured with strict separation of concerns. The code resides within a root namespace called `src/` to prevent top-level pollution.

```
/aims_pro_desktop/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml
├── SCRIPT_ENGINE_SPEC.md
├── PROJECT_STRUCTURE_SPEC.md
├── requirements.txt
├── setup.py
├── main.py                         # Single application entry point (Boots Backend + UI)
├── database.db                     # Local SQLite database instance (created on first run)
├── assets/                         # Global, non-compiled application static assets
│   ├── brand/                      # Corporate identity icons, logos, splashscreens
│   ├── audio_templates/            # Default license-free background audio beats (.mp3)
│   └── video_templates/            # Vertical 9:16 video clips, transitions, intro elements
├── src/                            # Monolithic Root Application Source Directory
│   ├── __init__.py
│   ├── config.py                   # High-level config and environment variable parser
│   │
│   ├── core/                       # Core system mechanics (Internal mechanics, no domain logic)
│   │   ├── __init__.py
│   │   ├── database/               # Relational engine initialization & connection pool
│   │   │   ├── __init__.py
│   │   │   ├── connection.py       # SQLAlchemy async engine configuration
│   │   │   └── base.py             # Declarative SQLAlchemy base for model inheritance
│   │   ├── logger/                 # Enterprise rotating logging config
│   │   │   ├── __init__.py
│   │   │   └── formatter.py
│   │   ├── cache/                  # In-memory LRU and SQLite-backed caching
│   │   │   ├── __init__.py
│   │   │   └── manager.py
│   │   └── security/               # Local user key encryption and hardware licensing
│   │       ├── __init__.py
│   │       └── license.py
│   │
│   ├── db/                         # Database migrations and physical tables
│   │   ├── __init__.py
│   │   ├── models.py               # ORM entity representations (Product, Script, Logs)
│   │   └── migrations/             # Alembic auto-generated schema history scripts
│   │
│   ├── models/                     # Shared immutable validation schemas (Pydantic / Domain models)
│   │   ├── __init__.py
│   │   ├── script.py               # Pydantic schemas representing the Script payload
│   │   ├── product.py              # Pydantic schemas for ingest parameters
│   │   └── settings.py             # User local app configuration settings schemas
│   │
│   ├── services/                   # Pure business logic layer (All operations executed here)
│   │   ├── __init__.py
│   │   ├── ai/                     # Gemini API orchestrators
│   │   │   ├── __init__.py
│   │   │   └── script_generator.py # Formulates requests to Gemini, handles structured responses
│   │   ├── tts/                    # Voice engine integrations
│   │   │   ├── __init__.py
│   │   │   ├── speech_synthesizer.py # Translates raw text to audio files (Fish Speech)
│   │   │   └── normalizer.py       # Converts numbers to words & phoneticizes English terms
│   │   ├── video/                  # Frame compositor & FFmpeg operators
│   │   │   ├── __init__.py
│   │   │   ├── ffmpeg_operator.py  # Builds shell command structures, runs subprocesses safely
│   │   │   └── cv_analyzer.py      # Uses OpenCV to inspect framerates, crops, and keyframes
│   │   ├── policy/                 # Compliance scanner and claim filter
│   │   │   ├── __init__.py
│   │   │   └── compliance.py       # Local regex-based claims pre-scanner and safety scoring
│   │   └── project/                # Handles local project directories and JSON exports
│   │       ├── __init__.py
│   │       └── workspace.py
│   │
│   ├── ui/                         # Presentation Layer (NiceGUI views & component rendering)
│   │   ├── __init__.py
│   │   ├── theme/                  # Theme configuration, visual styles, palette configs
│   │   │   ├── __init__.py
│   │   │   └── colors.py           # Brand color parameters (Artistic Flair theme configs)
│   │   ├── layouts/                # Structural templates (Navigation Rail, Main Layout)
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   └── header.py
│   │   ├── components/             # Reusable UI widgets
│   │   │   ├── __init__.py
│   │   │   ├── timeline_widget.py
│   │   │   ├── settings_dialog.py
│   │   │   └── terminal_logs.py
│   │   └── views/                  # Primary screen containers
│   │       ├── __init__.py
│   │       ├── dashboard.py        # Central dashboard container view
│   │       ├── script_editor.py    # Text editor, phonetic settings view
│   │       └── media_composer.py   # FFmpeg visual composition view
│   │
│   ├── plugins/                    # Expandable feature registration hooks
│   │   ├── __init__.py
│   │   ├── base_plugin.py          # Abstract Base Class containing plugin lifecycle hooks
│   │   └── custom/                 # Placeholders for future third-party integrations
│   │       └── __init__.py
│   │
│   └── api/                        # REST endpoint layer routing calls to Service Layer
│       ├── __init__.py
│       ├── router.py               # Master API router aggregating modular handlers
│       ├── endpoints/
│       │   ├── __init__.py
│       │   ├── scripts.py
│       │   ├── voice.py
│       │   └── video.py
│       └── middleware/
│           ├── __init__.py
│           └── errors.py           # Global FastAPI exception handlers
│
├── tests/                          # Automated suite (replicates structure of src/)
│   ├── __init__.py
│   ├── conftest.py                # PyTest global fixtures and mock database settings
│   ├── unit/                       # Low-level logic checks
│   │   ├── test_normalizer.py      # Validates English-to-Vietnamese conversion cases
│   │   ├── test_compliance.py      # Checks policy claim blocking regex
│   │   └── test_script_pydantic.py
│   └── integration/                # High-level pipeline coupling tests
│       ├── test_gemini_mock.py     # Simulates mock responses for pipeline tests
│       └── test_ffmpeg_subprocess.py
│
└── docs/                           # Internal technical documentation
    ├── architecture_overview.md
    ├── dev_setup.md
    └── fish_speech_handshake.md
```

---

## 4. Folder-by-Folder Architectural Breakdown

### 4.1 Root Level Files
*   `main.py`: **Single Responsibility:** Initialize and start the application. Instantiates the SQLite database (creating tables if absent), mounts the FastAPI router with CORS middleware, initializes the NiceGUI web server, and opens a local webview container for desktop execution.
    *   *What belongs:* Initialization code, dev server configurations, event loop configurations.
    *   *What NEVER belongs:* Complex API endpoints, direct raw HTML styling strings, or low-level file manipulations.

### 4.2 `src/core/`
*   **Single Responsibility:** Provide infrastructure utilities that are domain-agnostic. Modules here should be reusable in completely different software projects.
*   *Allowed Files:* Async database pools, low-level in-memory cache definitions, logging formatters, custom cryptography wrappers for local license key validation.
*   *Forbidden Files:* Business models (e.g., `ProductModel`), API routes (e.g., `/api/generate`), or presentation elements.

### 4.3 `src/db/`
*   **Single Responsibility:** Store ORM entities and handle migrations.
*   *Allowed Files:* Declarative models mapping to SQLite tables, Alembic migration scripts.
*   *Forbidden Files:* Pydantic schemas (use `src/models/` for that), presentation states, or API serializers.

### 4.4 `src/models/`
*   **Single Responsibility:** Contain shared, immutable Pydantic models for request/response serialization, API validation, and local setting files.
*   *Allowed Files:* Pydantic models representing ingest parameters, validated script structures, voice configuration settings, and FFmpeg render params.
*   *Forbidden Files:* SQLAlchemy ORM database models, view templates, or functions containing database queries or API logic.

### 4.5 `src/services/`
*   **Single Responsibility:** Drive the business logic of the app. Every user action (generating a script, rendering audio, stitching video) must execute inside a dedicated service.
*   *Allowed Files:* Gemini API connectors, Fish Speech REST API handlers, Vietnamese text normalizers, FFmpeg command builders, OpenCV frame manipulators.
*   *Forbidden Files:* Directly importing NiceGUI elements, creating UI dialog boxes, or writing raw REST API endpoint paths.

### 4.6 `src/ui/`
*   **Single Responsibility:** Handle the visual representation and layout controls using NiceGUI and Tailwind.
*   *Allowed Files:* View routers, custom UI components, color palette maps, layout headers, and client-side page configurations.
*   *Forbidden Files:* Raw database transactions (SQL/SQLAlchemy), writing to process log files directly, or calling external APIs directly without going through a service or API client.

### 4.7 `src/plugins/`
*   **Single Responsibility:** Define the abstract plugin interface and store optional dynamically-loaded feature extensions.
*   *Allowed Files:* Abstract base class for plugins (`base_plugin.py`), individual subdirectory hooks for dynamic features (e.g., automated social publishers).
*   *Forbidden Files:* Unintegrated, random third-party script fragments or general application utility wrappers.

### 4.8 `src/api/`
*   **Single Responsibility:** Map HTTP requests to Python service executions and manage API exceptions.
*   *Allowed Files:* FastAPI endpoint routers, parameter validation controllers, error middlewares.
*   *Forbidden Files:* View layouts or heavy business logic algorithms (defer directly to services).

---

## 5. Dependency Rules & Inter-Module Communication

To guarantee that modules remain independent, reusable, and easy to refactor, the application enforces a **Strict Unidirectional Layered Dependency Constraint**:

```
+-------------------------------------------------------------+
|                      ui (NiceGUI Views)                     |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     api (FastAPI Routes)                    |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     services (Business)                     |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     core / db / models                      |
+-------------------------------------------------------------+
```

### 5.1 Communication Laws
1.  **Strict Isolation of UI:** UI code (`src/ui/`) may import services (`src/services/`) and validation models (`src/models/`). It is **STRICTLY FORBIDDEN** for services or database modules to import UI components. This prevents circular dependency locks and allows running services headless (e.g., in a background CLI worker).
2.  **Service-Centric APIs:** API routes (`src/api/`) serve as lightweight gateways. They receive Pydantic request models, pass them to services, receive structured responses, and return them. No SQL transactions or heavy processing should live inside API routes.
3.  **Data Transferred via Pydantic:** Data moving between layers (e.g., from service to UI) must be converted into strict Pydantic model representation rather than returning raw database ORM objects. This ensures that database session changes never trigger serialization errors in downstream layers.
4.  **No Circular Imports:** If two services depend on each other, they must communicate via event emitters, shared callbacks, or be unified into a single orchestrator service.

---

## 6. Enterprise Coding Standards & Naming Conventions

All developers contributing to AI Marketing Studio PRO must write code compliant with the following stylistic rules:

### 6.1 General Styling & Structure
*   **Compliance:** Code must strictly comply with **PEP 8** style guidelines.
*   **Static Typing:** All function declarations **MUST** define strict type hints for arguments and return structures:
    ```python
    # Bad Code
    def process_script(script_data):
        return script_data.get("text")

    # Good Code
    def process_script(script: MarketingScript) -> str:
        return script.tts_text
    ```
*   **Docstrings:** Every module, class, and public function must feature a clear Google-style docstring explaining its behavior, parameters, and raised exceptions.

### 6.2 Naming Protocol Table

| Object Type | Naming Rule | Example |
| :--- | :--- | :--- |
| **Modules / Files** | `snake_case` | `speech_normalizer.py` |
| **Classes** | `PascalCase` | `FishSpeechSynthesizer` |
| **Functions / Methods**| `snake_case` | `phoneticize_english_terms()` |
| **Constants** | `UPPER_SNAKE_CASE` | `VIETNAMESE_SYLLABLE_RATE` |
| **Variables / Arguments**| `snake_case` | `product_description` |
| **DB Models** | `PascalCase` suffixing `Model` | `ProductModel` |
| **Pydantic Schemas** | `PascalCase` suffixing `Schema`| `ProductIngestSchema` |

---

## 7. Comprehensive Module Design Specifications

### 7.1 Text Normalization and Phone-Tuning Engine
Located in `src/services/tts/normalizer.py`, this module ensures that the script text reads naturally when converted to speech.

```
[Raw English Text] --> [Regex Matcher] --> [Phonetic Dictionary] --> [Vietnamese Phonetics]
```

*   **Sub-modules:**
    1.  `NumberConverter`: Scans text for digits and replaces them with fully expanded Vietnamese words. Handles currency symbols, decimals, and fractional notations (e.g., "1.5L" $\rightarrow$ "một lít rưỡi").
    2.  `Phoneticizer`: Evaluates and replaces registered English and technical terms with natural Vietnamese approximations (e.g., "WiFi" $\rightarrow$ "Quai phai").
*   **Inputs:** `raw_text: str`
*   **Outputs:** `tts_optimized_text: str`

### 7.2 TikTok Policy & Compliance Guard
Located in `src/services/policy/compliance.py`, this module analyzes scripts for risk before they are finalized.
*   **Mechanism:** Runs a lightweight local regex dictionary containing blacklisted words/phrases across high-risk categories (Cosmetics, Health, Financials).
*   **Risk Scoring:** Computes a compliance risk rating. If the rating exceeds threshold limits, the engine alerts the user and proposes safe alternatives.
*   **Inputs:** `generated_script_text: str`
*   **Outputs:** `compliance_report: dict` containing `is_safe: bool`, `violation_phrases: List[str]`, and `suggested_replacements: dict`.

### 7.3 FFmpeg Video Composer & CV Analyzer
Located in `src/services/video/ffmpeg_operator.py` and `cv_analyzer.py`, this module manages local media rendering operations.
*   **Mechanism:** Spawns a platform-independent subprocess running local FFmpeg binaries. It stitches template background clips, merges synthesized voice tracks, overlays ambient background music, and burns in high-contrast stylized subtitle text.
*   **CV Analyzer:** Inspects uploaded source video assets to extract metadata, detect aspect ratio, determine average framerate, and ensure video complies with short-form 9:16 portrait constraints.
*   **Inputs:** `render_instructions: ScriptRenderSchema`, `bg_video_path: Path`, `audio_path: Path`
*   **Outputs:** `output_video_path: Path`, `render_logs: str`

---

## 8. Cross-Platform (Windows-First) Packaging Strategy

Since the primary target environment is Windows desktop systems, the packaging architecture is built to ensure a robust, isolated local runtime experience:

*   **Executable Compilation:** The application is packaged into a standalone `.exe` using **PyInstaller** or **Briefcase**.
*   **Embedded Runtime Binaries:** To guarantee zero external dependencies for the user, custom build scripts bundle target-platform-specific compiled binaries directly inside the package:
    *   `bin/ffmpeg.exe` and `bin/ffprobe.exe`
    *   Embedded portable **SQLite** driver DLLs.
*   **Resource Management:** App data, local user settings, database instances, and generated video files must never write directly inside the executable's installation folder (which requires administrator privileges). Instead, the application must write to user-space folders:
    *   Windows: `%USERPROFILE%/AppData/Local/AIMarketingStudioPro/`
    *   macOS: `~/Library/Application Support/AIMarketingStudioPro/`
    *   Linux: `~/.config/aimarketingstudiopro/`

---

## 9. Operational & Cross-Cutting Strategies

### 9.1 Database Management
*   **Engine:** SQLite file located at `%USERPROFILE%/AppData/Local/AIMarketingStudioPro/database.db`.
*   **ORM Integration:** SQL Alchemy asynchronous connection loop handling concurrent operations safely.
*   **Schema Evolution:** Managed with **Alembic** migrations to safely upgrade the local database structure on update without losing historical user project logs.

### 9.2 Rotating File Logging
*   **Configuration:** The local system rotates logs automatically, writing to `logs/aims_pro.log`.
*   **Retention Policy:** Keeps a maximum of 5 files up to 10MB each.
*   **Log Level Configuration:**
    *   `INFO`: Standard events (e.g., successful API calls, startup handshakes, rendering completions).
    *   `WARN`: Non-blocking irregularities (e.g., slow response from local Fish Speech server, compliance claim flag).
    *   `ERROR`: Pipeline failures requiring immediate user intervention (e.g., missing Gemini API key, missing FFmpeg binary, malformed JSON).

### 9.3 In-Memory and SQLite-Backed Caching
*   **API Response Caching:** To minimize API token usage, responses to identical inputs (identical product profiles, parameters, and style targets) are cached in SQLite with a configurable TTL (Time-To-Live).
*   **Asset Buffering:** Background music tracks, transition templates, and voice prompt models are loaded into an in-memory LRU (Least Recently Used) cache during active user editing sessions.

---

## 10. Plugin & Modular Expansion Strategy

To allow AI Marketing Studio PRO to expand seamlessly, the application implements a dynamic, self-loading plugin system.

```
[Plugin Loader Service] --> [Scans src/plugins/custom/] --> [Loads Custom Modules] --> [Appends UI & APIs]
```

### 10.1 Abstract Plugin Specification
All plugin packages must extend the `BasePlugin` abstract class found in `src/plugins/base_plugin.py`:

```python
# Reference abstract class specification (Conceptual model, do not write implementation)
class BasePlugin(ABC):
    @abstractmethod
    def register_endpoints(self, app: FastAPI) -> None:
        """Register custom API routes within the core backend app."""
        pass

    @abstractmethod
    def inject_ui_elements(self) -> None:
        """Dynamically add custom menus, buttons, or views to NiceGUI layout."""
        pass

    @abstractmethod
    def on_startup(self) -> None:
        """Execute custom startup validation checks, hardware connections, etc."""
        pass
```

### 10.2 Future Native Plugins Roadmap
*   **Nano Banana Visualizer:** Dynamic AI-powered product shot generator and canvas editor.
*   **Background Remover Engine:** Local U2Net or RMBG machine learning model run on CPU threads.
*   **Viral Publisher Core:** Direct API integrations to authenticate accounts and upload rendered video packages to TikTok Shop, Shopee, and Facebook Reels.

---
*End of Engineering Specification Document.*  
*AI Marketing Studio PRO - Standardizing Professional, Modular, Local-First Python Desktop Software Architecture.*
