/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { MarketingScript, VideoScene } from '../types';
import { Film, Eye, Volume2, AlertCircle, Edit3, CheckCircle, RefreshCcw, BookOpen, Smartphone } from 'lucide-react';

interface ScriptTimelineProps {
  script: MarketingScript;
  onUpdateScene: (sceneId: string, updatedFields: Partial<VideoScene>) => void;
}

export const ScriptTimeline: React.FC<ScriptTimelineProps> = ({ script, onUpdateScene }) => {
  const [selectedSceneId, setSelectedSceneId] = useState<string>(script.scenes[0]?.id || '');
  const [editingSceneId, setEditingSceneId] = useState<string | null>(null);

  const selectedScene = script.scenes.find(s => s.id === selectedSceneId) || script.scenes[0];

  // Helper to calculate total words in the voiceover
  const calculateTotalWords = () => {
    return script.scenes.reduce((acc, s) => acc + s.voiceover.split(/\s+/).filter(Boolean).length, 0);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Script Timeline Segment */}
      <div className="lg:col-span-2 space-y-6">
        {/* Hook Strategy Accent Box */}
        <div id="hook-strategy-box" className="bg-slate-950/60 border border-[#FF3E00]/20 rounded-xl p-5 relative overflow-hidden">
          <div className="absolute top-0 right-0 px-3 py-1 bg-[#FF3E00]/10 text-[#FF3E00] text-[10px] font-mono border-l border-b border-[#FF3E00]/20 rounded-bl-lg font-bold">
            TIÊU ĐIỂM HOOK
          </div>
          <div className="flex items-start gap-3">
            <div className="mt-1 p-1.5 bg-[#FF3E00]/10 text-[#FF3E00] rounded">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-200">
                Phương Pháp Tiếp Cận: <span className="text-[#FF3E00] text-base">{script.hookType}</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
                {script.hookExplanation}
              </p>
            </div>
          </div>
        </div>

        {/* Scene List Timeline */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Film className="w-4 h-4 text-[#FF3E00]" />
              <span>Dòng Thời Gian Phân Cảnh ({script.scenes.length} Cảnh)</span>
            </h3>
            <span className="text-xs text-slate-400 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
              Tổng số từ: <strong className="text-slate-200 font-mono">{calculateTotalWords()}</strong> từ (~{script.totalDuration}s)
            </span>
          </div>

          <div className="space-y-3">
            {script.scenes.map((scene, index) => {
              const isSelected = selectedSceneId === scene.id;
              const isEditing = editingSceneId === scene.id;

              return (
                <div
                  id={`scene-row-${scene.id}`}
                  key={scene.id}
                  onClick={() => setSelectedSceneId(scene.id)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer relative ${
                    isSelected
                      ? 'bg-slate-900 border-[#FF3E00]/30 ring-1 ring-[#FF3E00]/20'
                      : 'bg-[#151515] border-white/5 hover:bg-slate-900/40 hover:border-slate-800'
                  }`}
                >
                  {/* Left Accent indicator */}
                  {isSelected && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-[#FF3E00] rounded-l-xl" />
                  )}

                  <div className="flex items-center justify-between gap-3 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="flex items-center justify-center w-5 h-5 rounded bg-slate-800 text-xs font-mono text-slate-300 font-semibold border border-slate-700">
                        {index + 1}
                      </span>
                      <span className="text-xs font-mono font-bold text-slate-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                        {scene.timecode}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1 bg-slate-950/60 px-2 py-0.5 rounded">
                        <Volume2 className="w-3 h-3 text-slate-400" />
                        {scene.sfxAudio || 'No SFX'}
                      </span>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingSceneId(isEditing ? null : scene.id);
                        }}
                        className="p-1 rounded text-slate-400 hover:text-[#FF3E00] hover:bg-slate-800/60 transition-all"
                        title="Chỉnh sửa lời"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>

                  {/* Visual and Speech content */}
                  {isEditing ? (
                    <div className="space-y-3 mt-3 pt-3 border-t border-slate-800/60" onClick={(e) => e.stopPropagation()}>
                      <div>
                        <label className="text-[10px] font-mono font-bold text-slate-500 uppercase block mb-1">Cảnh Hình Ảnh Overlay:</label>
                        <input
                          type="text"
                          value={scene.subtitle}
                          onChange={(e) => onUpdateScene(scene.id, { subtitle: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-[#FF3E00]"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] font-mono font-bold text-slate-500 uppercase block mb-1">Lời đọc (Mô tả dạng chữ cho TTS):</label>
                        <textarea
                          rows={2}
                          value={scene.voiceover}
                          onChange={(e) => onUpdateScene(scene.id, { voiceover: e.target.value })}
                          className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded px-2.5 py-1.5 focus:outline-none focus:border-[#FF3E00] resize-none font-sans"
                        />
                      </div>
                      <div className="flex justify-end">
                        <button
                          type="button"
                          onClick={() => setEditingSceneId(null)}
                          className="flex items-center gap-1 text-[10px] bg-[#FF3E00]/20 text-[#FF3E00] border border-[#FF3E00]/30 rounded px-2.5 py-1 hover:bg-[#FF3E00]/30 transition-all"
                        >
                          <CheckCircle className="w-3 h-3" />
                          Hoàn thành
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-1.5 text-xs">
                      <div className="text-slate-400 font-sans italic leading-relaxed">
                        <span className="text-slate-500 font-semibold not-italic mr-1">Hình ảnh:</span> {scene.visualAction}
                      </div>
                      <div className="text-[#FF3E00] font-semibold leading-relaxed">
                        <span className="text-slate-500 font-semibold mr-1">Giọng nói (TTS):</span> "{scene.voiceover}"
                      </div>
                      <div className="text-amber-300/90 font-medium leading-relaxed">
                        <span className="text-slate-500 font-semibold mr-1">Chữ hiển thị:</span> <span className="bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 text-[11px] font-mono font-bold">{scene.subtitle}</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Live Vertical Smartphone Mockup */}
      <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <Smartphone className="w-4 h-4 text-[#FF3E00]" />
          <span>Mô Phỏng Trực Quan (9:16)</span>
        </h3>

        <div className="flex justify-center">
          {/* Vertical device shell */}
          <div id="phone-mockup-frame" className="w-[280px] h-[500px] rounded-[36px] bg-slate-950 border-4 border-slate-800 p-2 shadow-2xl relative flex flex-col overflow-hidden ring-1 ring-slate-800">
            {/* Phone speaker notch */}
            <div className="absolute top-3 left-1/2 -translate-x-1/2 w-20 h-4 bg-slate-800 rounded-full z-20 flex items-center justify-center">
              <div className="w-8 h-1 bg-slate-900 rounded-full" />
            </div>

            {/* Simulated Screen Body */}
            <div className="flex-1 rounded-[28px] bg-[#151515] relative overflow-hidden flex flex-col justify-end p-4 z-10 select-none">
              {/* Dynamic looping background effect simulation based on tone */}
              <div className="absolute inset-0 bg-gradient-to-tr from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center text-center p-4">
                {/* Glowing light source */}
                <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-32 h-32 bg-[#FF3E00]/10 rounded-full blur-2xl animate-pulse" />
                
                <div className="space-y-3 z-10 opacity-70">
                  <span className="text-[9px] font-mono tracking-widest text-[#FF3E00]/80 bg-[#FF3E00]/10 px-2 py-0.5 rounded-full border border-[#FF3E00]/20">
                    {script.hookType.toUpperCase()}
                  </span>
                  <div className="text-[10px] text-slate-400 leading-relaxed font-mono px-2">
                    {selectedScene?.visualAction || "Bắt đầu cảnh..."}
                  </div>
                </div>
              </div>

              {/* Sidebar icons (TikTok style) */}
              <div className="absolute right-2.5 bottom-24 flex flex-col gap-3.5 items-center z-20">
                <div className="w-8 h-8 rounded-full bg-slate-950/60 border border-slate-800 flex items-center justify-center text-slate-300 text-[10px]">❤️</div>
                <div className="w-8 h-8 rounded-full bg-slate-950/60 border border-slate-800 flex items-center justify-center text-slate-300 text-[10px]">💬</div>
                <div className="w-8 h-8 rounded-full bg-slate-950/60 border border-slate-800 flex items-center justify-center text-slate-300 text-[10px]">⭐️</div>
              </div>

              {/* Interactive Bottom Video Details */}
              <div className="z-20 space-y-3 mt-auto">
                {/* Username & Audio metadata */}
                <div className="space-y-1">
                  <div className="text-[11px] font-bold text-white flex items-center gap-1.5">
                    <span>@marketing.studio.pro</span>
                    <span className="px-1.5 py-0.5 bg-[#FF3E00] text-white rounded text-[8px] font-bold">LIVE</span>
                  </div>
                  <div className="text-[9px] text-slate-300 max-w-[180px] line-clamp-1 truncate font-mono">
                    🔊 SFX: {selectedScene?.sfxAudio || "Background Music"}
                  </div>
                </div>

                {/* Subtitle text overlay (Simulates dynamic FFmpeg rendering) */}
                <div className="bg-black/40 backdrop-blur-sm border border-white/5 rounded-lg p-2.5 text-center transition-all duration-300 transform scale-100 hover:scale-102">
                  <span className="text-amber-300 font-extrabold text-sm tracking-wide drop-shadow-[0_2px_2px_rgba(0,0,0,1)] uppercase font-sans">
                    {selectedScene?.subtitle || "Dữ liệu văn bản..."}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Instructions box */}
        <div className="bg-slate-950 border border-slate-900 rounded-xl p-3.5 text-xs text-slate-400 leading-relaxed">
          <div className="flex gap-2 items-start">
            <AlertCircle className="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
            <span>
              <strong>Xem mô phỏng kịch bản:</strong> Click vào các phân cảnh bên trái để cập nhật hình ảnh hành động và text phụ đề trên màn hình điện thoại giả lập. Bạn có thể sửa trực tiếp kịch bản bằng nút bút chì.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
