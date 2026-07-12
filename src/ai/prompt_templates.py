"""Standard prompt templates for marketing scripts, hook generation, and content formatting."""

VERTICAL_VIDEO_SCRIPT_TEMPLATE = """You are a master of high-retention vertical video marketing (TikTok, Instagram Reels, YouTube Shorts).
Your goal is to write a script for a product/service that maximizes watch time and converts viewers.

Product Name: {product_name}
Target Audience: {target_audience}
Core Benefit: {core_benefit}
Tone: {tone}

Structure requirements:
1. THE HOOK (0-3s): Must be a pattern interrupt. Use bold visual descriptions and immediate emotional grab.
2. THE PROBLEM (3-15s): Make the audience feel the pain point acutely.
3. THE SOLUTION (15-30s): Introduce the product naturally as the perfect answer.
4. THE PROOF (30-45s): Include rapid-fire benefits, social proof, or demonstrations.
5. CALL TO ACTION (45-60s): Crisp, single action with zero friction.

Format the output strictly as a structured script, separating "VISUAL/VIDEO STAGE DIRECTION" and "SPOKEN VOICEOVER AUDIO" clearly.
"""

PRODUCT_PITCH_COPY_TEMPLATE = """Write an engaging, persuasive marketing campaign copy.

Product: {product_name}
Platform: {platform}
Tone: {tone}
Primary Value Proposition: {value_prop}

Format the response with variations:
- Option A: Conversational and narrative-driven (ideal for organic reach).
- Option B: High-urgency, direct-response (ideal for paid ads).
- Option C: Short, punchy, bullet-oriented.

Ensure every option has a captivating headline and a clear Call To Action.
"""

VOICE_HOOK_GENERATOR_TEMPLATE = """Generate {count} unique, high-retention audio hook variations.

Topic/Product: {topic}
Target Persona: {persona}
Emotional Trigger: {emotion}

Guidelines:
- Each hook must be 1 sentence only.
- Designed to be spoken aloud by a voiceover talent or AI voice system.
- Maximize curiosity, fear of missing out, or rapid identification of a benefit.
- Do not use cheesy, overused intro words like "Are you tired of..." or "Attention everyone!".
"""
