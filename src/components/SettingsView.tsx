import React, { useState } from 'react';
import { Settings, Shield, Server, Folder, Terminal, Check } from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [copied, setCopied] = useState(false);
  const [geminiKey, setGeminiKey] = useState("••••••••••••••••••••••••");
  const [fishEndpoint, setFishEndpoint] = useState("http://localhost:8000");
  const [outputPath, setOutputPath] = useState("/home/user/aims_projects/renders/");
  const [verboseLogging, setVerboseLogging] = useState(true);

  const saveSettings = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
    alert("Đã lưu thiết lập hệ thống thành công!");
  };

  return (
    <div className="space-y-6 animate-fadeIn select-none">
      
      {/* Settings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 text-xs">
        
        {/* API Credentials */}
        <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl space-y-4 shadow-xl">
          <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-widest border-b border-zinc-850 pb-2.5 flex items-center gap-2">
            <Shield className="w-4 h-4 text-orange-500" />
            <span>Mã bảo mật & API Cloud</span>
          </h3>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between mb-1 text-[10px] font-mono font-bold text-zinc-400">
                <span>GEMINI API SECRET KEY</span>
                <span className="text-zinc-500">Ghi nhận từ .env</span>
              </div>
              <input
                type="password"
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 rounded px-3 py-2 focus:outline-none"
              />
            </div>

            <div className="bg-zinc-950/60 p-2.5 rounded border border-zinc-850/60 text-[10px] text-zinc-500 leading-relaxed font-sans">
              🔑 **An toàn thông tin:** Khóa bí mật API được duy trì an toàn tại phân vùng máy chủ proxy server-side của bạn, hoàn toàn không rò rỉ ra trình duyệt web.
            </div>
          </div>
        </div>

        {/* TTS & Media Servers */}
        <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl space-y-4 shadow-xl">
          <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-widest border-b border-zinc-850 pb-2.5 flex items-center gap-2">
            <Server className="w-4 h-4 text-orange-500" />
            <span>Kết nối máy chủ cục bộ (TTS / API)</span>
          </h3>

          <div className="space-y-3">
            <div>
              <span className="text-[10px] font-mono font-bold text-zinc-400 block mb-1">FISH SPEECH API ENDPOINT</span>
              <input
                type="text"
                value={fishEndpoint}
                onChange={(e) => setFishEndpoint(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 font-mono rounded px-3 py-2 focus:outline-none"
              />
            </div>

            <div>
              <span className="text-[10px] font-mono font-bold text-zinc-400 block mb-1">THƯ MỤC LƯU VIDEO ĐẦU RA</span>
              <input
                type="text"
                value={outputPath}
                onChange={(e) => setOutputPath(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 font-mono rounded px-3 py-2 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Developer Console settings */}
        <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl space-y-4 shadow-xl lg:col-span-2">
          <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-widest border-b border-zinc-850 pb-2.5 flex items-center gap-2">
            <Terminal className="w-4 h-4 text-orange-500" />
            <span>Thiết lập chẩn đoán & Gỡ lỗi logs</span>
          </h3>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <span className="font-bold text-zinc-200">Ghi nhận log chi tiết (Verbose debug logging)</span>
              <p className="text-[11px] text-zinc-500">In toàn bộ tham số biên tập của luồng drawtext trong FFmpeg stdout.</p>
            </div>
            
            <button
              onClick={() => setVerboseLogging(!verboseLogging)}
              className={`px-3 py-1 rounded text-[10px] font-bold transition-all cursor-pointer ${
                verboseLogging ? 'bg-orange-600 text-white' : 'bg-zinc-950 text-zinc-500 border border-zinc-850'
              }`}
            >
              {verboseLogging ? 'Bật' : 'Tắt'}
            </button>
          </div>
        </div>

      </div>

      {/* Save Settings floating bottom bar */}
      <div className="flex justify-end border-t border-zinc-900 pt-4">
        <button
          onClick={saveSettings}
          className="px-6 py-2.5 bg-orange-600 hover:bg-orange-500 text-white font-bold rounded-lg transition-all flex items-center gap-1.5 cursor-pointer shadow-md"
        >
          {copied ? <Check className="w-3.5 h-3.5" /> : <Settings className="w-3.5 h-3.5" />}
          <span>{copied ? 'Đã lưu' : 'Lưu thiết lập'}</span>
        </button>
      </div>
    </div>
  );
};
