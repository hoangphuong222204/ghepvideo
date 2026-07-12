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
5. **FREE-First FFmpeg Composition Generation**:
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
- Pricing/Offer details: ${priceInfo || "Regular price"}
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
      res.json(scriptData);
    } catch (error: any) {
      console.error("Script generation error:", error);
      res.status(500).json({
        error: error.message || "Failed to generate video marketing script.",
        isKeyMissing: error.message?.includes("API Key is missing"),
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
