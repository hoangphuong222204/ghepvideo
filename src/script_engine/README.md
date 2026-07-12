# Module 05: AI Script Engine

The `src/script_engine` package constitutes the core copywriter, optimization, and business intelligence module of **AI Marketing Studio PRO**. 

Designed to process product briefs, run deep category/audience reviews, generate customized short-form video scripts (ranging from 1 to 50 items), and optimize speaking flows for high-retention vertical channels (TikTok, Shopee, Reels, Shorts), it guarantees flawless delivery without ever communicating with external AI backends directly.

All generative prompts go securely through **Module 04 (AI Gateway)**.

---

## Directory Structure

```text
src/script_engine/
├── __init__.py             # Public exports mapping
├── script_engine.py        # Central unified facade for FastAPI/NiceGUI
├── script_manager.py       # Batch pipeline manager & quality self-correction retries
├── analyzer.py             # Heuristic text length & keyword detection analyzer
├── product_analyzer.py     # AI audience/persona and motivated scenario scanner
├── policy_checker.py       # Sensitive term flags & automatic soft rewritings
├── pronunciation_adapter.py# English word converter for natural Vietnamese reading rhythm
├── number_converter.py     # High-precision digits-to-words Vietnamese numbers expander
├── prompt_generator.py     # Prompt compiler enforcing JSON output schemas
├── style_selector.py       # 14 Short-form styles guides registry
├── duration_estimator.py   # Words-to-Seconds speaker pacing estimation
├── quality_checker.py      # Hook, Selling, Pacing, Compliance multi-metric scoring
├── json_parser.py          # Decoders transforming raw text responses to models
├── models.py               # Typed Dataclasses structures (VideoScript, ScriptRequest)
├── validators.py           # Request validations and quantitive constraints
├── exceptions.py           # Custom exception hierarchy (QualityError, PolicyError)
├── constants.py            # Styles list, reading rates, phonetic dictionaries
└── README.md               # Package documentation (this file)
```

---

## Supported Copywriting Styles

The engine supports **14 distinct short-form styles**:

| Style | Tone & Layout |
| :--- | :--- |
| **Problem Solution** | Classic hook on problem -> product as solution -> Call to Action (CTA). |
| **Review** | Genuine unpacking, objective pros/cons lists, texture/finish focus. |
| **Native Review** | Highly subtle, organic personal tips without sounding salesy. |
| **POV** | First-person scenario setup where the viewer feels involved instantly. |
| **Luxury** | Elevated vocabulary, slower pace, exclusivity and craftsmanship focus. |
| **ASMR** | Micro-visual sound emphasis, sparse words, high sensorial pacing. |
| **Comparison** | Product features versus standard market alternatives side-by-side. |
| **Storytelling** | Setting up character arcs, conflicts, and dramatic resolution via product. |
| **Lifestyle** | Integrating products seamlessly into normal aesthetic day-in-the-life routines. |
| **Emotional** | Family, warmth, personal journeys, slow deep cadence. |
| **Expert** | Clinical trials, technical terms, statistics, high authority setup. |
| **Funny** | Memes, comedy angles, unexpected twists, highly relatable humor. |
| **Premium** | Sleek design, smart features, and high efficiency highlight. |
| **Minimal** | Ultra-short phrases, crisp negative space, messaging focus. |

---

## Key Features

### 1. Vietnamese Speech Optimization
To assist Text-to-Speech (TTS) models and voiceover artists in maintaining an impeccable reading rhythm:
- **Number Expansion:** Translates numerical digits (`100` -> `một trăm`, `250000` -> `hai trăm năm mươi nghìn`) so the script counts correct words and measures accurate speaking seconds.
- **English Pronunciation Adaptation:** Maps technical/branding terms case-insensitively (`tiktok` -> `tíc-tóc`, `sale` -> `seo`, `serum` -> `xi-rum`) to Vietnamese phonetics.

### 2. Platform Policy Checking
Proactively protects campaigns from bans or shadowbans by scanning against platform guidelines (such as TikTok Shop policies).
- Identifies aggressive or sensitive claims (e.g., `cam kết 100%`, `trị dứt điểm`).
- Automatically rewrites them to safe, compliant alternatives (`mang lại trải nghiệm tối ưu`, `hỗ trợ cải thiện rõ rệt`) without interrupting generation flows.

### 3. Duration Estimation & Word Count Validation
Calculates speech pacing precisely at **150 Words Per Minute (WPM)** for natural Vietnamese delivery. It ensures all generated script segments fit within the requested duration budget.

### 4. Multi-Metric Quality Checker
Each script is scored from `0.0` to `100.0` using a weighted metric suite:
- **Hook Score (20%):** Assesses if the opening scene hooks attention under 3 seconds.
- **Selling Score (20%):** Validates benefits highlights and clear Call to Action (CTA).
- **Natural Speech Score (15%):** Assesses rhythmic variation, flow, and sentence breaks.
- **Policy Score (25%):** Checks for safe term adherence.
- **Duration Score (10%):** Measures deviation from target length.
- **Originality Score (10%):** Compares Jaccard similarity across batch scripts to ensure **No Duplicate Styles** or content.

### 5. Auto-Correction & Self-Healing Loop
If a generated script falls below the required `min_quality_score` (default `70.0`), the engine retains it as a fallback but automatically issues up to **2 rewrite prompts** to the AI Gateway, passing detailed scoring feedback to let the model self-correct.

---

## Integration Details

- **Module 01 Config Manager:** Handled by AIManager internally.
- **Module 02 Logger System:** Comprehensive log traces on analytics and pipeline steps.
- **Module 03 Database Layer:** When a `campaign_id` is passed, scripts are written as structured `MarketingAsset` models in SQLite, and completion summaries are logged in `AuditLog` via thread-safe SQLAlchemy Units of Work.
- **Module 04 AI Gateway:** Resolves and targets the appropriate models, calling `generate`/`generate_async` under the hood.

---

## Code Example

```python
from src.script_engine import ScriptEngine, ScriptRequest

engine = ScriptEngine()

request = ScriptRequest(
    product_name="Serum Căng Bóng SkinRenew",
    product_description="Serum dưỡng ẩm sâu chứa Hyaluronic Acid và Vitamin C giúp căng bóng tức thì và mờ thâm mụn.",
    brand_name="SkinRenew",
    style="Problem Solution",
    duration_seconds=45,
    quantity=3, # Generates 3 scripts with different, non-duplicate styles!
    campaign_id=12,
    min_quality_score=75.0
)

# Run batch generation (async available with await engine.generate_scripts_async)
scripts = engine.generate_scripts(request)

for script in scripts:
    print(f"[{script.style}] {script.title} (Score: {script.overall_score})")
    print(f"Duration: {script.estimated_duration}s | Words: {script.word_count}")
    print("--- SCENES ---")
    for scene in script.scenes:
        print(f"Scene {scene.scene_number} ({scene.duration_seconds}s): {scene.spoken_text}")
```
