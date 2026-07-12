import React, { useState } from 'react';
import { MarketingScript } from '../types';
import { FolderOpen, Save, Trash2, Check, RefreshCw, Calendar, FileText } from 'lucide-react';

interface ProjectsViewProps {
  script: MarketingScript | null;
  onLoadDemo: (data: any) => void;
  onClearScript: () => void;
}

export const ProjectsView: React.FC<ProjectsViewProps> = ({
  script,
  onLoadDemo,
  onClearScript
}) => {
  const [copied, setCopied] = useState(false);

  const mockSavedProjects = [
    {
      id: "p1",
      name: "Son Kem Velvet Lip Glow.json",
      date: "12/07/2026",
      size: "4.8 KB",
      scenes: 6,
      tone: "asymmetric_hook"
    },
    {
      id: "p2",
      name: "Nồi Chiên Smart Cook 6L.json",
      date: "11/07/2026",
      size: "5.2 KB",
      scenes: 5,
      tone: "problem_solving"
    }
  ];

  return (
    <div className="space-y-6 animate-fadeIn select-none">
      
      {/* Save current project state */}
      <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl space-y-4 shadow-xl">
        <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-widest border-b border-zinc-850 pb-2.5 flex items-center gap-2">
          <Save className="w-4 h-4 text-orange-500" />
          <span>Lưu trữ phiên hiện tại</span>
        </h3>

        {script ? (
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs">
            <div className="space-y-1">
              <p className="text-zinc-200 font-bold">Kịch bản đang hoạt động: {script.hookType.toUpperCase()}</p>
              <p className="text-zinc-500 font-mono">Phiên hiện tại chứa {script.scenes.length} phân cảnh ({script.totalDuration}s)</p>
            </div>
            
            <div className="flex gap-2 w-full sm:w-auto">
              <button
                onClick={() => {
                  setCopied(true);
                  setTimeout(() => setCopied(false), 1500);
                  alert("Lưu dự án cục bộ thành công!");
                }}
                className="flex-1 sm:flex-none px-4 py-2 bg-orange-600 hover:bg-orange-500 text-white font-bold rounded text-[11px] transition-all flex items-center justify-center gap-1.5 cursor-pointer"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Save className="w-3.5 h-3.5" />}
                <span>Lưu kịch bản</span>
              </button>
              <button
                onClick={() => {
                  if(confirm("Bạn có chắc chắn muốn xóa kịch bản hiện tại?")) {
                    onClearScript();
                  }
                }}
                className="flex-1 sm:flex-none px-4 py-2 bg-zinc-950 border border-zinc-800 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/20 text-zinc-400 font-bold rounded text-[11px] transition-all flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Xóa phiên</span>
              </button>
            </div>
          </div>
        ) : (
          <p className="text-xs text-zinc-500 italic">Không có kịch bản hoạt động nào để lưu trữ.</p>
        )}
      </div>

      {/* Local storage project catalog */}
      <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl space-y-4 shadow-xl">
        <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-widest border-b border-zinc-850 pb-2.5 flex items-center gap-2">
          <FolderOpen className="w-4 h-4 text-orange-500" />
          <span>Danh sách tệp tin dự án gần đây</span>
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {mockSavedProjects.map((project) => (
            <div
              key={project.id}
              className="bg-zinc-950 p-4 border border-zinc-850 rounded-lg hover:border-orange-500/30 transition-all flex items-start justify-between cursor-pointer"
              onClick={() => {
                alert(`Đang đồng bộ nạp dự án ${project.name}`);
              }}
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-zinc-200">
                  <FileText className="w-4 h-4 text-[#3B82F6]" />
                  <span>{project.name}</span>
                </div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-[10px] font-mono text-zinc-500">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-zinc-600" />
                    <span>{project.date}</span>
                  </div>
                  <div>Size: {project.size}</div>
                  <div>Phân cảnh: {project.scenes}</div>
                  <div className="uppercase">Tone: {project.tone}</div>
                </div>
              </div>

              <div className="text-[10px] text-zinc-500 font-bold bg-zinc-900 border border-zinc-850 px-2 py-0.5 rounded hover:text-white cursor-pointer">
                Nạp tệp
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
