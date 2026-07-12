/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import "dotenv/config";
import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Safe lazy initialization of Google Gen AI
  const getGeminiClient = () => {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey || apiKey === "MY_GEMINI_API_KEY") {
      throw new Error(
        "Google Gemini API Key is missing or default. Please configure it in Settings > Secrets."
      );
    }
    return new GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build",
        },
      },
    });
  };

  // Helper function to detect and sanitize any price, gift, or CTA related info
  function enforcePriceSafety(input: string, fieldName: string): { cleaned: string; issues: string[] } {
    if (!input) return { cleaned: "", issues: [] };
    let cleaned = input;
    const issues: string[] = [];

    // 1. Prohibited CTA Replacements (Rule 6)
    const prohibitedCTAs = [
      { regex: /mua\s+ngay/gi, replacement: "Xem thông tin sản phẩm trong giỏ hàng." },
      { regex: /giá\s+chỉ/gi, replacement: "Nhấn vào sản phẩm để xem chi tiết." },
      { regex: /chỉ\s+còn/gi, replacement: "Xem thông tin mới nhất tại trang sản phẩm." },
      { regex: /giảm\s+ngay/gi, replacement: "Xem thông tin mới nhất tại trang sản phẩm." },
      { regex: /nhanh\s+tay/gi, replacement: "Nhấn vào sản phẩm để xem chi tiết." }
    ];

    for (const { regex, replacement } of prohibitedCTAs) {
      if (regex.test(cleaned)) {
        const matches = cleaned.match(regex);
        if (matches) {
          matches.forEach(m => {
            issues.push(`Phát hiện cụm kêu gọi hành động cấm: "${m}" trong [${fieldName}]. Đã thay bằng: "${replacement}"`);
          });
        }
        cleaned = cleaned.replace(regex, replacement);
      }
    }

    // 2. Prohibited Gift/Promotion Claims (Rule 5)
    const prohibitedGifts = [
      { regex: /mua\s+1\s+tặng\s+1/gi, replacement: "trải nghiệm trọn bộ" },
      { regex: /mua\s+một\s+tặng\s+một/gi, replacement: "trải nghiệm trọn bộ" },
      { regex: /tặng\s+kèm/gi, replacement: "đi kèm" },
      { regex: /khuyến\s+mãi/gi, replacement: "thông tin chi tiết" },
      { regex: /quà\s+tặng/gi, replacement: "sản phẩm đi kèm" },
      { regex: /combo/gi, replacement: "bộ sản phẩm" },
      { regex: /voucher/gi, replacement: "thông tin chi tiết" },
      { regex: /ưu\s+đãi/gi, replacement: "thông tin chi tiết" },
      { regex: /freeship/gi, replacement: "chính sách giao hàng" },
      { regex: /giảm\s+giá/gi, replacement: "chất lượng vượt trội" },
      { regex: /flash\s+sale/gi, replacement: "sự kiện ra mắt" }
    ];

    for (const { regex, replacement } of prohibitedGifts) {
      if (regex.test(cleaned)) {
        const matches = cleaned.match(regex);
        if (matches) {
          matches.forEach(m => {
            issues.push(`Phát hiện thuật ngữ quà tặng/khuyến mãi cấm: "${m}" trong [${fieldName}]. Đã tự động thay thế.`);
          });
        }
        cleaned = cleaned.replace(regex, replacement);
      }
    }

    // 3. Prohibited exact price patterns/phrases mapped to safe alternatives
    const prohibitedClaims = [
      { regex: /giảm\s+\d+%\s*(?:chỉ\s*còn|giá|cho|khi)\s*[^\s,.]*/gi, replacement: "nhấn vào giỏ hàng để xem ưu đãi đang áp dụng" },
      { regex: /chỉ\s+\d+\s*(?:nghìn|ngàn|k|vnd|vnđ|đ|₫|đồng)*/gi, replacement: "xem mức giá mới nhất tại trang sản phẩm" },
      { regex: /giá\s+gốc\s*\d+\s*(?:nghìn|ngàn|k|vnd|vnđ|đ|₫|đồng)*/gi, replacement: "ưu đãi có thể thay đổi theo từng thời điểm" },
      { regex: /giảm\s+còn\s*\d+\s*(?:nghìn|ngàn|k|vnd|vnđ|đ|₫|đồng)*/gi, replacement: "nhấn vào giỏ hàng để xem ưu đãi đang áp dụng" },
      { regex: /rẻ\s+nhất\s+thị\s+trường/gi, replacement: "kiểm tra ưu đãi hiện tại trong giỏ hàng" },
      { regex: /giá\s+hôm\s+nay/gi, replacement: "kiểm tra ưu đãi hiện tại trong giỏ hàng" },
      { regex: /flash\s+sale\s+chỉ\s+còn\s*[^\s,.]*/gi, replacement: "nhấn vào giỏ hàng để xem ưu đãi đang áp dụng" },
      { regex: /tiết\s+kiệm\s*\d+\s*(?:nghìn|ngàn|k|vnd|vnđ|đ|₫|đồng)*/gi, replacement: "kiểm tra ưu đãi hiện tại trong giỏ hàng" }
    ];

    for (const { regex, replacement } of prohibitedClaims) {
      if (regex.test(cleaned)) {
        const matches = cleaned.match(regex);
        if (matches) {
          matches.forEach(m => {
            issues.push(`Phát hiện cụm quảng cáo giá cấm: "${m}" trong [${fieldName}]. Đã tự động thay thế.`);
          });
        }
        cleaned = cleaned.replace(regex, replacement);
      }
    }

    // 4. Suffix k/K (e.g., 99k, 99 K)
    const kPattern = /\b\d+\s*[kK]\b/g;
    if (kPattern.test(cleaned)) {
      const matches = cleaned.match(kPattern);
      if (matches) {
        matches.forEach(m => {
          issues.push(`Phát hiện mẫu giá dạng K: "${m}" trong [${fieldName}]. Đã tự động loại bỏ.`);
        });
      }
      cleaned = cleaned.replace(kPattern, "thông tin chi tiết");
    }

    // 5. Spelled out numbers followed by price words (e.g., "chín mươi chín nghìn", "hai trăm ngàn", "mười lăm nghìn đồng")
    const spelledPattern = /\b(?:không|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|chục|trăm|lẻ|linh|mốt|tư|nhăm)\s+(?:không|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|chục|trăm|lẻ|linh|mốt|tư|nhăm|nghìn|ngàn|triệu|tỷ|đồng|k)*\s*(?:nghìn|ngàn|triệu|tỷ|đồng)\b/gi;
    if (spelledPattern.test(cleaned)) {
      const matches = cleaned.match(spelledPattern);
      if (matches) {
        matches.forEach(m => {
          issues.push(`Phát hiện giá trị số bằng chữ: "${m}" trong [${fieldName}]. Đã tự động loại bỏ.`);
        });
      }
      cleaned = cleaned.replace(spelledPattern, "mức giá cực tốt");
    }

    // 6. Standard currency patterns (e.g., 99.000đ, 99.000, 99,000đ, ₫99,000, $99, 199.000 vnd)
    const currencyPattern = /\b\d+(?:[.,]\d{3})*\s*(?:[đ₫dD]|VND|VNĐ|Vnd|Vnđ|USD|Usd|usd|\$)\b/gi;
    if (currencyPattern.test(cleaned)) {
      const matches = cleaned.match(currencyPattern);
      if (matches) {
        matches.forEach(m => {
          issues.push(`Phát hiện mẫu giá trị đơn vị tiền tệ: "${m}" trong [${fieldName}]. Đã tự động loại bỏ.`);
        });
      }
      cleaned = cleaned.replace(currencyPattern, "mức giá ưu đãi tại giỏ hàng");
    }

    // 7. Standalone raw big numbers (e.g. 199000, 99000, etc.)
    const bigNumPattern = /\b\d{5,}\b/g;
    if (bigNumPattern.test(cleaned)) {
      const matches = cleaned.match(bigNumPattern);
      if (matches) {
        matches.forEach(m => {
          issues.push(`Phát hiện chuỗi số đại diện giá thô: "${m}" trong [${fieldName}]. Đã tự động loại bỏ.`);
        });
      }
      cleaned = cleaned.replace(bigNumPattern, "thông tin chi tiết");
    }

    // 8. Standalone symbols
    const standaloneSymbols = /(?:\bVND\b|\bVNĐ\b|\bVnđ\b|[₫đ$])/gi;
    if (standaloneSymbols.test(cleaned)) {
      const matches = standaloneSymbols.test(cleaned) ? cleaned.match(standaloneSymbols) : null;
      if (matches) {
        matches.forEach(m => {
          issues.push(`Phát hiện ký hiệu giá: "${m}" trong [${fieldName}]. Đã tự động loại bỏ.`);
        });
      }
      cleaned = cleaned.replace(standaloneSymbols, "");
    }

    return { cleaned, issues };
  }

  // Sanitizes all text fields in a MarketingScript structure and returns list of corrected validation issues
  function cleanAndValidateMarketingScript(script: any): any {
    if (!script) return script;
    const issues: string[] = [];

    // Sanitize hookExplanation
    if (script.hookExplanation) {
      const { cleaned, issues: fieldIssues } = enforcePriceSafety(script.hookExplanation, "Lời giải thích Hook");
      script.hookExplanation = cleaned;
      issues.push(...fieldIssues);
    }

    // Sanitize scenes
    if (Array.isArray(script.scenes)) {
      script.scenes.forEach((scene: any, idx: number) => {
        const sceneLabel = `Cảnh ${idx + 1}`;
        if (scene.voiceover) {
          const { cleaned, issues: fieldIssues } = enforcePriceSafety(scene.voiceover, `${sceneLabel} - Giọng đọc`);
          scene.voiceover = cleaned;
          issues.push(...fieldIssues);
        }
        if (scene.subtitle) {
          const { cleaned, issues: fieldIssues } = enforcePriceSafety(scene.subtitle, `${sceneLabel} - Phụ đề`);
          scene.subtitle = cleaned;
          issues.push(...fieldIssues);
        }
        if (scene.visualAction) {
          const { cleaned, issues: fieldIssues } = enforcePriceSafety(scene.visualAction, `${sceneLabel} - Hành động`);
          scene.visualAction = cleaned;
          issues.push(...fieldIssues);
        }
      });
    }

    // Sanitize ffmpegCommand and pythonFFmpegScript
    if (script.ffmpegCommand) {
      const { cleaned, issues: fieldIssues } = enforcePriceSafety(script.ffmpegCommand, "Lệnh FFmpeg");
      script.ffmpegCommand = cleaned;
      issues.push(...fieldIssues);
    }
    if (script.pythonFFmpegScript) {
      const { cleaned, issues: fieldIssues } = enforcePriceSafety(script.pythonFFmpegScript, "Kịch bản Python FFmpeg");
      script.pythonFFmpegScript = cleaned;
      issues.push(...fieldIssues);
    }

    script.validationIssues = issues;
    return script;
  }

  // API endpoint: Generate Vietnamese marketing scripts, Voice cues, and FFmpeg instructions
  app.post("/api/generate-script", async (req, res) => {
    try {
      const {
        name,
        category,
        keyFeatures,
        targetAudience,
        videoTone,
        duration,
        priceInfo,
        callToAction,
      } = req.body;

      if (!name) {
        return res.status(400).json({ error: "Product name is required." });
      }

      const ai = getGeminiClient();

      // System instruction sets the persona of Senior TikTok Content Creator, Vietnamese Copywriter, and Video Director
      const systemInstruction = `
You are the Lead Marketing Copywriter, TikTok Shop Viral Content Expert, and Creative Video Director for AI Marketing Studio PRO.
Your goal is to write a highly natural, viral Vietnamese marketing video script for TikTok/Reels based on product details.

Strict Writing Guidelines:
1. **The Hook (First 2-3 seconds)**: MUST be extremely strong, direct, and address a visual or narrative pain point of the target audience. No warm greetings or introductions like "Xin chào các bạn" or "Hôm nay mình sẽ giới thiệu...". Start with the problem or an exciting transformation!
2. **Vietnamese for Speech (TTS Friendly)**: The voiceover text MUST be written in 100% natural, colloquial Vietnamese, optimized for Fish Speech TTS engine:
   - Spell out ALL numbers (e.g., use "chín mươi chín nghìn" instead of "99k" or "99.000đ", use "hai mươi mốt" instead of "21").
   - Spell out units (e.g., use "mét", "gam", "phần trăm", "độ xê" instead of "m", "g", "%", "°C").
   - Spell out acronyms/abbreviations (e.g., use "Ai ti" instead of "IT", "Ai ai" instead of "AI", "Súp bờ" instead of "Super").
   - Do not use hashtags, emojis, brackets, or English slangs inside the 'voiceover' fields (keep them plain text so TTS doesn't glitch). Emojis and hashtags can go in visual descriptions or overlays.
3. **Product Policy & Trustworthiness**: Avoid exaggerated claims or absolute words like "trị dứt điểm", "cam kết hoàn toàn", "chữa khỏi" if it is a wellness or cosmetic product. Frame features around realistic user experiences and benefits.
4. **Visual Action**: Provide rich visual actions suitable for a 9:16 vertical short-form video (e.g., zoom cuts, product closeup, high-contrast text overlay, text highlights, sound effect cues).
5. **PRICE SAFETY RULE (CRITICAL MANDATE - ABSOLUTE CEILING)**:
   - You MUST NEVER include explicit price numbers, discount amounts, voucher values, original prices, or currency symbols in the generated hook, body, voiceover text, subtitles, call to action, scene overlays, or any other output.
   - Prices constantly change; hence, absolute numeric pricing claims are strictly forbidden.
   - Absolutely forbidden phrases: "Chỉ 99 nghìn đồng", "Giá gốc 299 nghìn", "Giảm còn 199K", "Rẻ nhất thị trường", "Giá hôm nay", "Flash sale chỉ còn...", "Tiết kiệm 50 nghìn", or any numeric/spelled equivalents representing prices.
   - You MUST replace any price/discount information with these exact safe Vietnamese alternatives:
     * "Kiểm tra ưu đãi hiện tại trong giỏ hàng"
     * "Xem mức giá mới nhất tại trang sản phẩm"
     * "Nhấn vào giỏ hàng để xem ưu đãi đang áp dụng"
     * "Ưu đãi có thể thay đổi theo từng thời điểm"
6. **NO GIFTS, NO PROMOS RULE (CRITICAL MANDATE)**:
   - You MUST NEVER use terms representing gifts, promotions, combos, or vouchers.
   - Absolutely forbidden words: "Tặng kèm", "Mua 1 tặng 1", "Mua một tặng một", "Khuyến mãi", "Quà tặng", "Combo", "Voucher", "Ưu đãi", "Freeship", "Giảm giá", "Flash Sale".
   - Replace any such mentions in input content with purely descriptive, generic product benefit details. Do not reference gift packages or temporary marketing campaigns.
7. **CTA REPLACEMENT RULE (CRITICAL MANDATE)**:
   - Do NOT use forbidden call-to-actions such as: "Mua ngay", "Giá chỉ", "Chỉ còn", "Giảm ngay", "Nhanh tay".
   - Instead, you MUST only use these exact allowed alternative CTAs:
     * "Xem thông tin sản phẩm trong giỏ hàng."
     * "Nhấn vào sản phẩm để xem chi tiết."
     * "Xem thông tin mới nhất tại trang sản phẩm."
8. **FREE-First FFmpeg Composition Generation**:
   - Provide a functional shell FFmpeg command to stitch the scenes together.
   - Also provide a beautifully structured Python subprocess script that stitches background video assets, mixes an audio track (from TTS and ambient music), and overlays stylized subtitles at the exact scene timecodes.
`;

      const prompt = `
Generate a viral vertical video marketing script for the following product:
- Product Name: ${name}
- Category: ${category || "General"}
- Key Features: ${keyFeatures || "Not specified"}
- Target Audience: ${targetAudience || "General buyers"}
- Video Tone: ${videoTone || "hype"} (Values: hype, educational, storytelling, problem_solving, asymmetric_hook)
- Targeted Video Duration: ${duration || 30} seconds
- Pricing/Offer details (APPLY PRICE SAFETY RULE - IGNORE RAW NUMBERS): ${priceInfo || "Regular price"}
- Call To Action (CTA): ${callToAction || "Click the link below!"}

Please output a strictly structured JSON response that complies with the schema. Ensure there are exactly ${
        duration === 15 ? 3 : duration === 30 ? 5 : 8
      } scenes matching the duration.
Make sure the voiceover text reads naturally and matches the ${duration}s limit when read at normal speed (approx. 3-4 syllables per second).
`;

      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: prompt,
        config: {
          systemInstruction,
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              hookType: {
                type: Type.STRING,
                description: "Name of the hook strategy used (e.g. Pain Point, Curiosity, Social Proof).",
              },
              hookExplanation: {
                type: Type.STRING,
                description: "Explanation of why this hook works for Vietnamese viewers.",
              },
              scenes: {
                type: Type.ARRAY,
                items: {
                  type: Type.OBJECT,
                  properties: {
                    id: { type: Type.STRING },
                    timecode: { type: Type.STRING, description: "Start and end time, e.g. 00:00 - 00:05" },
                    visualAction: { type: Type.STRING, description: "Action to display on screen (vertical frame details)." },
                    voiceover: { type: Type.STRING, description: "Spelled-out speech in Vietnamese, optimized for Fish Speech. No abbreviations or punctuation symbols that TTS can't read." },
                    subtitle: { type: Type.STRING, description: "Subtitles overlay text (can include price text, emojis)." },
                    sfxAudio: { type: Type.STRING, description: "Sound effect/ambient suggestion (e.g., swoosh, pop, cash register, subtle upbeat beat)." },
                  },
                  required: ["id", "timecode", "visualAction", "voiceover", "subtitle", "sfxAudio"],
                },
              },
              totalDuration: { type: Type.INTEGER, description: "Calculated total duration in seconds." },
              ffmpegCommand: {
                type: Type.STRING,
                description: "Terminal FFmpeg command to merge scenes and draw subtitle overlays.",
              },
              pythonFFmpegScript: {
                type: Type.STRING,
                description: "Full Python script containing setup and ffmpeg commands to run locally on the desktop.",
              },
            },
            required: [
              "hookType",
              "hookExplanation",
              "scenes",
              "totalDuration",
              "ffmpegCommand",
              "pythonFFmpegScript",
            ],
          },
        },
      });

      const responseText = response.text;
      if (!responseText) {
        throw new Error("No script content received from Gemini.");
      }

      const scriptData = JSON.parse(responseText.trim());
      const safeScriptData = cleanAndValidateMarketingScript(scriptData);
      res.json(safeScriptData);
    } catch (error: any) {
      console.error("Script generation error:", error);
      res.status(500).json({
        error: error.message || "Failed to generate video marketing script.",
        isKeyMissing: error.message?.includes("API Key is missing"),
      });
    }
  });

  // API endpoint: Extract structured product info from raw pasted content
  app.post("/api/extract-product-info", async (req, res) => {
    try {
      const { rawText } = req.body;
      if (!rawText || !rawText.trim()) {
        return res.status(400).json({ error: "Nội dung thô không được để trống." });
      }

      const ai = getGeminiClient();

      const systemInstruction = `
Bạn là chuyên gia phân tích và trích xuất dữ liệu sản phẩm của AI Marketing Studio PRO.
Nhiệm vụ của bạn là đọc thông tin thô được cung cấp (ví dụ: mô tả sản phẩm trên Shopee, TikTok Shop, Lazada, bài viết bán hàng Facebook, bài viết giới thiệu website hoặc file TXT) và trích xuất thành một cấu trúc thông số sản phẩm hoàn chỉnh để tạo kịch bản video viral.

Quy định quan trọng về trích xuất để TUÂN THỦ LUẬT AN TOÀN GIÁ (PRICE SAFETY RULE):
1. "priceInfo": Bạn TUYỆT ĐỐI KHÔNG ĐƯỢC trích xuất giá bán cụ thể hoặc bất kỳ con số, mức giảm giá, voucher hay đơn vị tiền tệ nào vào đây. Thay vì ghi giá bán (ví dụ: "99k", "250.000đ", "hai trăm nghìn đồng", "199000"), hãy viết một thông điệp an toàn trung tính và được phép như: "Xem thông tin sản phẩm trong giỏ hàng." hoặc "Xem mức giá mới nhất tại trang sản phẩm."
2. "promotion": TUYỆT ĐỐI KHÔNG trích xuất bất kỳ từ ngữ nào liên quan đến quà tặng, quà kèm, mua 1 tặng 1, khuyến mãi, voucher, giảm giá, flash sale hay freeship. Hãy điền "Không áp dụng" hoặc mô tả các đặc tính hữu ích dài hạn của sản phẩm thay thế.
3. TUYỆT ĐỐI KHÔNG SỬ DỤNG các từ cấm kỵ sau trong bất kỳ trường nào: "Tặng kèm", "Mua 1 tặng 1", "Mua một tặng một", "Khuyến mãi", "Quà tặng", "Combo", "Voucher", "Ưu đãi", "Freeship", "Giảm giá", "Flash Sale".
4. "callToAction": Tuyệt đối không dùng các cụm từ kêu gọi bị cấm như: "Mua ngay", "Giá chỉ", "Chỉ còn", "Giảm ngay", "Nhanh tay". Thay vào đó, bạn chỉ được phép chọn và điền một trong các cụm từ sau:
   - "Xem thông tin sản phẩm trong giỏ hàng."
   - "Nhấn vào sản phẩm để xem chi tiết."
   - "Xem thông tin mới nhất tại trang sản phẩm."
5. "videoTone": Đánh giá nội dung sản phẩm để đề xuất tông giọng phù hợp nhất. Chỉ được chọn một trong các giá trị sau: "asymmetric_hook", "problem_solving", "hype", "educational", "storytelling".
6. "duration": Đề xuất thời lượng phù hợp. Chỉ được chọn một trong các giá trị số sau: 15, 30, 60.
7. Ngôn ngữ: Toàn bộ thông tin trích xuất phải bằng Tiếng Việt tự nhiên, ngắn gọn, súc tích và có tính thuyết phục cao.
`;

      const prompt = `
Hãy phân tích nội dung thông tin sản phẩm thô sau đây và trích xuất thành đối tượng JSON theo đúng cấu trúc yêu cầu:

NỘI DUNG THÔ:
"""
${rawText}
"""
`;

      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: prompt,
        config: {
          systemInstruction,
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              name: { type: Type.STRING, description: "Tên sản phẩm chính xác, rõ ràng." },
              brand: { type: Type.STRING, description: "Thương hiệu sản phẩm nếu có, hoặc để rỗng." },
              category: { type: Type.STRING, description: "Ngành hàng hoặc phân loại sản phẩm." },
              priceInfo: { type: Type.STRING, description: "Giá tiền sản phẩm được diễn giải chi tiết bằng chữ Tiếng Việt." },
              promotion: { type: Type.STRING, description: "Chương trình khuyến mãi, ưu đãi, quà tặng kèm nếu có." },
              targetAudience: { type: Type.STRING, description: "Chân dung khách hàng mục tiêu phù hợp nhất." },
              desire: { type: Type.STRING, description: "Mong muốn thầm kín, lý do khách mua hàng hoặc lợi ích cốt lõi." },
              keyFeatures: { type: Type.STRING, description: "Các ưu điểm vượt trội, thông số kỹ thuật hoặc điểm gây đau khổ (pain point) khách gặp phải." },
              platform: { type: Type.STRING, description: "Nền tảng đăng bài đề xuất (ví dụ: TikTok Shop, Shopee Video, Facebook Reels)." },
              videoTone: { 
                type: Type.STRING, 
                description: "Tông giọng video đề xuất. Phải là 1 trong các giá trị: asymmetric_hook, problem_solving, hype, educational, storytelling." 
              },
              duration: { type: Type.INTEGER, description: "Thời lượng video đề xuất (15, 30 hoặc 60)." },
              callToAction: { type: Type.STRING, description: "Lời kêu gọi hành động (CTA) kích thích hành vi mua." },
              keywords: { type: Type.STRING, description: "3 đến 5 từ khóa cốt lõi của sản phẩm cách nhau bởi dấu phẩy." },
              forbiddenWords: { type: Type.STRING, description: "Các từ cấm kỵ nên tránh khi quảng cáo trên nền tảng (ví dụ: cam kết hoàn toàn, trị tận gốc, tốt nhất)." },
              advancedPrompt: { type: Type.STRING, description: "Gợi ý định hướng biên kịch bổ sung cho AI." },
            },
            required: [
              "name",
              "brand",
              "category",
              "priceInfo",
              "promotion",
              "targetAudience",
              "desire",
              "keyFeatures",
              "platform",
              "videoTone",
              "duration",
              "callToAction",
              "keywords",
              "forbiddenWords",
              "advancedPrompt"
            ],
          },
        },
      });

      const responseText = response.text;
      if (!responseText) {
        throw new Error("Không nhận được kết quả phân tích từ Gemini.");
      }

      const extractedData = JSON.parse(responseText.trim());
      
      // Post-extraction sanitization layer to fully enforce price safety
      if (extractedData.priceInfo) {
        const { cleaned } = enforcePriceSafety(extractedData.priceInfo, "Giá bán");
        extractedData.priceInfo = cleaned || "Xem mức giá mới nhất tại trang sản phẩm";
      }
      if (extractedData.promotion) {
        const { cleaned } = enforcePriceSafety(extractedData.promotion, "Khuyến mãi");
        extractedData.promotion = cleaned || "Ưu đãi có thể thay đổi theo từng thời điểm";
      }
      if (extractedData.callToAction) {
        const { cleaned } = enforcePriceSafety(extractedData.callToAction, "Lời kêu gọi");
        extractedData.callToAction = cleaned;
      }
      
      res.json(extractedData);
    } catch (error: any) {
      console.error("Product extraction error:", error);
      res.status(500).json({
        error: error.message || "Không thể phân tích dữ liệu sản phẩm.",
      });
    }
  });

  // Serve static files and load Vite Dev Server middleware
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
  });
}

startServer();
