import React, { useState } from 'react';
import { MarketingScript, VideoScene } from '../types';
import {
  Subtitles, Sliders, Layout, Download, Check, AlignCenter, Layers, AlertCircle, RefreshCw
} from 'lucide-react';

interface SubtitleViewProps {
  script: MarketingScript | null;
  selectedSceneId: string;
  onSelectScene: (id: string) => void;
  onUpdateScene: (sceneId: string, updatedFields: Partial<VideoScene>) => void;
}

export const SubtitleView: React.FC<SubtitleViewProps> = ({
  script,
  selectedSceneId,
  onSelectScene,
  onUpdateScene,
}) => {
  const [copied, setCopied] = useState<'srt' | 'ass' | null>(null);
  const [fontFamily, setFontFamily] = useState<string>('font-sans');
  const [fontSize, setFontSize] = useState<number>(24);
  const [fontColor, setFontColor] = useState<string>('text-amber-400');
  const [strokeColor, setStrokeColor] = useState<string>('black');
  const [safeZone, setSafeZone] = useState<boolean>(true);

  if (!script) {
    return (
      <div className="border border-dashed border-zinc-800 rounded-2xl p-16 text-center text-zinc-500 bg-zinc-900/10 flex flex-col items-center justify-center min-h-[350px]">
        <Subtitles className="w-12 h-12 text-zinc-700 mb-4 animate-pulse" />
        <h3 className="text-sm font-semibold text-zinc-300">Chưa có kịch bản chạy phụ đề</h3>
        <p className="text-[10px] text-zinc-500 mt-1 max-w-sm">
          Nhập thông tin sản phẩm và chạy Gemini để tạo kịch bản. Dòng phụ đề sẽ tự động ánh xạ đồng bộ.
        </p>
      </div>
    );
  }

  const selectedScene = script.scenes.find(s => s.id === selectedSceneId) || script.scenes[0];

  // Helper to compile a basic SRT string
  const compileSRT = () => {
    return script.scenes.map((sc, idx) => {
      const times = sc.timecode.split(' - ');
      const start = `00:00:${times[0]?.trim() || '00'},000`;
      const end = `00:00:${times[1]?.trim() || '05'},000`;
      return `${idx + 1}\n${start} --> ${end}\n${sc.subtitle}\n\n`;
    }).join('').trim();
  };

  // Helper to compile basic ASS string
  const compileASS = () => {
    const header = `[Script Info]\nTitle: AIMS Pro Subtitles\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, BackColour, OutlineColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,64,&H0000FFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,1,2,10,10,10,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n`;
    const events = script.scenes.map((sc) => {
      const times = sc.timecode.split(' - ');
      const start = `0:00:${times[0]?.trim() || '00'}.00`;
      const end = `0:00:${times[1]?.trim() || '05'}.00`;
      return `Dialogue: 0,${start},${end},Default,,0,0,0,,${sc.subtitle}`;
    }).join('\n');
    return header + events;
  };

  const copySubtitleText = (format: 'srt' | 'ass') => {
    const text = format === 'srt' ? compileSRT() : compileASS();
    navigator.clipboard.writeText(text);
    setCopied(format);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="space-y-6 animate-fadeIn select-none">
      
      {/* Horizontal timeline track segment */}
      <div className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl space-y-3.5 shadow-md">
        <div className="flex justify-between items-center border-b border-zinc-850 pb-2">
          <span className="text-[10px] font-mono font-bold text-zinc-400 uppercase tracking-widest block">
            Thước đo dòng thời gian (Subtitle timeline tracks)
          </span>
          <span className="text-[10px] text-zinc-500 font-mono">0.00s - {script.totalDuration}.00s</span>
        </div>
        
        {/* Timeline Tracks ruler */}
        <div className="relative h-12 bg-zinc-950 border border-zinc-800 rounded-lg flex items-center p-1 overflow-x-auto">
          {script.scenes.map((sc, index) => {
            const isSelected = selectedSceneId === sc.id;
            return (
              <div
                key={sc.id}
                onClick={() => onSelectScene(sc.id)}
                className={`h-full rounded text-center cursor-pointer flex flex-col justify-center transition-all px-2 border shrink-0 ${
                  isSelected
                    ? 'bg-orange-600/10 border-orange-500/40 text-orange-500'
                    : 'bg-zinc-900 border-zinc-850 text-zinc-500 hover:text-zinc-300'
                }`}
                style={{ width: `${100 / script.scenes.length}%`, minWidth: '80px' }}
              >
                <span className="text-[9px] font-mono font-black block">CẢNH {index + 1}</span>
                <span className="text-[8px] font-mono block opacity-80">{sc.timecode}</span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left Side: Subtitle List & Inline Edit */}
        <div className="lg:col-span-4 bg-zinc-900 border border-zinc-850 rounded-xl p-4.5 space-y-4 h-[420px] overflow-y-auto">
          <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block border-b border-zinc-850 pb-2">
            Biên tập dòng thoại
          </span>
          
          <div className="space-y-3.5">
            {script.scenes.map((scene, idx) => {
              const isSelected = selectedSceneId === scene.id;
              return (
                <div
                  key={scene.id}
                  onClick={() => onSelectScene(scene.id)}
                  className={`p-3 rounded-lg border text-xs text-left transition-all space-y-2 cursor-pointer ${
                    isSelected
                      ? 'bg-zinc-800 border-orange-500/30'
                      : 'bg-zinc-950/60 border-zinc-850 hover:bg-zinc-850'
                  }`}
                >
                  <div className="flex justify-between items-center text-[10px] font-mono text-zinc-400">
                    <span className="font-bold text-zinc-300">Phân cảnh #{idx + 1}</span>
                    <input
                      type="text"
                      value={scene.timecode}
                      onClick={(e) => e.stopPropagation()}
                      onChange={(e) => onUpdateScene(scene.id, { timecode: e.target.value })}
                      className="w-16 bg-zinc-950 border border-zinc-850 text-center text-[10px] rounded focus:outline-none focus:border-orange-500"
                    />
                  </div>
                  <input
                    type="text"
                    value={scene.subtitle}
                    onClick={(e) => e.stopPropagation()}
                    onChange={(e) => onUpdateScene(scene.id, { subtitle: e.target.value })}
                    className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-orange-500 text-xs font-sans"
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* Center: Style and Preview pane */}
        <div className="lg:col-span-5 bg-zinc-900 border border-zinc-850 rounded-xl p-5 flex flex-col justify-between h-[420px]">
          
          {/* Subtitle Visual Simulator */}
          <div className="space-y-4 flex-1">
            <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block border-b border-zinc-850 pb-2">
              Xem thử phong cách phụ đề (Visual Preview)
            </span>

            <div className="relative w-full h-44 rounded-lg bg-zinc-950 border border-zinc-800 overflow-hidden flex flex-col justify-end p-4">
              {/* Grid Safe zone guidelines */}
              {safeZone && (
                <div className="absolute inset-x-2 inset-y-4 border border-dashed border-red-500/20 rounded pointer-events-none flex flex-col justify-between p-1 select-none">
                  <span className="text-[7px] font-mono text-red-500/30">LỀ AN TOÀN TRÊN (SAFE ZONE TOP)</span>
                  <span className="text-[7px] font-mono text-red-500/30 text-right">LỀ AN TOÀN DƯỚI (SAFE ZONE BOTTOM)</span>
                </div>
              )}

              {/* Glowing center sphere */}
              <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-16 h-16 bg-orange-500/5 rounded-full blur-xl pointer-events-none" />

              {/* The Styled overlay text */}
              <div className="z-10 text-center bg-black/40 backdrop-blur-sm p-3.5 rounded border border-zinc-900 shadow-xl max-w-[90%] mx-auto">
                <p className={`font-black tracking-wide uppercase drop-shadow-[0_2px_2px_rgba(0,0,0,1)] select-none leading-tight ${fontFamily} ${fontSize === 20 ? 'text-xs' : fontSize === 24 ? 'text-sm' : 'text-base'} ${fontColor}`}>
                  {selectedScene?.subtitle || 'Chưa viết phụ đề'}
                </p>
              </div>
            </div>

            {/* Quick helper toggles */}
            <div className="flex justify-between items-center text-xs text-zinc-400 bg-zinc-950/60 p-2.5 rounded border border-zinc-850">
              <span className="flex items-center gap-1.5 font-sans">
                <AlertCircle className="w-3.5 h-3.5 text-zinc-500" />
                Vùng an toàn TikTok (tránh nút thả tim, cmt)
              </span>
              <button
                onClick={() => setSafeZone(!safeZone)}
                className={`px-2 py-0.5 text-[10px] font-bold rounded transition-all cursor-pointer ${
                  safeZone ? 'bg-orange-500/10 text-orange-500 border border-orange-500/20' : 'bg-zinc-800 text-zinc-400'
                }`}
              >
                {safeZone ? 'Bật' : 'Tắt'}
              </button>
            </div>
          </div>

          {/* Style modifiers rack */}
          <div className="grid grid-cols-3 gap-2.5 pt-3 border-t border-zinc-850 mt-4 shrink-0">
            {/* Fonts */}
            <div className="space-y-1">
              <span className="text-[8px] font-mono font-bold text-zinc-500 uppercase block">Phông chữ</span>
              <select
                value={fontFamily}
                onChange={(e) => setFontFamily(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-300 text-[10px] rounded px-1.5 py-1 focus:outline-none"
              >
                <option value="font-sans">Inter (Thanh lịch)</option>
                <option value="font-mono">JetBrains Mono</option>
              </select>
            </div>

            {/* Font size */}
            <div className="space-y-1">
              <span className="text-[8px] font-mono font-bold text-zinc-500 uppercase block">Cỡ chữ</span>
              <select
                value={fontSize}
                onChange={(e) => setFontSize(parseInt(e.target.value))}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-300 text-[10px] rounded px-1.5 py-1 focus:outline-none"
              >
                <option value={20}>20px (Nhỏ)</option>
                <option value={24}>24px (Vừa)</option>
                <option value={28}>28px (Lớn)</option>
              </select>
            </div>

            {/* Colors */}
            <div className="space-y-1">
              <span className="text-[8px] font-mono font-bold text-zinc-500 uppercase block">Màu chữ</span>
              <select
                value={fontColor}
                onChange={(e) => setFontColor(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-300 text-[10px] rounded px-1.5 py-1 focus:outline-none"
              >
                <option value="text-amber-400">Vàng chanh</option>
                <option value="text-white">Trắng tuyết</option>
                <option value="text-orange-500">Cam rực rỡ</option>
              </select>
            </div>
          </div>
        </div>

        {/* Right Side: ASS / SRT Code Exporter */}
        <div className="lg:col-span-3 bg-zinc-900 border border-zinc-850 rounded-xl p-4.5 flex flex-col justify-between h-[420px]">
          <div className="space-y-4 flex-1">
            <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block border-b border-zinc-850 pb-2">
              Xuất tệp phụ đề rời
            </span>

            {/* SRT box */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-[10px] font-mono">
                <span className="text-zinc-400 font-bold">TẬP SRT PHỔ BIẾN</span>
                <button
                  onClick={() => copySubtitleText('srt')}
                  className="text-orange-500 hover:text-orange-400 font-bold flex items-center gap-1 cursor-pointer"
                >
                  {copied === 'srt' ? <Check className="w-3 h-3" /> : null}
                  {copied === 'srt' ? 'Xong' : 'Copy'}
                </button>
              </div>
              <pre className="bg-zinc-950 p-2.5 rounded border border-zinc-850 text-[9px] font-mono text-zinc-500 overflow-x-auto max-h-[110px] leading-normal">
                {compileSRT()}
              </pre>
            </div>

            {/* ASS box */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-[10px] font-mono">
                <span className="text-zinc-400 font-bold">KỸ THUẬT SỐ ASS STYLED</span>
                <button
                  onClick={() => copySubtitleText('ass')}
                  className="text-orange-500 hover:text-orange-400 font-bold flex items-center gap-1 cursor-pointer"
                >
                  {copied === 'ass' ? <Check className="w-3 h-3" /> : null}
                  {copied === 'ass' ? 'Xong' : 'Copy'}
                </button>
              </div>
              <pre className="bg-zinc-950 p-2.5 rounded border border-zinc-850 text-[9px] font-mono text-zinc-500 overflow-x-auto max-h-[120px] leading-normal">
                {compileASS()}
              </pre>
            </div>
          </div>

          <div className="bg-zinc-950/40 p-2.5 border border-zinc-850/60 rounded text-[9px] text-zinc-500 font-mono leading-normal flex items-center gap-2 mt-4">
            <Download className="w-3.5 h-3.5 text-zinc-600 shrink-0" />
            <span>Mã phụ đề sẽ tự động tích hợp chèn cứng lên khung video thông qua lệnh FFmpeg drawtext / sub.</span>
          </div>
        </div>

      </div>
    </div>
  );
};
