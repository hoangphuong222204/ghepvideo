# AI Marketing Studio PRO: AI Script Engine Technical Specification
**Document Code:** AIMS-PRO-SES-001  
**Version:** 1.0.0-Draft  
**Author:** Lead AI Software Architect  
**Status:** Approved for Engineering Implementation  

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [System Responsibilities](#2-system-responsibilities)
3. [System Workflow](#3-system-workflow)
4. [Input Specification](#4-input-specification)
5. [Output Specification](#5-output-specification)
6. [Script Generation Rules](#6-script-generation-rules)
7. [TikTok Policy Rules](#7-tiktok-policy-rules)
8. [Fish Speech Optimization](#8-fish-speech-optimization)
9. [Quality Scoring](#9-quality-scoring)
10. [Error Handling](#10-error-handling)
11. [Performance](#11-performance)
12. [Future Expansion](#12-future-expansion)

---

## 1. Purpose

The purpose of this document is to specify the complete, rigorous architectural design of the **AI Script Engine** for **AI Marketing Studio PRO**. 

This engine serves as the core intelligence unit of the application. It takes raw, unstructured or structured product descriptions, analyses them, and generates highly natural, policy-compliant, viral short-form video scripts (for TikTok, Reels, Shopee Video) optimized for the **Fish Speech TTS engine** (Vietnamese language).

To maximize runtime efficiency and minimize operational cloud costs, the engine operates on a **Free-First Single-Inference Architecture**. It executes exactly **one** call to the Google Gemini API to extract intelligence, validate claims, rewrite policy issues, adapt pronunciations, and produce up to 50 completely distinct scripts in a structured JSON payload. All subsequent audio rendering (Fish Speech TTS) and video stitching (FFmpeg) are handled locally on the client's desktop environment.

---

## 2. System Responsibilities

The AI Script Engine is responsible for executing the following tasks within a single pipeline run:

*   **Product Semantic Analysis:** Deconstruct arbitrary input text across all vertical categories (Fashion, Tech, Cosmetics, Home, etc.) to discover core selling points, target demographics, and emotional hooks.
*   **TikTok Shop Policy Filtering & Compliance:** Automatically detect restricted words (e.g., medical claims, absolute promises, unverified guarantees) and translate them into soft-selling, safe Vietnamese alternatives.
*   **English-to-Vietnamese Pronunciation Adaptation (Fish Speech Friendly):** Convert standard English/Tech terms and brand names into phonetic, natural Vietnamese spelling so that Fish Speech reads them smoothly without speech artifact glitches.
*   **Numeral-to-Word Conversion:** Expand numbers, prices, and metrics into written Vietnamese text to guarantee natural-sounding speech rate and flow.
*   **Multi-Style Script Generation:** Produce up to 50 completely different scripts featuring diverse storytelling formats (e.g., ASMR, Problem-Solution, Native Review, POV) without repeating key phrases or structures.
*   **Temporal Calibration & Word Rate Estimation:** Estimate speaking durations dynamically based on syllable counts and Vietnamese articulation rate rules, ensuring scripts tightly fit target limits (e.g., exactly 24s ±1s).
*   **Strict JSON Outflow:** Guarantee a perfectly formatted JSON response mapping precisely to the requested schema, suitable for immediate parsing by downstream modules.

---

## 3. System Workflow

The following ASCII diagram illustrates the sequence of operations from initial product input down to the local output delivery.

```
+-----------------------------------------------------------------------------------+
|                               USER/APPLICATION INPUT                              |
|   - Product Metadata, Price, Core Info, Style Targets, Script Count Target (1-50) |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        AI SCRIPT ENGINE - PRE-PROCESSING BLOCK                    |
|   - Validate input boundaries and assemble standard structures                    |
|   - Compile category-agnostic system prompts and zero-shot instructions           |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        GEMINI API GATEWAY (SINGLE INFERENCE)                      |
|                                                                                   |
|  [SYSTEM CONTEXT & Persona: Expert Vietnamese Video Director & Copywriter]        |
|                                         |                                         |
|  +--------------------------------------+--------------------------------------+  |
|  | STEP A: Semantic Deconstruction      | STEP B: Policy Safeguard Checking    |  |
|  | - Extract target audience & category | - Soft-rewrite absolute claims       |  |
|  +--------------------------------------+--------------------------------------+  |
|  | STEP C: Script Multi-Styling (1-50)  | STEP D: Vietnamese Speech Tuning     |  |
|  | - Write completely different hooks   | - English Phonetics & Number spelling|  |
|  +--------------------------------------+--------------------------------------+  |
|                                         |                                         |
|  [STRUCTURED OUTPUT PROTOCOL: responseMimeType = "application/json"]              |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        POST-INFERENCE COMPLIANCE & QUALITY SCORING                |
|   - Locally check JSON structural integrity and parse elements                   |
|   - Evaluate against the AIMS Quality Index (Hook, Speech, Compliance metrics)    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                             DOWNSTREAM COUPLING INTERFACES                        |
|                                                                                   |
|  +--------------------------------------+--------------------------------------+  |
|  | local_fish_speech_engine.py          | local_ffmpeg_assembler.py            |  |
|  | - Synthesizes .wav files             | - Overlay subtitles and render video |  |
|  +--------------------------------------+--------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 4. Input Specification

To facilitate generic category support without demanding manual configurations from the user, the input schema is designed to ingest standard product descriptions and structure parameters.

### 4.1 Input Parameters Table

| Parameter Name | Data Type | Required | Default Value | Validation Constraints | Example Value |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `productName` | String | Yes | N/A | Must not be empty. Max 150 chars. | `"Tai Nghe Không Dây Pro S1"` |
| `category` | String | No | `"Auto-Detect"` | String values. | `"Electronics"` |
| `rawDescription`| String | Yes | N/A | Min 10 characters. Max 2000 chars. | `"Tai nghe pin trâu 40h, chống ồn đỉnh cao ANC"` |
| `priceInfo` | String | No | `"Regular Price"` | Freeform price statement. | `"990.000đ đang sale còn 499.000đ"` |
| `promotions` | String | No | `"None"` | Freeform campaign/promo details. | `"Mua 1 tặng 1 trong hôm nay"` |
| `targetAudience`| String | No | `"General Buyers"`| Custom user segmentation details. | `"Học sinh lái xe ôm công nghệ, shipper"` |
| `scriptCount` | Integer | No | `3` | Minimum: `1`, Maximum: `50`. | `5` |
| `targetDuration`| Integer | No | `24` | Must be either `15`, `30`, or `60` sec. | `30` |
| `selectedStyle` | String | No | `"Any"` | `"Any"`, `"Review"`, `"ASMR"`, `"Luxury"`, etc.| `"Problem-Solving"` |
| `toneColor` | String | No | `"Friendly"` | `"Hype"`, `"Friendly"`, `"Expert"`, `"POV"`.| `"Hype"` |

---

## 5. Output Specification

The output of the engine must strictly return standard, raw JSON directly parseable by client software engines.

### 5.1 JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AIMS_ScriptEngineOutput",
  "type": "object",
  "properties": {
    "metadata": {
      "type": "object",
      "properties": {
        "detectedCategory": { "type": "string" },
        "targetAudienceProfile": { "type": "string" },
        "coreSellingPoints": {
          "type": "array",
          "items": { "type": "string" }
        },
        "buyingMotivations": {
          "type": "array",
          "items": { "type": "string" }
        },
        "usageScenarios": {
          "type": "array",
          "items": { "type": "string" }
        },
        "policyIssuesFound": { "type": "boolean" },
        "policyFixesApplied": { "type": "string" }
      },
      "required": [
        "detectedCategory",
        "targetAudienceProfile",
        "coreSellingPoints",
        "buyingMotivations",
        "usageScenarios",
        "policyIssuesFound",
        "policyFixesApplied"
      ]
    },
    "scripts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "integer" },
          "style": { "type": "string" },
          "hook": { "type": "string" },
          "body": { "type": "string" },
          "cta": { "type": "string" },
          "tts_text": { "type": "string" },
          "estimated_seconds": { "type": "integer" },
          "video_direction_cues": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "timecode": { "type": "string" },
                "visualAction": { "type": "string" },
                "subtitleText": { "type": "string" },
                "sfxAudioCue": { "type": "string" }
              },
              "required": ["timecode", "visualAction", "subtitleText", "sfxAudioCue"]
            }
          }
        },
        "required": [
          "id",
          "style",
          "hook",
          "body",
          "cta",
          "tts_text",
          "estimated_seconds",
          "video_direction_cues"
        ]
      }
    }
  },
  "required": ["metadata", "scripts"]
}
```

### 5.2 Output Fields Explanation

*   `detectedCategory`: The automatically classified segment of the product to guide the vocabulary level (e.g., high-tech vs. soft lifestyle cosmetic tones).
*   `policyIssuesFound`: True if the model intercepted prohibited words during processing.
*   `policyFixesApplied`: Log notes explaining how dangerous claims were toned down (e.g., changed "chữa dứt điểm" to "hỗ trợ làm dịu").
*   `tts_text`: The fully assembled, seamless written script with all numbers, acronyms, and English terms expanded to natural phonetic Vietnamese. This is the exact raw feed string for Fish Speech.
*   `video_direction_cues`: The breakdown timeline containing visual, structural overlay text (subtitles), and background sound effects matching specific video progress timestamps.

---

## 6. Script Generation Rules

The generation algorithm within Gemini must guarantee script variety, high engagement, and perfect timing structure.

### 6.1 Hook Variety and Structure

Short-form videos succeed or fail in the first 3 seconds. The engine must adhere to the **No Greeting, Direct Entry Hook Rule**.
*   **Forbidden Openings:** "Chào mọi người...", "Hôm nay mình sẽ giới thiệu...", "Các bạn ơi..."
*   **Permitted Structures:** Start with a dramatic question, a shocking visual comparison, an emotional crisis, or a direct value proposition.

| Hook Strategy | Mechanism | Example (Vietnamese) |
| :--- | :--- | :--- |
| **Pain Point Crisis** | Starts with an annoying, common daily struggle. | "Mùa hè nóng ba mươi chín độ mà điều hòa lại hỏng đúng lúc nửa đêm..." |
| **Curiosity / Shock** | Challenges a common belief or displays a high contrast. | "Đừng bao giờ mua chiếc tai nghe này nếu bạn không muốn bị điếc vì âm bass quá đỉnh..." |
| **Social Proof / Hype**| Leverages massive viral trend momentum. | "Hơn mười nghìn người đã cháy túi vì cực phẩm dưỡng da này..." |

### 6.2 Diverse Storytelling Styles
If generating multiple scripts (`scriptCount > 1`), the engine selects different frameworks for each script from the following master matrix to ensure zero repetition:

```
[Problem-Solution] --> [Expert Review] --> [ASMR / Cinematic] --> [POV Storytelling]
```

1.  **Problem-Solution:** Standard logical loop. Introduce pain, present product as hero, display proof, CTA.
2.  **ASMR / Minimalist:** High visual focus, descriptive audio cues, calm whispering-vibe text, short punchy statements.
3.  **POV (Point of View) Lifestyle:** Simulates an organic post. "Góc nhìn của một đứa lười dọn nhà khi tậu được máy hút bụi..."
4.  **Luxury/Aesthetic:** Highly descriptive adjectives focusing on sensation, touch, elegance, status, and premium design.

### 6.3 Duration Control & Speaking Rate Calibrator
Vietnamese speech speed rules must be enforced programmatically by the prompt to match target timings (e.g., 24 seconds maximum):
*   **Normal Vietnamese Speech Rate:** ~3.2 words (syllables) per second.
*   **Fast/Hype Review Rate:** ~4.0 words (syllables) per second.
*   **Calculation Constraint:** For a 24-second script, the total word count in `tts_text` must remain strictly between **75 and 95 words (syllables)**. The engine must reject overlong scripts before rendering them.

---

## 7. TikTok Policy Rules

TikTok Shop applies strict automated moderation to claims in product descriptions. The AI Script Engine runs an active mitigation layer to avoid suspension risks.

### 7.1 Forbidden Claims & Automatic Rewriting Matrix

| Restricted Concept / Phrase | Reason | Safe Compliant Alternative |
| :--- | :--- | :--- |
| `"Trị dứt điểm"`, `"Chữa khỏi 100%"` | Unverified medical claim. | `"Hỗ trợ cải thiện rõ rệt"`, `"Giúp làm giảm cảm giác khó chịu"` |
| `"Cam kết hiệu quả"` | Misleading promise. | `"Trải nghiệm thay đổi tích cực sau vài tuần sử dụng"` |
| `"Tốt nhất Việt Nam"`, `"Số 1"` | Unsubstantiated absolute claim. | `"Được cực kỳ nhiều khách hàng tin chọn"`, `"Dòng sản phẩm thuộc top yêu thích"` |
| `"Trắng da cấp tốc chỉ sau 3 ngày"` | Prohibited speed cosmetic claim. | `"Dưỡng da sáng mịn màng rạng rỡ từng ngày"` |
| `"An toàn tuyệt đối không tác dụng phụ"`| Absolute safety statement. | `"Công thức lành tính dịu nhẹ cho mọi đối tượng"` |

### 7.2 Safety Check Pipeline Policy
1.  Verify if the detected category is High-Risk (e.g., Cosmetics, Health, Supplements).
2.  If High-Risk, actively tone down features, focus on sensory experiences (how it feels, looks, smells) and usability scenarios rather than biological or chemical modifications.

---

## 8. Fish Speech Optimization

Fish Speech is a state-of-the-art voice cloning and text-to-speech engine. To generate natural human-sounding Vietnamese speech, the text fed into it must be free of technical symbols, English acronyms, or bare numbers, which usually cause the model to make unnatural spelling mistakes or robotic pauses.

### 8.1 Pronunciation Adaptations (English to Vietnamese Phonetics)

English terms must be converted to Vietnamese phonetic spellings. Meaning must be preserved, not translated:

*   **Technology/Standard Terms:**
    *   `Bluetooth` $\rightarrow$ `"Blu tút"`
    *   `WiFi` $\rightarrow$ `"Quai fai"`
    *   `USB` $\rightarrow$ `"Du ét bi"`
    *   `CPU` $\rightarrow$ `"Xi pi diu"`
    *   `SSD` $\rightarrow$ `"Ét ét đi"`
    *   `LED` $\rightarrow$ `"Lét"`
    *   `App` $\rightarrow$ `"Áp"`
*   **Fashion & Cosmetic Terms:**
    *   `Loafer` $\rightarrow$ `"Loa phơ"`
    *   `Velvet` $\rightarrow$ `"Veo vét"`
    *   `Serum` $\rightarrow$ `"Xê rum"`
    *   `Sneaker` $\rightarrow$ `"Xì ni cơ"`
    *   `Lipstick` $\rightarrow$ `"Lip tích"`

### 8.2 Numeral Expansion Rules

All digits, prices, percentages, and dimensions must be expanded into letters:

*   `99k` or `99.000đ` $\rightarrow$ `"Chín mươi chín nghìn đồng"`
*   `1.500.000 VNĐ` $\rightarrow$ `"Một triệu năm trăm nghìn đồng"`
*   `85%` $\rightarrow$ `"Tám mươi lăm phần trăm"`
*   `6L` (capacity) $\rightarrow$ `"Sáu lít"`
*   `100W` (power) $\rightarrow$ `"Một trăm oát"`
*   `24/7` $\rightarrow$ `"Hai mươi tư trên bảy"`

### 8.3 Punctuation and Breathing Pauses
Fish Speech utilizes standard punctuation to infer voice pitch drops and breathing pauses.
*   **Commas (`,`):** Yields a brief 300ms pause, holding the pitch slightly high for continuation.
*   **Periods (`.`):** Yields a 600ms pause, dropping the pitch of the final syllable.
*   **Ellipses (`...`):** Yields a dramatic 1-second pause. Useful after hooks or before presenting the price.
*   **Forbidden Symbols:** No `#`, `@`, `*`, `[`, `]`, `(`, `)` should appear inside `tts_text` as they confuse the pronunciation engine.

---

## 9. Quality Scoring

To ensure that the output scripts meet production standards, the engine computes a self-evaluating **Quality Index (AIMS-QI)** for each script before finalizing the JSON payload.

### 9.1 Quality Metrics Matrix

```
+--------------------------------------------------------------------------+
|                        AIMS QUALITY INDEX (AIMS-QI)                      |
|                                                                          |
|  [HOK] Hook Impact Score (1-10)       - Is the hook under 3s? No greets? |
|  [NAT] Speech Naturalness (1-10)     - Are English & numbers expanded?   |
|  [SEL] Selling Power Index (1-10)    - Clear value prop & enticing CTA?  |
|  [CMP] Policy Compliance Score (1-10) - Zero forbidden absolute claims?   |
|  [ORG] Originality Index (1-10)      - Non-repetitive style structure?   |
+--------------------------------------------------------------------------+
```

$$\text{AIMS-QI} = 0.25 \times \text{HOK} + 0.20 \times \text{NAT} + 0.15 \times \text{SEL} + 0.25 \times \text{CMP} + 0.15 \times \text{ORG}$$

### 9.2 Quality Benchmarks
*   **Pass Threshold:** $\text{AIMS-QI} \ge 8.0$
*   If a script scores below 8.0, the engine internally adjusts the generation and corrects the offending parameter (e.g., rewriting long hooks or expanding unspelled digits) before delivering the payload.

---

## 10. Error Handling

A robust system must gracefully handle downstream integration errors, API limitations, or invalid inputs.

### 10.1 Error Treatment Guide

| Failure Scenario | Root Cause | System Response / Mitigation |
| :--- | :--- | :--- |
| **Invalid Input Fields** | Missing `productName` or extremely short `rawDescription`. | Throw HTTP 400 Bad Request. Prevent API call to save tokens. |
| **Gemini API Timeout** | Network fluctuation or high model load. | Implement exponential backoff retry. Fallback to client cached templates. |
| **Malformed JSON Output** | Model returned markdown wrap or non-JSON trailing commas. | Strip formatting markdown (````json ... ````) programmatically and run JSON regex repair. |
| **Policy Violation Block** | User entered extremely dangerous medical instructions. | Refuse to generate, return specific compliance warning asking to change product properties. |
| **Fish Speech Text Too Long** | Output word count exceeds maximum syllables allowed. | Auto-truncate script body to fit temporal 24s/30s constraints. |

---

## 11. Performance

Because the system is designed to run locally on creators' desktops with single-cloud API leverage, resources are highly optimized.

### 11.1 Performance Targets
*   **API Response Time:** Maximum 8.5 seconds for up to 5 scripts; maximum 20 seconds for 50 scripts.
*   **Token Consumption Estimate:** 
    *   Input Token Count: ~1,500 tokens (including complete system persona and safety rules prompt).
    *   Output Token Count: ~1,000 tokens per script generated.
*   **Local Processor Overhead:** Virtually 0% CPU/Memory overhead on the hosting environment during script planning, reserving full computing resources for FFmpeg and localized audio synthesizer loops.

---

## 12. Future Expansion

AI Marketing Studio PRO is designed for seamless, modular updates. The AI Script Engine can easily hook into subsequent modules:

1.  **Nano Banana (Vietnamese Voice Model):** Deeply integrate with native specialized Vietnamese TTS voice models for hyper-realistic local accent modulations.
2.  **Integrated Image/Video Generator:** Utilize visual action instructions to query stable diffusion or video models directly to create synthetic backgrounds when actual product footage is unavailable.
3.  **Dynamic Subtitle Renderer:** Export standard SubRip Subtitle (`.srt`) files derived from the timestamp sequences of `video_direction_cues` for automatic, stylized high-contrast burnt-in caption overlay rendering.
4.  **Auto TikTok Publisher:** Push completed, rendered vertical video files directly to TikTok Shop Creator accounts using official public developer APIs.
5.  **Multi-Agent Competitive Intelligence:** Connect multiple sub-agents to crawl competitor shop channels, analyze high-performing scripts, and feed successful hooks back into the AI Script Engine input stream for real-time market alignment.

---
*End of Specification Document.*  
*AI Marketing Studio PRO - Empowering Vietnamese Creators through Scalable, Free-First Offline Engineering.*
