import React, { useState, useEffect } from 'react';
import { MarketingScript, VideoScene, VoiceSettings } from '../types';
import {
  Smartphone, Volume2, Subtitles, AlignLeft, Info, Play, Square, Settings, Database, Sliders
} from 'lucide-react';

interface PreviewPanelProps {
  script: MarketingScript | null;
  selectedSceneId: string;
  onSelectScene: (id: string) => void;
  voiceSettings: VoiceSettings;
  onUpdateVoiceSettings: (settings: VoiceSettings) => void;
  isPlaying: boolean;
  onPlayToggle: () => void;
}

type TabType = 'video' | 'audio' | 'subtitle' | 'timeline' | 'metadata';

export const PreviewPanel: React.FC<PreviewPanelProps> = ({
  script,
  selectedSceneId,
  onSelectScene,
  voiceSettings,
  onUpdateVoiceSettings,
  isPlaying,
  onPlayToggle
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('video');

  const selectedScene = script?.scenes.find(s => s.id === selectedSceneId) || script?.scenes[0];

  const calculateTotalWords = () => {
    if (!script) return 0;
    return script.scenes.reduce((acc, s) => acc + s.voiceover.split(/\s+/).filter(Boolean).length, 0);
  };

  return (
    <div className="w-80 bg-zinc-950 border-l border-zinc-800 flex flex-col h-full shrink-0 select-none overflow-hidden">
      {/* Tabs list */}
      <div className="grid grid-cols-5 border-b border-zinc-800 bg-zinc-950/60 p-1 gap-0.5 shrink-0">
        {[
          { key: 'video', label: 'Video', icon: Smartphone },
          { key: 'audio', label: 'Audio', icon: Volume2 },
          { key: 'subtitle', label: 'Sub', icon: Subtitles },
          { key: 'timeline', label: 'Track', icon: AlignLeft },
          { key: 'metadata', label: 'Meta', icon: Info },
        ].map(tab => {
          const Icon = tab.icon;
          const isSelected = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as TabType)}
              className={`py-2 text-[10px] font-semibold rounded flex flex-col items-center justify-center gap-1 transition-all cursor-pointer ${
                isSelected
                  ? 'bg-zinc-900 text-orange-500 border border-zinc-800'
                  : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/40'
              }`}
              title={tab.label}
            >
              <Icon className="w-3.5 h-3.5" />
              <span className="text-[9px] scale-[0.9]">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Dynamic Tab Body */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col justify-between">
        {script ? (
          <>
            {/* VIDEO PREVIEW */}
            {activeTab === 'video' && (
              <div className="space-y-4 flex flex-col items-center flex-1 justify-center">
                <div className="w-[220px] h-[390px] rounded-[32px] bg-black border-4 border-zinc-800 p-2 shadow-2xl relative flex flex-col overflow-hidden ring-1 ring-zinc-800/50">
                  {/* Phone speaker notch */}
                  <div className="absolute top-2.5 left-1/2 -translate-x-1/2 w-16 h-3 bg-zinc-800 rounded-full z-20 flex items-center justify-center">
                    <div className="w-6 h-0.5 bg-zinc-900 rounded-full" />
                  </div>

                  {/* Simulator Screen Body */}
                  <div className="flex-1 rounded-[24px] bg-zinc-900 relative overflow-hidden flex flex-col justify-end p-3 z-10 select-none">
                    {/* Simulated Background */}
                    <div className="absolute inset-0 bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 flex items-center justify-center text-center p-3">
                      {/* Dynamic Light Sphere */}
                      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-24 h-24 bg-orange-500/10 rounded-full blur-2xl animate-pulse" />
                      
                      <div className="space-y-2 z-10 opacity-80">
                        <span className="text-[8px] font-mono tracking-widest text-orange-500 bg-orange-500/10 px-2 py-0.5 rounded-full border border-orange-500/20">
                          {script.hookType.toUpperCase()}
                        </span>
                        <div className="text-[9px] text-zinc-400 leading-relaxed font-mono px-1 select-none pointer-events-none line-clamp-5">
                          {selectedScene?.visualAction || 'Bắt đầu phân cảnh...'}
                        </div>
                      </div>
                    </div>

                    {/* Left TikTok Controls Overlay */}
                    <div className="absolute right-1.5 bottom-20 flex flex-col gap-2.5 items-center z-20">
                      <div className="w-6 h-6 rounded-full bg-zinc-950/60 border border-zinc-800 flex items-center justify-center text-zinc-300 text-[8px] cursor-pointer hover:bg-zinc-800 transition-all">❤️</div>
                      <div className="w-6 h-6 rounded-full bg-zinc-950/60 border border-zinc-800 flex items-center justify-center text-zinc-300 text-[8px] cursor-pointer hover:bg-zinc-800 transition-all">💬</div>
                      <div className="w-6 h-6 rounded-full bg-zinc-950/60 border border-zinc-800 flex items-center justify-center text-zinc-300 text-[8px] cursor-pointer hover:bg-zinc-800 transition-all">⭐️</div>
                    </div>

                    {/* Content Overlays */}
                    <div className="z-20 space-y-2.5 mt-auto">
                      <div className="space-y-0.5">
                        <div className="text-[10px] font-bold text-white flex items-center gap-1">
                          <span>@marketing.studio</span>
                          <span className="px-1 py-0.2 bg-orange-600 text-white rounded-[2px] text-[7px] font-black">AI</span>
                        </div>
                        <div className="text-[8px] text-zinc-300 max-w-[140px] truncate font-mono">
                          🔊 {selectedScene?.sfxAudio || 'Học máy rà tiếng...'}
                        </div>
                      </div>

                      {/* Styled Subtitle Overlay */}
                      <div className="bg-black/60 backdrop-blur-md border border-zinc-800 rounded p-2 text-center shadow-lg shadow-black/40">
                        <span className="text-amber-400 font-black text-xs tracking-wide drop-shadow-[0_1.5px_1.5px_rgba(0,0,0,1)] uppercase font-sans leading-tight block">
                          {selectedScene?.subtitle || 'Văn bản kịch bản'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Subtitle / Play Control row */}
                <div className="w-full flex items-center justify-between bg-zinc-900 border border-zinc-800 rounded-lg p-2 gap-2">
                  <div className="truncate flex-1">
                    <span className="text-[9px] font-mono text-zinc-500 block">PHÂN CẢNH HIỆN TẠI</span>
                    <span className="text-xs text-zinc-300 truncate font-semibold block">{selectedScene?.timecode || '00:00'}</span>
                  </div>
                  <button
                    onClick={onPlayToggle}
                    className={`py-1.5 px-3 rounded text-xs font-bold flex items-center gap-1 cursor-pointer transition-all ${
                      isPlaying
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : 'bg-orange-600 text-white hover:bg-orange-500'
                    }`}
                  >
                    {isPlaying ? <Square className="w-3.5 h-3.5 fill-red-400" /> : <Play className="w-3.5 h-3.5 fill-white" />}
                    <span>{isPlaying ? 'Dừng' : 'Nghe'}</span>
                  </button>
                </div>
              </div>
            )}

            {/* AUDIO CONFIG */}
            {activeTab === 'audio' && (
              <div className="space-y-4 flex-1">
                <div className="bg-zinc-900/60 p-3 rounded-lg border border-zinc-800 space-y-3">
                  <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-1">
                    <Settings className="w-3.5 h-3.5 text-orange-500" />
                    <span>Bộ cấu hình giọng nói</span>
                  </h4>

                  {/* Speaker */}
                  <div className="space-y-1">
                    <label className="text-[10px] text-zinc-400 block">Mẫu giọng phát:</label>
                    <select
                      value={voiceSettings.speaker}
                      onChange={(e) => onUpdateVoiceSettings({ ...voiceSettings, speaker: e.target.value as any })}
                      className="w-full bg-zinc-950 border border-zinc-800 text-xs text-zinc-300 rounded px-2 py-1.5 focus:outline-none focus:border-orange-500"
                    >
                      <option value="vi-female-warm">Nữ Miền Bắc (Trầm ấm)</option>
                      <option value="vi-male-natural">Nam Miền Bắc (Phòng thu)</option>
                      <option value="vi-female-hype">Nữ Miền Nam (Tốc độ, TikTok)</option>
                      <option value="vi-male-hype">Nam Miền Nam (Sôi động)</option>
                    </select>
                  </div>

                  {/* Speed */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-zinc-400">
                      <span>Tốc độ đọc:</span>
                      <span className="text-orange-500 font-mono">{voiceSettings.speed}x</span>
                    </div>
                    <input
                      type="range"
                      min="0.8"
                      max="1.5"
                      step="0.1"
                      value={voiceSettings.speed}
                      onChange={(e) => onUpdateVoiceSettings({ ...voiceSettings, speed: parseFloat(e.target.value) })}
                      className="w-full accent-orange-500 h-1 bg-zinc-850 rounded"
                    />
                  </div>

                  {/* Pitch */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-[10px] text-zinc-400">
                      <span>Cao độ giọng:</span>
                      <span className="text-orange-500 font-mono">{voiceSettings.pitch}x</span>
                    </div>
                    <input
                      type="range"
                      min="0.8"
                      max="1.2"
                      step="0.05"
                      value={voiceSettings.pitch}
                      onChange={(e) => onUpdateVoiceSettings({ ...voiceSettings, pitch: parseFloat(e.target.value) })}
                      className="w-full accent-orange-500 h-1 bg-zinc-850 rounded"
                    />
                  </div>
                </div>

                {/* Animated visual audio equalizer */}
                <div className="h-28 bg-zinc-950 border border-zinc-800 rounded-lg p-3 flex flex-col justify-between">
                  <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest block">Phổ âm thanh</span>
                  <div className="flex items-end justify-center gap-[4px] h-16">
                    {Array.from({ length: 15 }).map((_, i) => (
                      <div
                        key={i}
                        className={`w-[4px] rounded-t transition-all ${isPlaying ? 'bg-orange-500 animate-pulse' : 'bg-zinc-800'}`}
                        style={{
                          height: isPlaying ? `${10 + Math.random() * 80}%` : '6px',
                          animationDuration: isPlaying ? `${0.3 + Math.random() * 0.7}s` : '0s'
                        }}
                      />
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* SUBTITLE PREVIEW */}
            {activeTab === 'subtitle' && (
              <div className="space-y-4 flex-1">
                <div className="bg-zinc-900/60 p-3 rounded-lg border border-zinc-800 space-y-3">
                  <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-1">
                    <Subtitles className="w-3.5 h-3.5 text-orange-500" />
                    <span>Lớp phụ đề chạy</span>
                  </h4>
                  <div className="bg-zinc-950 p-2.5 rounded border border-zinc-800 text-xs font-mono text-amber-400 min-h-16 flex items-center justify-center text-center">
                    "{selectedScene?.subtitle || 'Chưa chọn phân cảnh'}"
                  </div>
                </div>

                <div className="bg-zinc-900/40 p-3 rounded-lg border border-zinc-800 space-y-2 text-xs">
                  <span className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider block">Thiết lập kiểu hiển thị</span>
                  <div className="space-y-1.5 text-zinc-400">
                    <div className="flex justify-between">
                      <span>Cỡ chữ biên tập:</span>
                      <span className="text-zinc-200">24px (Mặc định)</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Màu chính:</span>
                      <span className="text-amber-400 font-bold">Vàng chanh</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Hiệu ứng đổ bóng:</span>
                      <span className="text-zinc-200">Khối đen dày</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TIMELINE TRACKS */}
            {activeTab === 'timeline' && (
              <div className="space-y-3 flex-1 overflow-y-auto max-h-[300px]">
                <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest block mb-2">Trình tự phân cảnh</span>
                {script.scenes.map((sc, index) => {
                  const isSelected = selectedSceneId === sc.id;
                  return (
                    <div
                      key={sc.id}
                      onClick={() => onSelectScene(sc.id)}
                      className={`p-2.5 rounded border text-left cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-orange-500/10 border-orange-500/40 text-orange-500'
                          : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200'
                      }`}
                    >
                      <div className="flex justify-between items-center text-[10px] font-mono font-bold mb-1">
                        <span>CẢNH {index + 1}</span>
                        <span className="opacity-80">{sc.timecode}</span>
                      </div>
                      <p className="text-xs truncate font-sans">{sc.subtitle}</p>
                    </div>
                  );
                })}
              </div>
            )}

            {/* METADATA */}
            {activeTab === 'metadata' && (
              <div className="space-y-3 flex-1 text-xs text-zinc-400">
                <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest block">Thống số kịch bản video</span>
                
                <div className="bg-zinc-900/60 p-3 rounded-lg border border-zinc-800 space-y-2">
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Độ phân giải dọc:</span>
                    <span className="text-zinc-200 font-mono">1080 x 1920 (9:16)</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Định dạng file xuất:</span>
                    <span className="text-zinc-200 font-mono">MP4 container</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Codec nén hình:</span>
                    <span className="text-zinc-200 font-mono">h264_nvenc (Hardware GPU)</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Số phân cảnh:</span>
                    <span className="text-zinc-200 font-mono font-semibold">{script.scenes.length}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-zinc-800/60">
                    <span className="text-zinc-500">Tổng số từ (speech):</span>
                    <span className="text-zinc-200 font-mono font-semibold">{calculateTotalWords()} từ</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-zinc-500">Ước tính tệp nén:</span>
                    <span className="text-emerald-400 font-mono">~12.4 MB (30s)</span>
                  </div>
                </div>

                <div className="bg-zinc-900/30 p-2.5 rounded border border-zinc-800/40 text-[10px] leading-relaxed flex items-center gap-1.5 text-zinc-500 font-mono">
                  <Database className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
                  <span>Mô hình: gemini-3.5-flash-001 (context: 1M tokens)</span>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-4 text-zinc-500">
            <Smartphone className="w-10 h-10 text-zinc-700 mb-2 animate-pulse" />
            <p className="text-xs">Chưa có kịch bản hoạt động</p>
            <p className="text-[10px] text-zinc-600 mt-1 max-w-[150px]">Hãy nhập thông tin sản phẩm và chạy Gemini để kích hoạt trình mô phỏng.</p>
          </div>
        )}

        {/* Bottom context indicator */}
        <div className="pt-3 border-t border-zinc-900 text-[9px] font-mono text-zinc-600 flex justify-between items-center shrink-0">
          <span>WORKSPACE PREVIEW</span>
          <span>AIMS-V1.2</span>
        </div>
      </div>
    </div>
  );
};
