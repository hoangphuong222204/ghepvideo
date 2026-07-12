/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface ProductInfo {
  name: string;
  category: string;
  keyFeatures: string;
  targetAudience: string;
  videoTone: 'hype' | 'educational' | 'storytelling' | 'problem_solving' | 'asymmetric_hook';
  duration: 15 | 30 | 60;
  priceInfo: string;
  callToAction: string;
}

export interface VideoScene {
  id: string;
  timecode: string;
  visualAction: string;
  voiceover: string; // Optimized for Fish Speech TTS (Vietnamese, no weird symbols)
  subtitle: string;  // Screen overlay text
  sfxAudio: string;  // Sound effects / ambient music transition cues
}

export interface MarketingScript {
  hookType: string;
  hookExplanation: string;
  scenes: VideoScene[];
  totalDuration: number;
  ffmpegCommand: string;      // Simple bash snippet
  pythonFFmpegScript: string; // Complete offline Python rendering pipeline
}

export interface VoiceSettings {
  speaker: 'vi-male-natural' | 'vi-female-warm' | 'vi-male-hype' | 'vi-female-hype';
  speed: number;    // 0.8 to 1.5
  pitch: number;    // 0.8 to 1.2
  emotion: 'excited' | 'informative' | 'confident' | 'friendly' | 'calm';
}

export interface BackgroundAsset {
  id: string;
  name: string;
  url: string;
  type: 'video' | 'image';
  category: 'tech' | 'cosmetic' | 'lifestyle' | 'minimal' | 'food';
}
