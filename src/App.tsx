/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import { ProductInfo, MarketingScript, VideoScene } from './types';
import { ProductInput } from './components/ProductInput';
import { ScriptTimeline } from './components/ScriptTimeline';
import { AudioVoicePanel } from './components/AudioVoicePanel';
import { Sparkles, Terminal, Play, FileText, Settings, Video, CheckCircle, Cpu, ShieldAlert, Code } from 'lucide-react';

export default function App() {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [script, setScript] = useState<MarketingScript | null>(null);
  const [diagnostics, setDiagnostics] = useState<string[]>([]);

  // Function to append logs
  const addLog = (msg: string) => {
    setDiagnostics(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`].slice(-8));
  };

  const handleGenerateScript = async (info: ProductInfo) => {
    setIsLoading(true);
    setError(null);
    addLog(`Initiating generation pipeline for '${info.name}'`);
    addLog(`Mime configuration: application/json. Model target: Gemini 3.5 Flash`);

    try {
      const response = await fetch('/api/generate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(info),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Failed to generate script.');
      }

      const data = await response.json();
      setScript(data);
      addLog(`SUCCESS: script generation complete. Generated ${data.scenes?.length} scenes.`);
      addLog(`FFmpeg rendering scripts injected & ready.`);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Một lỗi không xác định đã xảy ra.');
      addLog(`ERROR: Pipeline failed. ${err.message || ''}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateScene = (sceneId: string, updatedFields: Partial<VideoScene>) => {
    if (!script) return;
    const updatedScenes = script.scenes.map(s => {
      if (s.id === sceneId) {
        return { ...s, ...updatedFields };
      }
      return s;
    });
    setScript({
      ...script,
      scenes: updatedScenes
    });
    addLog(`UPDATED: Scene ${sceneId} was modified by user editor`);
  };

  return (
    <div className="min-h-screen bg-[#0A0A0A] text-white flex flex-col font-sans select-none overflow-x-hidden antialiased">
      {/* Top Header */}
      <header className="h-20 border-b border-white/10 flex items-center justify-between px-6 sm:px-8 bg-[#0F0F0F] shrink-0">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-[#FF3E00] flex items-center justify-center font-black text-xl italic text-white shadow-lg shadow-[#FF3E00]/10">M</div>
          <div>
            <h1 className="text-[10px] tracking-[0.3em] font-bold text-white/40 uppercase">PROJECT CODE: AIMS-PRO</h1>
            <p className="text-lg font-light tracking-tight">AI MARKETING STUDIO <span className="font-black italic text-[#FF3E00]">PRO</span></p>
          </div>
        </div>
        <div className="hidden lg:flex gap-6 items-center text-[10px] tracking-widest uppercase font-semibold">
          <span className="text-[#FF3E00] flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#FF3E00] animate-pulse"></span>
            Engine: Gemini 3.5 Flash
          </span>
          <span className="opacity-40 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
            Fish Speech: Active
          </span>
          <span className="opacity-40 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
            FFmpeg: Ready
          </span>
        </div>
      </header>

      {/* Workspace Inner Container */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigation Rail */}
        <nav className="w-16 border-r border-white/10 hidden md:flex flex-col items-center py-8 gap-8 bg-[#0F0F0F] shrink-0">
          <div className="p-2 text-[#FF3E00] border-b border-white/5 pb-4 w-full flex justify-center">
            <Video className="w-6 h-6" />
          </div>
          <div className="p-2 text-white/30 hover:text-white transition-all cursor-pointer" title="Cấu hình kịch bản">
            <FileText className="w-6 h-6" />
          </div>
          <div className="p-2 text-white/30 hover:text-white transition-all cursor-pointer" title="Thông số kỹ thuật">
            <Cpu className="w-6 h-6" />
          </div>
          <div className="p-2 text-white/30 hover:text-white transition-all cursor-pointer mt-auto" title="Cài đặt dự án">
            <Settings className="w-6 h-6" />
          </div>
        </nav>

        {/* Main Workspace Frame */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 space-y-8 max-w-7xl mx-auto w-full">
          {/* Welcome Intro Section */}
          <div className="bg-[#151515] border border-white/5 p-6 rounded-lg relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 font-mono text-[10px] tracking-wider text-white/10 uppercase">
              Free-First Offline rendering setup
            </div>
            <h2 className="text-[11px] uppercase tracking-widest text-[#FF3E00] font-bold mb-3 italic underline underline-offset-4">
              GIỚI THIỆU HỆ THỐNG
            </h2>
            <div className="text-sm font-light text-white/80 leading-relaxed max-w-3xl space-y-2">
              <p>
                Chào mừng bạn đến với <strong className="text-white font-semibold">AI Marketing Studio PRO</strong>. Giải pháp hoàn hảo, tối ưu chi phí dành cho các nhà sáng tạo nội dung TikTok Shop tại Việt Nam.
              </p>
              <p>
                Sử dụng mô hình <strong className="text-[#FF3E00] font-semibold">Google Gemini</strong> để lập kế hoạch kịch bản và chuẩn bị giọng nói thuần Việt trơn tru nhất cho engine <strong className="text-white font-medium">Fish Speech</strong>. Biên dịch video tự động offline bằng các kịch bản lệnh <strong className="text-white font-medium">FFmpeg</strong> mà không tốn phí vận hành mây.
              </p>
            </div>
          </div>

          {/* Core Content Blocks */}
          <div className="grid grid-cols-1 gap-8">
            {/* 1. Form Section */}
            <div className="bg-[#151515] border border-white/5 p-1 rounded-lg">
              <ProductInput onGenerate={handleGenerateScript} isLoading={isLoading} />
            </div>

            {/* Error Message Screen */}
            {error && (
              <div id="error-screen" className="bg-red-950/20 border border-red-500/30 rounded-lg p-5 flex gap-3 items-start">
                <ShieldAlert className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <h4 className="text-sm font-bold text-red-400">Lỗi thực thi dữ liệu</h4>
                  <p className="text-xs text-white/70">{error}</p>
                  {error.includes("Secrets") && (
                    <div className="text-xs text-amber-300 mt-2">
                      💡 Vui lòng truy cập góc phải phía trên của AI Studio, chọn <strong>Settings &gt; Secrets</strong>, thêm biến <strong>GEMINI_API_KEY</strong> rồi điền khóa API của bạn để kích hoạt hệ thống.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 2. Generation Output Presentation */}
            {script ? (
              <div className="space-y-8">
                {/* Visual Timeline and Phone Simulator */}
                <div className="bg-[#151515] border border-white/5 p-6 rounded-lg relative">
                  <div className="absolute top-0 right-0 p-4 font-mono text-[10px] text-white/20">LIVE_VIEWPORT_PREVIEW</div>
                  <h2 className="text-[11px] uppercase tracking-widest text-[#FF3E00] font-bold mb-6 italic underline underline-offset-4">
                    Kịch Bản Content TikTok & Preview
                  </h2>
                  <ScriptTimeline script={script} onUpdateScene={handleUpdateScene} />
                </div>

                {/* 3. Audio Panel */}
                <div className="bg-[#151515] border border-white/5 p-1 rounded-lg">
                  <AudioVoicePanel scenes={script.scenes} />
                </div>

                {/* 4. Local Rendering Pipeline & Python Integration */}
                <div className="bg-[#151515] border border-white/5 p-6 rounded-lg space-y-4">
                  <div className="flex items-center justify-between border-b border-white/5 pb-3">
                    <h2 className="text-[11px] uppercase tracking-widest text-[#FF3E00] font-bold italic underline underline-offset-4">
                      Tự Động Hóa Biên Tập Với FFmpeg & Python
                    </h2>
                    <span className="text-[10px] font-mono text-white/30">PYTHON_SUBPROCESS_GENERATOR</span>
                  </div>

                  <p className="text-xs text-white/70 leading-relaxed">
                    AI Marketing Studio PRO mang lại một kịch bản Python hoàn chỉnh. Kịch bản này tự động ghép nối các phân cảnh, chèn giọng nói tiếng Việt được tổng hợp bởi Fish Speech, thêm nhạc nền, vẽ văn bản phụ đề động lên khung hình dọc 9:16 chuẩn chỉ.
                  </p>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold text-white/60">Lệnh FFmpeg Gốc (Thiết kế nhanh):</span>
                    </div>
                    <pre className="bg-[#0A0A0A] border border-white/5 p-4 rounded-lg overflow-x-auto text-xs font-mono text-amber-400">
                      {script.ffmpegCommand || "ffmpeg -i input.mp4 -vf \"drawtext=text='Văn bản mẫu':fontsize=24\" output.mp4"}
                    </pre>
                  </div>

                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-semibold text-white/60">Kịch Bản Python Chạy Offline (Sử dụng FFmpeg Subprocess):</span>
                    </div>
                    <pre className="bg-[#0A0A0A] border border-white/5 p-4 rounded-lg overflow-x-auto text-xs font-mono text-emerald-400 max-h-[350px] overflow-y-auto">
                      {script.pythonFFmpegScript || "# Đang chuẩn bị kịch bản..."}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              !isLoading && (
                <div className="border border-dashed border-white/10 rounded-2xl p-12 text-center text-white/40 space-y-4 bg-[#0F0F0F]/40">
                  <Sparkles className="w-12 h-12 text-[#FF3E00] mx-auto animate-pulse" />
                  <div className="space-y-1">
                    <h3 className="text-base font-semibold text-white/80">Kịch bản chưa được tạo</h3>
                    <p className="text-xs max-w-md mx-auto">
                      Nhập thông tin sản phẩm của bạn ở bảng trên hoặc chọn các mẫu có sẵn để Gemini AI thiết kế một kịch bản video TikTok giữ chân người xem tốt nhất.
                    </p>
                  </div>
                </div>
              )
            )}
          </div>

          {/* Bottom Diagnostics Log Console */}
          <footer className="bg-[#151515] border border-white/5 p-5 rounded-lg space-y-3">
            <div className="flex justify-between items-center border-b border-white/5 pb-2">
              <h3 className="text-[10px] uppercase tracking-widest text-white/40 font-bold flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-[#FF3E00]" />
                System Diagnostics
              </h3>
              <span className="text-[9px] font-mono text-green-500 bg-green-500/10 px-2 py-0.5 rounded border border-green-500/20 uppercase">
                Status: Operational
              </span>
            </div>
            <div className="font-mono text-[10px] text-white/30 space-y-1.5 max-h-[140px] overflow-y-auto">
              <p>&gt; [INFO] AI Marketing Studio PRO engine initialized.</p>
              <p>&gt; [INFO] Fish Speech natural voice synthesizers ready.</p>
              <p>&gt; [INFO] Google Gemini API connection online.</p>
              {diagnostics.map((log, index) => (
                <p key={index} className="text-white/60">&gt; {log}</p>
              ))}
              {isLoading && (
                <p className="text-[#FF3E00] animate-pulse">&gt; [PROCESS] Waiting for Gemini model generation response...</p>
              )}
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
