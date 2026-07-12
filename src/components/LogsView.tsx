import React, { useState } from 'react';
import { Terminal, ShieldAlert, CheckCircle, Info, RefreshCw } from 'lucide-react';

export const LogsView: React.FC = () => {
  const [filter, setFilter] = useState<'all' | 'info' | 'warn' | 'error'>('all');

  const logEntries = [
    { time: "12:05:01", level: "info", text: "Successfully initialized Gemini-3.5 API client." },
    { time: "12:05:04", level: "info", text: "FastAPI local microservices running on port 8000." },
    { time: "12:05:10", level: "info", text: "Found local FFmpeg executable: /usr/bin/ffmpeg." },
    { time: "12:06:15", level: "warn", text: "No custom voice actor file loaded. Falling back to default vi-female-warm." },
    { time: "12:07:02", level: "info", text: "Rendering scene #1 voice synthesis output. Status: OK." },
    { time: "12:07:08", level: "error", text: "FFmpeg render skipped: Missing background audio overlay asset files." }
  ];

  const filteredLogs = logEntries.filter(log => {
    if (filter === 'all') return true;
    return log.level === filter;
  });

  return (
    <div className="space-y-6 animate-fadeIn select-none">
      
      {/* Logs filter bar */}
      <div className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl flex items-center justify-between shadow-md">
        <div className="flex gap-2">
          {[
            { key: 'all', label: 'Tất cả logs' },
            { key: 'info', label: 'Thông tin (Info)' },
            { key: 'warn', label: 'Cảnh báo (Warn)' },
            { key: 'error', label: 'Lỗi hệ thống (Error)' }
          ].map(p => (
            <button
              key={p.key}
              onClick={() => setFilter(p.key as any)}
              className={`py-1 px-3 text-[10px] font-bold rounded-full transition-all cursor-pointer ${
                filter === p.key
                  ? 'bg-orange-600 text-white'
                  : 'bg-zinc-950 text-zinc-500 hover:text-zinc-200 border border-zinc-850'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        <button
          onClick={() => alert("Đã xóa sạch bộ đệm logs!")}
          className="text-[10px] font-bold text-zinc-400 hover:text-white bg-zinc-950 border border-zinc-850 px-3 py-1 rounded transition-all cursor-pointer"
        >
          Xóa Logs
        </button>
      </div>

      {/* Terminal log panel */}
      <div className="bg-zinc-950 border border-zinc-800 rounded-xl p-5 font-mono text-[11px] leading-relaxed min-h-[320px] shadow-inner flex flex-col justify-between">
        <div className="space-y-2 flex-1">
          {filteredLogs.map((entry, index) => (
            <div key={index} className="flex items-start gap-3">
              <span className="text-zinc-600 font-semibold shrink-0 select-none">[{entry.time}]</span>
              <span className={`px-1 rounded text-[9px] font-bold tracking-wider uppercase shrink-0 select-none ${
                entry.level === 'error' ? 'bg-red-500/20 text-red-400' :
                entry.level === 'warn' ? 'bg-amber-500/20 text-amber-400' :
                'bg-blue-500/20 text-blue-400'
              }`}>
                {entry.level}
              </span>
              <span className="text-zinc-300 font-sans">{entry.text}</span>
            </div>
          ))}
        </div>

        <div className="border-t border-zinc-900 pt-3.5 mt-6 text-[9px] text-zinc-600 flex justify-between select-none">
          <span>* Hệ thống tự động ghi chép logs chẩn đoán</span>
          <span>AIMS-STDOUT-WRAPPER</span>
        </div>
      </div>
    </div>
  );
};
