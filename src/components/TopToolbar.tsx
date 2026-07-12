import React from 'react';
import { Video, Cpu, RefreshCw, Download, Upload, HelpCircle } from 'lucide-react';

interface TopToolbarProps {
  currentProjectName: string;
  engineStatus: {
    gemini: 'active' | 'inactive';
    fishSpeech: 'active' | 'inactive';
    ffmpeg: 'active' | 'inactive';
  };
  onNewProject: () => void;
  onImport: () => void;
  onExport: () => void;
}

export const TopToolbar: React.FC<TopToolbarProps> = ({
  currentProjectName,
  engineStatus,
  onNewProject,
  onImport,
  onExport
}) => {
  return (
    <header className="h-14 bg-zinc-950 border-b border-zinc-800 flex items-center justify-between px-4 shrink-0 select-none">
      {/* Brand Logo & Name */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-gradient-to-br from-orange-600 to-orange-500 rounded-lg flex items-center justify-center font-black text-sm italic text-white shadow-md shadow-orange-600/20">
          M
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold font-mono tracking-[0.15em] text-zinc-500">AIMS-PRO</span>
            <span className="w-1 h-1 rounded-full bg-zinc-700" />
            <span className="text-[11px] font-mono text-orange-500 bg-orange-500/10 px-1.5 py-0.2 rounded border border-orange-500/20 uppercase font-semibold">
              Desktop Workspace
            </span>
          </div>
          <h1 className="text-sm font-semibold tracking-tight text-zinc-100 flex items-center gap-1">
            AI MARKETING STUDIO <span className="font-black italic text-orange-500">PRO</span>
          </h1>
        </div>
      </div>

      {/* Middle Current Project */}
      <div className="hidden md:flex items-center gap-2 px-3 py-1 bg-zinc-900 border border-zinc-800 rounded-lg max-w-xs lg:max-w-md">
        <Video className="w-3.5 h-3.5 text-zinc-400" />
        <span className="text-xs text-zinc-400 font-medium">Dự án hiện tại:</span>
        <span className="text-xs text-zinc-100 font-semibold truncate max-w-[120px] lg:max-w-[200px]">
          {currentProjectName || 'Chưa lưu dự án'}
        </span>
      </div>

      {/* Right Controls & Status */}
      <div className="flex items-center gap-4">
        {/* Actions */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={onNewProject}
            className="h-8 px-2.5 rounded bg-orange-600 hover:bg-orange-500 text-white text-xs font-medium transition-all flex items-center gap-1.5 shadow-sm shadow-orange-600/10 active:scale-95 cursor-pointer"
          >
            Tạo Mới
          </button>
          <button
            onClick={onImport}
            className="h-8 px-2 rounded hover:bg-zinc-800 border border-zinc-800 text-zinc-300 text-xs font-medium transition-all flex items-center gap-1 active:scale-95 cursor-pointer"
            title="Nhập kịch bản JSON"
          >
            <Upload className="w-3.5 h-3.5" />
            <span className="hidden lg:inline">Nhập</span>
          </button>
          <button
            onClick={onExport}
            className="h-8 px-2 rounded hover:bg-zinc-800 border border-zinc-800 text-zinc-300 text-xs font-medium transition-all flex items-center gap-1 active:scale-95 cursor-pointer"
            title="Xuất kịch bản / code"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden lg:inline">Xuất</span>
          </button>
        </div>

        <div className="h-4 w-[1px] bg-zinc-800" />

        {/* Engine status indicators */}
        <div className="flex items-center gap-3">
          {/* Gemini */}
          <div className="flex items-center gap-1.5" title="Google Gemini 3.5 API Status">
            <span className={`w-1.5 h-1.5 rounded-full ${engineStatus.gemini === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-[10px] font-mono text-zinc-400 font-semibold uppercase">Gemini</span>
          </div>

          {/* Fish Speech */}
          <div className="flex items-center gap-1.5" title="Fish Speech TTS Local Engine Status">
            <span className={`w-1.5 h-1.5 rounded-full ${engineStatus.fishSpeech === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-zinc-600'}`} />
            <span className="text-[10px] font-mono text-zinc-400 font-semibold uppercase">TTS</span>
          </div>

          {/* FFmpeg */}
          <div className="flex items-center gap-1.5" title="FFmpeg / FFprobe Native Binaries Status">
            <span className={`w-1.5 h-1.5 rounded-full ${engineStatus.ffmpeg === 'active' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-[10px] font-mono text-zinc-400 font-semibold uppercase">FFmpeg</span>
          </div>
        </div>
      </div>
    </header>
  );
};
