import React from 'react';
import {
  SlidersHorizontal, Sparkles, Volume2, Video, Download, ArrowRight, Activity, Cpu
} from 'lucide-react';

export const WorkflowView: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn select-none">
      {/* Intro info bar */}
      <div className="bg-zinc-950 border border-zinc-800 p-4 rounded-xl flex items-center justify-between shadow-md">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-orange-600/15 text-orange-500 rounded">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-zinc-200">Sơ đồ khối luồng biên dịch (AIMS Pipeline)</h3>
            <p className="text-[10px] text-zinc-500">Mô tả quy trình xử lý dữ liệu tự động từ sản phẩm đầu vào đến tệp MP4 nén cuối cùng</p>
          </div>
        </div>
        <span className="text-[9px] font-mono font-bold text-sky-400 bg-sky-500/10 border border-sky-500/20 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
          Node-based logic
        </span>
      </div>

      {/* SVG Connected Nodes visual flow */}
      <div className="bg-zinc-900 border border-zinc-850 p-6 rounded-2xl relative overflow-hidden flex flex-col items-center justify-center min-h-[420px] shadow-2xl">
        {/* Background circuit grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1f1f23_1px,transparent_1px),linear-gradient(to_bottom,#1f1f23_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />

        {/* Dynamic Connected Pipeline */}
        <div className="relative flex flex-col md:flex-row items-center justify-between w-full max-w-4xl gap-8 md:gap-4 z-10">
          
          {/* Node 1: User parameters */}
          <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 w-48 text-center space-y-2.5 shadow-lg hover:border-orange-500/30 transition-all">
            <div className="mx-auto w-8 h-8 rounded bg-orange-600/10 text-orange-500 flex items-center justify-center border border-orange-500/20">
              <SlidersHorizontal className="w-4 h-4" />
            </div>
            <div className="space-y-0.5">
              <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">NODE 01</span>
              <h4 className="text-xs font-bold text-zinc-200">Product Config</h4>
              <p className="text-[10px] text-zinc-500 font-sans">Brand, pain point, promo parameters</p>
            </div>
            <div className="text-[9px] font-mono bg-zinc-900 border border-zinc-800 text-zinc-400 py-1 rounded">
              Ready
            </div>
          </div>

          <div className="hidden md:block text-zinc-600 shrink-0">
            <ArrowRight className="w-5 h-5 text-orange-500 animate-pulse" />
          </div>

          {/* Node 2: Gemini AI */}
          <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 w-48 text-center space-y-2.5 shadow-lg hover:border-orange-500/30 transition-all">
            <div className="mx-auto w-8 h-8 rounded bg-[#3B82F6]/10 text-[#3B82F6] flex items-center justify-center border border-[#3B82F6]/20">
              <Sparkles className="w-4 h-4 fill-[#3B82F6]" />
            </div>
            <div className="space-y-0.5">
              <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">NODE 02</span>
              <h4 className="text-xs font-bold text-zinc-200">Gemini AI Planner</h4>
              <p className="text-[10px] text-zinc-500 font-sans">Hooks, scenes & layout compiler</p>
            </div>
            <div className="text-[9px] font-mono bg-[#3B82F6]/10 border border-[#3B82F6]/20 text-[#3B82F6] py-1 rounded font-bold">
              Active
            </div>
          </div>

          <div className="hidden md:block text-zinc-600 shrink-0">
            <ArrowRight className="w-5 h-5 text-orange-500 animate-pulse" />
          </div>

          {/* Node 3: Fish TTS */}
          <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 w-48 text-center space-y-2.5 shadow-lg hover:border-orange-500/30 transition-all">
            <div className="mx-auto w-8 h-8 rounded bg-pink-500/10 text-pink-500 flex items-center justify-center border border-pink-500/20">
              <Volume2 className="w-4 h-4" />
            </div>
            <div className="space-y-0.5">
              <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">NODE 03</span>
              <h4 className="text-xs font-bold text-zinc-200">Fish TTS Synth</h4>
              <p className="text-[10px] text-zinc-500 font-sans">Voice acting local synthesis</p>
            </div>
            <div className="text-[9px] font-mono bg-zinc-900 border border-zinc-800 text-zinc-400 py-1 rounded">
              Ready
            </div>
          </div>

          <div className="hidden md:block text-zinc-600 shrink-0">
            <ArrowRight className="w-5 h-5 text-orange-500 animate-pulse" />
          </div>

          {/* Node 4: FFmpeg Concat */}
          <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-4 w-48 text-center space-y-2.5 shadow-lg hover:border-orange-500/30 transition-all">
            <div className="mx-auto w-8 h-8 rounded bg-emerald-500/10 text-emerald-500 flex items-center justify-center border border-emerald-500/20">
              <Video className="w-4 h-4" />
            </div>
            <div className="space-y-0.5">
              <span className="text-[8px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">NODE 04</span>
              <h4 className="text-xs font-bold text-zinc-200">FFmpeg Burn-In</h4>
              <p className="text-[10px] text-zinc-500 font-sans">Video, audio & style rendering</p>
            </div>
            <div className="text-[9px] font-mono bg-zinc-900 border border-zinc-800 text-zinc-400 py-1 rounded">
              Ready
            </div>
          </div>

        </div>

        {/* Node pipeline specs details table */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 w-full max-w-4xl border-t border-zinc-800 mt-10 pt-6">
          <div className="space-y-0.5 text-center sm:text-left">
            <span className="text-[8px] font-mono text-zinc-500 uppercase block font-bold">Cổng API Lập Kịch Bản</span>
            <span className="text-xs text-zinc-300 font-mono font-semibold">Gemini 3.5 API</span>
          </div>
          <div className="space-y-0.5 text-center sm:text-left">
            <span className="text-[8px] font-mono text-zinc-500 uppercase block font-bold">Bộ giọng đọc thuần Việt</span>
            <span className="text-xs text-zinc-300 font-mono font-semibold">Fish-Speech Local</span>
          </div>
          <div className="space-y-0.5 text-center sm:text-left">
            <span className="text-[8px] font-mono text-zinc-500 uppercase block font-bold">Khung video đích</span>
            <span className="text-xs text-zinc-300 font-mono font-semibold">1080x1920 (9:16)</span>
          </div>
          <div className="space-y-0.5 text-center sm:text-left">
            <span className="text-[8px] font-mono text-zinc-500 uppercase block font-bold">Bộ sinh hiệu ứng</span>
            <span className="text-xs text-orange-500 font-mono font-semibold flex items-center gap-1 justify-center sm:justify-start">
              <Cpu className="w-3.5 h-3.5 animate-spin" />
              <span>GPU Accelerated</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
