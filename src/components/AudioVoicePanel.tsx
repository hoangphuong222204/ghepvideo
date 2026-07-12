/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { VoiceSettings, VideoScene } from '../types';
import { Volume2, Play, Square, Code2, AlertTriangle, Check, Settings, Sparkles, Sliders } from 'lucide-react';

interface AudioVoicePanelProps {
  scenes: VideoScene[];
}

export const AudioVoicePanel: React.FC<AudioVoicePanelProps> = ({ scenes }) => {
  const [settings, setSettings] = useState<VoiceSettings>({
    speaker: 'vi-female-warm',
    speed: 1.0,
    pitch: 1.0,
    emotion: 'excited'
  });

  const [activeSceneId, setActiveSceneId] = useState<string>(scenes[0]?.id || '');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  const activeScene = scenes.find(s => s.id === activeSceneId) || scenes[0];

  // Web Speech Synthesis simulator
  const handleTTSPlay = () => {
    if (!activeScene) return;
    
    // Stop any ongoing speech
    window.speechSynthesis.cancel();

    if (isPlaying) {
      setIsPlaying(false);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(activeScene.voiceover);
    
    // Find a Vietnamese voice if available
    const voices = window.speechSynthesis.getVoices();
    const viVoice = voices.find(v => v.lang.includes('vi') || v.lang.includes('VI'));
    if (viVoice) {
      utterance.voice = viVoice;
    }
    
    // Configure rate and pitch
    utterance.rate = settings.speed;
    utterance.pitch = settings.pitch;

    utterance.onend = () => {
      setIsPlaying(false);
    };

    utterance.onerror = () => {
      setIsPlaying(false);
    };

    setIsPlaying(true);
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  const fishSpeechPythonCode = `import requests
import json

# Hàm gọi API Fish Speech chạy cục bộ (Docker / Local Python venv)
def generate_vietnamese_voice(text, speaker_id="${settings.speaker}", speed=${settings.speed}, output_filename="scene_voice.wav"):
    url = "http://localhost:8000/v1/tts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_FISH_SPEECH_API_KEY_IF_NEEDED" # Để trống nếu chạy offline không pass
    }
    
    payload = {
        "text": text,
        "chunk_length": 200,
        "format": "wav",
        "references": [], # Có thể thêm mẫu giọng mồi 3s để clone
        "reference_id": speaker_id,
        "speed": speed,
        "emotion": "${settings.emotion}",
        "pitch": ${settings.pitch}
    }
    
    print(f"Đang gửi yêu cầu chuyển văn bản thành giọng nói Fish Speech cho câu: '{text[:30]}...'")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        with open(output_filename, "wb") as f:
            f.write(response.content)
        print(f"Thành công! Đã lưu file âm thanh chất lượng cao: {output_filename}")
        return output_filename
    else:
        print(f"Lỗi kết nối Fish Speech Engine: {response.status_code}")
        print(response.text)
        return None

# Chạy thử với phân cảnh đã chọn
text_sample = "${activeScene?.voiceover.replace(/"/g, '\\"') || 'Nội dung phân cảnh của bạn'}"
generate_vietnamese_voice(text_sample)
`;

  const copyCode = () => {
    navigator.clipboard.writeText(fishSpeechPythonCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-[#151515] border border-white/5 rounded-xl p-6 shadow-xl space-y-6 relative overflow-hidden">
      {/* Background visual highlight */}
      <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-[#FF3E00]/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-[#FF3E00]/10 rounded-lg text-[#FF3E00] border border-[#FF3E00]/20">
            <Volume2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-100">Cấu Hình Fish Speech TTS</h2>
            <p className="text-[11px] text-slate-400">Giọng đọc Việt hóa tự nhiên cao cấp chạy cục bộ</p>
          </div>
        </div>
        <span className="text-[10px] font-mono text-[#FF3E00] bg-[#FF3E00]/10 border border-[#FF3E00]/20 px-2.5 py-0.5 rounded-full font-bold">
          OFFLINE ENGINE
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Voice Parameters Configuration */}
        <div className="space-y-4">
          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 space-y-4">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-[#FF3E00]" />
              <span>Thông Số Giọng Nói</span>
            </h3>

            {/* Speaker profile */}
            <div>
              <label className="text-xs text-slate-400 block mb-1">Mẫu giọng (Speaker Profile):</label>
              <select
                id="speaker-select"
                value={settings.speaker}
                onChange={(e) => setSettings(prev => ({ ...prev, speaker: e.target.value as any }))}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-lg px-2.5 py-2 focus:outline-none focus:border-[#FF3E00]"
              >
                <option value="vi-female-warm">Nữ Miền Bắc (Ngọt ngào, Truyền cảm)</option>
                <option value="vi-male-natural">Nam Miền Bắc (Trầm ấm, Chuyên nghiệp)</option>
                <option value="vi-female-hype">Nữ Miền Nam (Năng động, Reviewer TikTok)</option>
                <option value="vi-male-hype">Nam Miền Nam (Hào sảng, Thuyết phục)</option>
              </select>
            </div>

            {/* Emotion */}
            <div>
              <label className="text-xs text-slate-400 block mb-1">Cảm xúc giọng đọc:</label>
              <select
                id="emotion-select"
                value={settings.emotion}
                onChange={(e) => setSettings(prev => ({ ...prev, emotion: e.target.value as any }))}
                className="w-full bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-lg px-2.5 py-2 focus:outline-none focus:border-[#FF3E00]"
              >
                <option value="excited">Hào hứng, sôi động (Viral Review)</option>
                <option value="informative">Truyền tải thông tin rõ ràng (Educational)</option>
                <option value="confident">Tự tin, chuyên nghiệp (Thuyết trình)</option>
                <option value="friendly">Thân thiện, gần gũi (Kể chuyện)</option>
                <option value="calm">Nhẹ nhàng, thư giãn (ASMR / Mỹ phẩm)</option>
              </select>
            </div>

            {/* Speed & Pitch controllers */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs text-slate-400">Tốc độ:</label>
                  <span className="text-[10px] font-mono text-[#FF3E00]">{settings.speed}x</span>
                </div>
                <input
                  id="speed-range"
                  type="range"
                  min="0.8"
                  max="1.5"
                  step="0.1"
                  value={settings.speed}
                  onChange={(e) => setSettings(prev => ({ ...prev, speed: parseFloat(e.target.value) }))}
                  className="w-full accent-[#FF3E00] h-1 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>
              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs text-slate-400">Cao độ:</label>
                  <span className="text-[10px] font-mono text-[#FF3E00]">{settings.pitch}x</span>
                </div>
                <input
                  id="pitch-range"
                  type="range"
                  min="0.8"
                  max="1.2"
                  step="0.05"
                  value={settings.pitch}
                  onChange={(e) => setSettings(prev => ({ ...prev, pitch: parseFloat(e.target.value) }))}
                  className="w-full accent-[#FF3E00] h-1 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Web TTS Player Test Box */}
          <div className="bg-slate-950 p-4.5 rounded-xl border border-slate-800/60 space-y-3 relative">
            <h4 className="text-xs font-semibold text-slate-300">Nghe Thử Giọng Phân Cảnh</h4>
            
            <div className="flex items-center gap-3">
              <select
                id="tts-scene-select"
                value={activeSceneId}
                onChange={(e) => setActiveSceneId(e.target.value)}
                className="flex-1 bg-slate-900 border border-slate-800 text-slate-300 text-xs rounded px-2 py-1.5 focus:outline-none"
              >
                {scenes.map((scene, idx) => (
                  <option key={scene.id} value={scene.id}>
                    Cảnh {idx + 1} ({scene.timecode})
                  </option>
                ))}
              </select>

              <button
                id="tts-play-btn"
                onClick={handleTTSPlay}
                className={`py-1.5 px-3 rounded text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                  isPlaying
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                    : 'bg-[#FF3E00] text-white hover:bg-[#E03700] font-bold'
                }`}
              >
                {isPlaying ? (
                  <>
                    <Square className="w-3.5 h-3.5 fill-red-400" />
                    <span>Dừng</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-white" />
                    <span>Nghe</span>
                  </>
                )}
              </button>
            </div>

            {/* Equalizer animation when playing */}
            <div className="h-6 flex items-center justify-center gap-[3px] bg-slate-900/40 rounded border border-slate-800/40 px-3">
              {isPlaying ? (
                Array.from({ length: 18 }).map((_, i) => (
                  <div
                    key={i}
                    className="w-[3px] bg-[#FF3E00] rounded-full animate-pulse"
                    style={{
                      height: `${Math.random() * 100}%`,
                      minHeight: '4px',
                      animationDuration: `${0.4 + Math.random() * 0.6}s`
                    }}
                  />
                ))
              ) : (
                <span className="text-[10px] text-slate-500 italic font-sans">
                  Nhấn Nghe Thử để kiểm tra nhịp điệu đọc tiếng Việt
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Local Python Code Script */}
        <div className="space-y-2 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Code2 className="w-4 h-4 text-[#FF3E00]" />
              <span>Python Integration Script</span>
            </span>
            <button
              id="copy-python-fish-btn"
              onClick={copyCode}
              className="text-[10px] font-bold text-[#FF3E00] hover:text-[#FF3E00]/80 flex items-center gap-1.5 bg-[#FF3E00]/10 border border-[#FF3E00]/20 px-2 py-1 rounded transition-all cursor-pointer"
            >
              {copied ? <Check className="w-3.5 h-3.5" /> : null}
              {copied ? 'Đã sao chép' : 'Sao chép code'}
            </button>
          </div>

          <pre className="flex-1 bg-slate-950 p-4 rounded-xl border border-slate-800 overflow-x-auto text-[10px] text-emerald-400 font-mono leading-relaxed max-h-[220px]">
            {fishSpeechPythonCode}
          </pre>

          <div className="bg-amber-500/5 border border-amber-500/10 rounded-lg p-3 text-[10.5px] text-amber-300 leading-relaxed flex gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
            <span>
              <strong>Lưu ý về Fish Speech:</strong> Fish Speech hỗ trợ clone giọng nói tiếng Việt bằng cách tải file mồi (.wav) dài khoảng 3 đến 5 giây. Để tích hợp cục bộ, hãy khởi động server Fish Speech API rồi chạy đoạn code Python trên để tự động xuất ra âm thanh chất lượng phòng thu hoàn toàn miễn phí.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
