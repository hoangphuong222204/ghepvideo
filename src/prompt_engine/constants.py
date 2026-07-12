"""Constants used throughout the Prompt Engine."""

from typing import Dict, List, Set

# Supported AI Providers
PROVIDER_GEMINI = "Gemini"
PROVIDER_OPENAI = "OpenAI"
PROVIDER_CLAUDE = "Claude"
PROVIDER_DEEPSEEK = "DeepSeek"
PROVIDER_QWEN = "Qwen"
PROVIDER_OLLAMA = "Ollama"
PROVIDER_LM_STUDIO = "LM Studio"

SUPPORTED_PROVIDERS: Set[str] = {
    PROVIDER_GEMINI,
    PROVIDER_OPENAI,
    PROVIDER_CLAUDE,
    PROVIDER_DEEPSEEK,
    PROVIDER_QWEN,
    PROVIDER_OLLAMA,
    PROVIDER_LM_STUDIO,
}

# Standard Prompt Categories / Use Cases
CAT_AI_SCRIPT = "AI Script"
CAT_TRANSLATION = "Translation"
CAT_REWRITE = "Rewrite"
CAT_SEO = "SEO"
CAT_MARKETING = "Marketing"
CAT_PRODUCT_ANALYSIS = "Product Analysis"
CAT_VIDEO_PROMPT = "Video Prompt"
CAT_IMAGE_PROMPT = "Image Prompt"
CAT_VOICE_PROMPT = "Voice Prompt"

SUPPORTED_CATEGORIES: Set[str] = {
    CAT_AI_SCRIPT,
    CAT_TRANSLATION,
    CAT_REWRITE,
    CAT_SEO,
    CAT_MARKETING,
    CAT_PRODUCT_ANALYSIS,
    CAT_VIDEO_PROMPT,
    CAT_IMAGE_PROMPT,
    CAT_VOICE_PROMPT,
}

# Provider Specific Token/Length Restrictions & Safeguards (Character/Token counts approximate)
PROVIDER_LIMITS: Dict[str, Dict[str, int]] = {
    PROVIDER_GEMINI: {"max_characters": 8000000, "recommendation_limit": 1000000},
    PROVIDER_OPENAI: {"max_characters": 500000, "recommendation_limit": 128000},
    PROVIDER_CLAUDE: {"max_characters": 800000, "recommendation_limit": 200000},
    PROVIDER_DEEPSEEK: {"max_characters": 250000, "recommendation_limit": 64000},
    PROVIDER_QWEN: {"max_characters": 128000, "recommendation_limit": 32000},
    PROVIDER_OLLAMA: {"max_characters": 64000, "recommendation_limit": 16000},
    PROVIDER_LM_STUDIO: {"max_characters": 64000, "recommendation_limit": 16000},
}

# Template Version Stability Modes
VERSION_STABILITY_DRAFT = "Draft"
VERSION_STABILITY_CANDIDATE = "Candidate"
VERSION_STABILITY_ACTIVE = "Active"
VERSION_STABILITY_DEPRECATED = "Deprecated"

VERSION_STABILITY_MODES: Set[str] = {
    VERSION_STABILITY_DRAFT,
    VERSION_STABILITY_CANDIDATE,
    VERSION_STABILITY_ACTIVE,
    VERSION_STABILITY_DEPRECATED,
}

# Performance and Cache defaults
DEFAULT_CACHE_TTL_SECONDS = 300  # 5 minutes
MAX_CACHE_SIZE = 1000  # maximum template variations cached

# Prebuilt default prompt templates for instant execution
DEFAULT_TEMPLATES: List[Dict[str, str]] = [
    {
        "name": "gemini_script_generator",
        "category": CAT_AI_SCRIPT,
        "provider": PROVIDER_GEMINI,
        "version": "1.0.0",
        "description": "Premium Vietnamese marketing video script generator optimized for Gemini",
        "system_prompt": (
            "You are an expert Vietnamese conversion copywriter. "
            "Write highly engaging, authentic video scripts in Vietnamese based on the product description."
        ),
        "user_prompt": (
            "Product: {{ product_name }}\n"
            "Description: {{ product_description }}\n"
            "Style: {{ style | default('Problem Solution') }}\n"
            "Platform: {{ platform | default('TikTok') }}\n"
            "{% if core_benefit %}Core Benefit: {{ core_benefit }}\n{% endif %}"
            "Generate a highly visual marketing script with exactly {{ quantity | default(1) }} scenes."
        ),
    },
    {
        "name": "generic_marketing_rewriter",
        "category": CAT_REWRITE,
        "provider": PROVIDER_OPENAI,
        "version": "1.0.0",
        "description": "Rewrites marketing copy into viral, engaging tones",
        "system_prompt": "You are a professional marketing editor. Enhance the punchiness, flow, and visual imagery of the copy.",
        "user_prompt": (
            "Rewrite the following copy:\n"
            "\"{{ text }}\"\n"
            "Tone: {{ tone | default('Energetic') }}\n"
            "Keep the length under {{ max_length | default(500) }} characters."
        ),
    },
    {
        "name": "seo_keyword_generator",
        "category": CAT_SEO,
        "provider": PROVIDER_GEMINI,
        "version": "1.1.0",
        "description": "Generates semantic Vietnamese keywords and meta-tags",
        "system_prompt": "You are an SEO architect. Provide structured meta-titles, meta-descriptions, and LSI keywords.",
        "user_prompt": (
            "Analyze and extract keywords for website: {{ url }}\n"
            "Topic: {{ topic }}\n"
            "Target Audience: {{ target_audience | default('Vietnamese Shoppers') }}"
        ),
    }
]
