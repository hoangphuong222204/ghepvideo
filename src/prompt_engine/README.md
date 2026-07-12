# Module 06: Enterprise Prompt Engine

The **Prompt Engine** is the specialized business intelligence layer of **AI Marketing Studio PRO** responsible for the configuration, validation, rendering, versioning, split A/B testing, and token optimization of AI prompts.

---

## 🏗️ Architecture & Component Design

The module is structured as follows:

```text
src/prompt_engine/
├── __init__.py               # Package public exports
├── prompt_engine.py         # Unified high-level Facade
├── prompt_manager.py        # Central pipeline orchestrator
├── prompt_builder.py        # Dynamic query generator
├── prompt_renderer.py       # Jinja2-based template rendering engine
├── prompt_validator.py      # Input, provider boundary, and injection guards
├── prompt_optimizer.py      # Whitespace and lexical token-reduction compression
├── prompt_templates.py      # Preloaded system defaults registry
├── template_loader.py       # Deserializer & serializer for JSON structures
├── template_repository.py   # Physical file storage with semver auto-resolution
├── template_cache.py        # Thread-safe Cache with TTL and capacity limits
├── variable_resolver.py     # Variable binding, environment fallback, and type-caster
├── version_manager.py       # Semantic version control and state transition mapping
├── ab_testing.py            # Variant traffic splits and conversion tracking
├── prompt_history.py        # Local JSONL diagnostic histories and database integration
├── prompt_exporter.py       # Exporter (JSON, YAML, TXT)
├── prompt_importer.py       # Importer (JSON, YAML)
├── models.py                # Dataclasses representing all entities
├── validators.py            # Validation helper functions
├── constants.py             # System categories, limits, and pre-packaged templates
└── exceptions.py            # Module-specific structured exceptions hierarchy
```

---

## 🚀 Key Features

### 1. Unified Facade Access
The entire module is fronted by the simple, high-level `PromptEngine` facade:
```python
from src.prompt_engine import PromptEngine

engine = PromptEngine(
    storage_dir="./assets/prompts",
    history_filepath="./assets/prompt_history.jsonl"
)
```

### 2. Full Variable Resolution & Pre-flight Safe Casts
Variables are validated, type-cast, and filled with system defaults or fallback OS environment variables automatically before compiling:
```python
user_vars = {
    "product_name": "Pro Organic Coffee",
    "product_description": "Single-origin Arabica beans roasted in Dalat."
}

# VariableResolver casts, checks types, binds envs, and handles unresolved required fields gracefully
rendered = engine.render_prompt("gemini_script_generator", user_vars)
print(rendered.user_prompt)
```

### 3. High-Performance Template Storage & Thread-Safe Cache
Templates are stored physically on disk as structured JSON records. A dual-level, thread-safe memory cache speeds up consecutive fetches using configurable Time-To-Live (TTL) expiration and capacity limits.

### 4. Advanced Versioning & Visual Line Diffs
Create major, minor, or patch template versions with full changelogs. Align, track, and diff changes visually line-by-line:
```python
# Bumps version: 1.0.0 -> 1.0.1
new_template = engine.version_bump(
    template_name="gemini_script_generator",
    new_user_prompt="New visual user prompt outline with {{ product_name }}",
    bump_type="patch"
)

# Compare changes line-by-line
comparison = engine.compare_templates("gemini_script_generator", "1.0.0", "1.0.1")
for line in comparison.user_prompt_diff:
    print(f"[{line.type}] {line.content}")
```

### 5. Multi-variant A/B Tests
Route traffic randomly or via strict percentage splits across two template variants to test performance:
```python
test_config = engine.create_ab_test(
    test_id="video_cta_experiment",
    name="CTA Placement Split",
    template_name="gemini_script_generator",
    version_a="1.0.0",
    version_b="1.1.0",
    allocation_ratio_a=0.5
)

# Serves version 1.0.0 or 1.1.0
selected_version, label = engine.select_test_version(test_config)

# ... Run LLM generation with selected version ...

# Mark success conversion on variant completion
engine.record_test_conversion(test_config, label)

# Query conversion rates, metrics, and recommend the leader variant
stats = engine.get_test_stats(test_config)
print(f"Leading Variant: {stats['leading_variant']}")
```

### 6. Token Savings & Compression Algorithms
Optimize templates by stripping whitespace and redundant polite or conversational filler phrases to reduce bills and improve response times:
```python
raw_prompt = "  Please generate   a very nice script for   my business. Thank you so much.  "
compressed = engine.optimize_prompt(raw_prompt, compress_whitespace=True, remove_fillers=True)

print(f"Compressed Text: {compressed.optimized_text}")
print(f"Tokens Saved: {compressed.tokens_saved_estimate}")
```

---

## 🔒 Security & Safeguards
- **OS Compatibility (Windows First):** Safe string sanitization restricts characters in filenames to avoid path-traversal attacks.
- **Provider Safeguards:** Automatically measures character length boundaries against pre-configured provider thresholds (e.g. Gemini, OpenAI, Claude) and throws strict errors or warning logs prior to hitting API endpoints.
- **Prompt Injection Defense:** Scans rendered instructions for standard injection attempt keywords (e.g. `ignore previous instructions`, `bypass guidelines`) and flags risk ratings within rendered metadata logs.
