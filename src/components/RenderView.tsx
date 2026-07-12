import React, { useState, useEffect, useRef } from 'react';
import { MarketingScript } from '../types';
import {
  Video, Play, Terminal, Cpu, Sliders, Check, Clock, Download, RefreshCw, AlertCircle
} from 'lucide-react';

interface RenderViewProps {
  script: MarketingScript | null;
  onSetStatusMessage: (msg: string) => void;
  onSetWorkflowStatus: (status: 'Idle' | 'Generating' | 'Rendering' | 'Completed' | 'Error') => void;
}

export const RenderView: React.FC<RenderViewProps> = ({
  script,
  onSetStatusMessage,
  onSetWorkflowStatus
}) => {
  const [renderProgress, setRenderProgress] = useState<number>(0);
  const [isRendering, setIsRendering] = useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([
    "=== AIMS-PRO FFmpeg Multiplexing Compiler Init ===",
    "Engine version: aims_ffmpeg_x64 v1.2.0-release",
    "Checking native binaries... OK (Found local/bin/ffmpeg)",
    "Checking audio voice profiles... OK",
    "System ready. Click 'Bắt đầu xuất video' to run compiling pipeline."
  ]);
  const [hwAcceleration, setHwAcceleration] = useState<string>('h264_nvenc');
  const [fps, setFps] = useState<number>(30);
  const [bitrate, setBitrate] = useState<string>('8M');

  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const addLog = (line: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${line}`]);
  };

  const startRender = () => {
    if (!script) return;
    setIsRendering(true);
    setRenderProgress(0);
    onSetWorkflowStatus('Rendering');
    onSetStatusMessage('Đang biên tập và xuất video bằng FFmpeg Engine...');

    setLogs([
      "=== Bắt đầu biên dịch video quảng cáo ===",
      `Sản phẩm kịch bản: ${script.hookType.toUpperCase()}`,
      `Thời lượng kịch bản: ${script.totalDuration}s`,
      `Số phân cảnh: ${script.scenes.length} scene tracks`
    ]);

    const steps = [
      { prg: 5, log: "Bắt đầu trích xuất luồng thoại TTS từ cache bộ đệm..." },
      { prg: 15, log: "Đang ghép nối luồng thoại cảnh 1 và lồng ghép âm thanh sfx..." },
      { prg: 30, log: "Đang nạp video nền mẫu: 'son_kem_moi_closeup.mp4'..." },
      { prg: 45, log: "Áp dụng cấu trúc lọc FFmpeg lọc phụ đề chèn cứng (burn-in subtitle filters)..." },
      { prg: 60, log: "Đang render luồng hình ảnh khung dọc 1080x1920 @30fps..." },
      { prg: 75, log: "Multiplexing: Đồng bộ hóa tiếng nói thoại, nhạc nền lofi lồng ghép..." },
      { prg: 90, log: "Mã hóa nén sản phẩm qua luồng tăng tốc phần cứng NVENC h264..." },
      { prg: 98, log: "Ghi dữ liệu video xuống phân vùng ổ đĩa tạm..." },
      { prg: 100, log: "=== HOÀN THÀNH BIÊN TẬP! Video quảng cáo đã sẵn sàng tải xuống ===" }
    ];

    steps.forEach((step, index) => {
      setTimeout(() => {
        setRenderProgress(step.prg);
        addLog(step.log);

        if (step.prg === 100) {
          setIsRendering(false);
          onSetWorkflowStatus('Completed');
          onSetStatusMessage('Xuất video thành công!');
        }
      }, (index + 1) * 1200);
    });
  };

  return (
    <div className="space-y-6 animate-fadeIn select-none">
      {/* Top action block */}
      <div className="bg-zinc-950 border border-zinc-800 p-4 rounded-xl flex flex-col sm:flex-row justify-between items-center gap-4 shadow-md">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-orange-600/15 text-orange-500 rounded">
            <Video className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-zinc-200">FFmpeg Render Pipeline</h3>
            <p className="text-[10px] text-zinc-500">Hợp nhất tất cả phân cảnh, lời thoại và phụ đề thành video hoàn chỉnh</p>
          </div>
        </div>

        <button
          onClick={startRender}
          disabled={!script || isRendering}
          className={`px-6 py-2.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
            !script || isRendering
              ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed border border-zinc-750'
              : 'bg-orange-600 hover:bg-orange-500 text-white shadow shadow-orange-600/15'
          }`}
        >
          {isRendering ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-white" />}
          <span>{isRendering ? 'Đang xuất video...' : 'Bắt đầu xuất video'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left column: Render settings & Queue */}
        <div className="lg:col-span-5 space-y-4">
          
          {/* Active Queue panel */}
          <div className="bg-zinc-900 border border-zinc-850 p-4.5 rounded-xl space-y-3.5 shadow-xl">
            <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block border-b border-zinc-850 pb-2">
              Danh sách hàng đợi render
            </span>

            <div className="bg-zinc-950 border border-zinc-850 rounded-lg p-3 space-y-2.5">
              <div className="flex justify-between items-center text-xs">
                <span className="text-zinc-300 font-bold">tiktok_shop_ads_output.mp4</span>
                <span className={`text-[9px] font-mono font-bold ${
                  renderProgress === 100 ? 'text-emerald-400' : isRendering ? 'text-orange-500' : 'text-zinc-500'
                }`}>
                  {renderProgress === 100 ? 'HOÀN THÀNH' : isRendering ? `ĐANG CHẠY ${renderProgress}%` : 'ĐANG ĐỢI'}
                </span>
              </div>

              {/* Progress slider bar */}
              <div className="w-full bg-zinc-900 h-2 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-orange-600 to-orange-400 transition-all duration-300"
                  style={{ width: `${renderProgress}%` }}
                />
              </div>

              <div className="flex justify-between text-[9px] font-mono text-zinc-500">
                <span>Khung dọc 9:16</span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {isRendering ? 'Còn ~10 giây' : renderProgress === 100 ? 'Đã lưu' : 'Chưa chạy'}
                </span>
              </div>

              {renderProgress === 100 && (
                <a
                  href="#"
                  onClick={(e) => { e.preventDefault(); alert("Giả lập tải tệp video MP4 thành công!"); }}
                  className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs rounded transition-all text-center flex items-center justify-center gap-1.5 mt-2 cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  Tải Xuống Video Đã Xuất
                </a>
              )}
            </div>
          </div>

          {/* Advanced FFmpeg Compiler settings */}
          <div className="bg-zinc-900 border border-zinc-850 p-4.5 rounded-xl space-y-4 shadow-xl">
            <h4 className="text-xs font-bold text-zinc-300 uppercase tracking-widest flex items-center gap-1.5 border-b border-zinc-850 pb-2">
              <Sliders className="w-3.5 h-3.5 text-orange-500" />
              <span>Cấu hình compiler nâng cao</span>
            </h4>

            {/* Hardware select */}
            <div>
              <span className="text-[9px] font-mono font-bold text-zinc-400 block mb-1">TĂNG TỐC PHẦN CỨNG (HW ACCELERATOR)</span>
              <select
                value={hwAcceleration}
                onChange={(e) => setHwAcceleration(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs rounded px-2.5 py-1.5 focus:outline-none"
              >
                <option value="h264_nvenc">NVIDIA NVENC H.264 (Phổ biến, khuyên dùng)</option>
                <option value="hevc_qsv">Intel QuickSync HEVC (Tiết kiệm dung lượng)</option>
                <option value="h264_videotoolbox">Apple VideoToolbox H.264 (Dành cho macOS)</option>
                <option value="libx264">CPU-only libx264 (Bộ giải mã mềm, chậm)</option>
              </select>
            </div>

            {/* FPS and Bitrate */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <span className="text-[9px] font-mono font-bold text-zinc-400 block mb-1">TỐC ĐỘ KHUNG HÌNH</span>
                <select
                  value={fps}
                  onChange={(e) => setFps(parseInt(e.target.value))}
                  className="w-full bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs rounded px-2.5 py-1.5 focus:outline-none"
                >
                  <option value={24}>24 FPS (Cinematic)</option>
                  <option value={30}>30 FPS (Mặc định)</option>
                  <option value={60}>60 FPS (Mượt mà)</option>
                </select>
              </div>

              <div>
                <span className="text-[9px] font-mono font-bold text-zinc-400 block mb-1">BITRATE HÌNH ẢNH</span>
                <select
                  value={bitrate}
                  onChange={(e) => setBitrate(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 text-zinc-300 text-xs rounded px-2.5 py-1.5 focus:outline-none"
                >
                  <option value="4M">4 Mbps (Nhỏ gọn)</option>
                  <option value="8M">8 Mbps (Độ nét cao)</option>
                  <option value="15M">15 Mbps (Phòng thu)</option>
                </select>
              </div>
            </div>
          </div>

        </div>

        {/* Right column: Terminal log window */}
        <div className="lg:col-span-7 bg-zinc-950 border border-zinc-800 rounded-xl p-4 flex flex-col justify-between h-[380px] font-mono text-xs shadow-inner">
          <div className="flex items-center justify-between border-b border-zinc-850 pb-2 mb-2 shrink-0 select-none">
            <span className="text-[10px] font-bold text-zinc-400 flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-orange-500" />
              BỘ ĐIỀU KHIỂN LOGS (FFMPEG STDOUT)
            </span>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
              <span className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
              <span className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto text-emerald-400 p-2.5 rounded bg-black/50 border border-zinc-900 space-y-1.5 leading-relaxed text-[11px]">
            {logs.map((log, idx) => (
              <div key={idx}>{log}</div>
            ))}
            <div ref={logsEndRef} />
          </div>

          <div className="pt-2 border-t border-zinc-900/60 mt-2 text-[9px] text-zinc-500 flex justify-between select-none shrink-0">
            <span>CONSOLE WRAP</span>
            <span>UTF-8 ENCODING</span>
          </div>
        </div>

      </div>
    </div>
  );
};
