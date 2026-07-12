import React, { useState, useEffect } from 'react';
import { VideoScene, VoiceSettings } from '../types';
import {
  Volume2, Play, Square, Code, Check, Sliders, AudioLines, Flame, Settings, Sparkles, Activity
} from 'lucide-react';

interface VoiceViewProps {
  scenes: VideoScene[];
  settings: VoiceSettings;
  onUpdateSettings: (settings: VoiceSettings) => void;
  selectedSceneId: string;
  onSelectScene: (id: string) => void;
  isPlaying: boolean;
  onPlayToggle: () => void;
}

export const VoiceView: React.FC<VoiceViewProps> = ({
  scenes,
  settings,
  onUpdateSettings,
  selectedSceneId,
  onSelectScene,
  isPlaying,
  onPlayToggle,
}) => {
  const [copied, setCopied] = useState<boolean>(false);

  const activeScene = scenes.find(s => s.id === selectedSceneId) || scenes[0];

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
    <div className="space-y-6 animate-fadeIn select-none">
      {/* Visual Header */}
      <div className="flex items-center justify-between bg-zinc-950 border border-zinc-800 p-4 rounded-xl">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-orange-600/15 text-orange-500 rounded">
            <Volume2 className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-zinc-200">Cấu Hình Fish Speech & TTS</h3>
            <p className="text-[10px] text-zinc-500">Giọng đọc Việt hóa tự nhiên cao cấp chạy cục bộ hoàn toàn miễn phí</p>
          </div>
        </div>
        <span className="text-[9px] font-mono font-bold text-orange-500 bg-orange-500/10 border border-orange-500/20 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
          Offline TTS Engine
        </span>
      </div>

      {/* Grid of panels */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        
        {/* Left rack: Parameter Settings */}
        <div className="space-y-4">
          <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl space-y-4 shadow-xl">
            <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-widest flex items-center gap-2 border-b border-zinc-850 pb-2.5">
              <Sliders className="w-3.5 h-3.5 text-orange-500" />
              <span>Thiết lập thông số âm học</span>
            </h4>

            {/* Speaker profile */}
            <div>
              <label className="text-[10px] font-mono font-bold text-zinc-400 block mb-1">MẪU GIỌNG ĐỌC (SPEAKER PROFILE)</label>
              <select
                value={settings.speaker}
                onChange={(e) => onUpdateSettings({ ...settings, speaker: e.target.value as any })}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded px-3 py-2 focus:outline-none focus:border-orange-500"
              >
                <option value="vi-female-warm">Nữ Miền Bắc (Ngọt ngào, Truyền cảm)</option>
                <option value="vi-male-natural">Nam Miền Bắc (Trầm ấm, Chuyên nghiệp)</option>
                <option value="vi-female-hype">Nữ Miền Nam (Năng động, Reviewer TikTok)</option>
                <option value="vi-male-hype">Nam Miền Nam (Hào sảng, Thuyết phục)</option>
              </select>
            </div>

            {/* Emotion */}
            <div>
              <label className="text-[10px] font-mono font-bold text-zinc-400 block mb-1">CẢM XÚC BIỂU CẢM GIỌNG ĐỌC</label>
              <select
                value={settings.emotion}
                onChange={(e) => onUpdateSettings({ ...settings, emotion: e.target.value as any })}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded px-3 py-2 focus:outline-none focus:border-orange-500"
              >
                <option value="excited">Hào hứng, sôi động (Viral Review)</option>
                <option value="informative">Truyền tải thông tin rõ ràng (Educational)</option>
                <option value="confident">Tự tin, chuyên nghiệp (Thuyết trình)</option>
                <option value="friendly">Thân thiện, gần gũi (Kể chuyện)</option>
                <option value="calm">Nhẹ nhàng, thư giãn (ASMR / Mỹ phẩm)</option>
              </select>
            </div>

            {/* Speed & Pitch */}
            <div className="grid grid-cols-2 gap-4 pt-1">
              <div>
                <div className="flex justify-between items-center mb-1 text-[10px] font-mono font-bold text-zinc-400">
                  <span>TỐC ĐỘ (SPEED)</span>
                  <span className="text-orange-500">{settings.speed}x</span>
                </div>
                <input
                  type="range"
                  min="0.8"
                  max="1.5"
                  step="0.1"
                  value={settings.speed}
                  onChange={(e) => onUpdateSettings({ ...settings, speed: parseFloat(e.target.value) })}
                  className="w-full accent-orange-500 h-1 bg-zinc-800 rounded cursor-pointer"
                />
              </div>
              <div>
                <div className="flex justify-between items-center mb-1 text-[10px] font-mono font-bold text-zinc-400">
                  <span>CAO ĐỘ (PITCH)</span>
                  <span className="text-orange-500">{settings.pitch}x</span>
                </div>
                <input
                  type="range"
                  min="0.8"
                  max="1.2"
                  step="0.05"
                  value={settings.pitch}
                  onChange={(e) => onUpdateSettings({ ...settings, pitch: parseFloat(e.target.value) })}
                  className="w-full accent-orange-500 h-1 bg-zinc-800 rounded cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* Web TTS Player Test Bench */}
          <div className="bg-zinc-900 border border-zinc-850 p-4.5 rounded-xl space-y-3 shadow-xl">
            <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-widest block border-b border-zinc-850 pb-2">
              Bàn nghe thử và tối ưu hoá câu đọc
            </h4>

            <div className="flex items-center gap-3">
              <select
                value={selectedSceneId}
                onChange={(e) => onSelectScene(e.target.value)}
                className="flex-1 bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded px-2.5 py-1.5 focus:outline-none"
              >
                {scenes.map((sc, idx) => (
                  <option key={sc.id} value={sc.id}>
                    Cảnh {idx + 1} ({sc.timecode})
                  </option>
                ))}
              </select>

              <button
                onClick={onPlayToggle}
                className={`py-1.5 px-4 rounded text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
                  isPlaying
                    ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                    : 'bg-orange-600 hover:bg-orange-500 text-white'
                }`}
              >
                {isPlaying ? <Square className="w-3.5 h-3.5 fill-red-400" /> : <Play className="w-3.5 h-3.5 fill-white" />}
                <span>{isPlaying ? 'Dừng phát' : 'Nghe thử'}</span>
              </button>
            </div>

            {/* Dynamic Waveform Panel */}
            <div className="h-16 bg-zinc-950 rounded-lg border border-zinc-850 p-2.5 flex flex-col justify-between relative overflow-hidden">
              <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-wider block">Phổ âm dao động (Waveform)</span>
              
              <div className="flex items-end justify-center gap-[3px] h-9">
                {Array.from({ length: 44 }).map((_, i) => (
                  <div
                    key={i}
                    className={`w-[2.5px] rounded-t transition-all ${
                      isPlaying ? 'bg-orange-500 animate-pulse' : 'bg-zinc-800'
                    }`}
                    style={{
                      height: isPlaying ? `${15 + Math.random() * 85}%` : '5px',
                      animationDuration: isPlaying ? `${0.2 + Math.random() * 0.8}s` : '0s'
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right rack: Python SDK integrations */}
        <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl flex flex-col justify-between shadow-xl min-h-[350px]">
          <div className="space-y-3.5 flex-1">
            <div className="flex items-center justify-between border-b border-zinc-850 pb-2.5">
              <span className="text-xs font-bold text-zinc-300 uppercase tracking-widest flex items-center gap-1.5">
                <Code className="w-4 h-4 text-orange-500" />
                <span>Mã nguồn Python ghép cục bộ</span>
              </span>
              <button
                onClick={copyCode}
                className="text-[10px] font-bold text-orange-500 hover:text-orange-400 flex items-center gap-1 bg-orange-500/10 border border-orange-500/20 px-2 py-1 rounded transition-all cursor-pointer"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : null}
                {copied ? 'Đã sao chép' : 'Sao chép mã'}
              </button>
            </div>

            <pre className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 text-[10px] text-emerald-400 font-mono leading-relaxed overflow-x-auto max-h-[220px] overflow-y-auto">
              {fishSpeechPythonCode}
            </pre>
          </div>

          <div className="bg-orange-500/5 border border-orange-500/15 rounded-lg p-3.5 text-xs text-orange-300 leading-relaxed flex gap-2.5 mt-4">
            <Activity className="w-4 h-4 text-orange-500 shrink-0 mt-0.5" />
            <span className="font-sans">
              <strong>Hợp tác cục bộ:</strong> Đảm bảo Docker Fish Speech hoặc Python virtualenv đang khởi chạy trên cổng mặc định localhost:8000. Bạn cũng có thể tải các giọng đọc tùy biến (voice clone) từ định dạng tệp .wav ngắn 3 giây để bắt chước bất kỳ reviewer nổi tiếng nào.
            </span>
          </div>
        </div>

      </div>
    </div>
  );
};
