import React, { useState } from 'react';
import { MarketingScript, VideoScene } from '../types';
import {
  Film, Edit3, Volume2, CheckCircle, Sparkles, AlertCircle, ChevronRight, PlayCircle, Plus
} from 'lucide-react';

interface ScriptViewProps {
  script: MarketingScript | null;
  selectedSceneId: string;
  onSelectScene: (id: string) => void;
  onUpdateScene: (sceneId: string, updatedFields: Partial<VideoScene>) => void;
}

export const ScriptView: React.FC<ScriptViewProps> = ({
  script,
  selectedSceneId,
  onSelectScene,
  onUpdateScene,
}) => {
  const [editingSceneId, setEditingSceneId] = useState<string | null>(null);

  if (!script) {
    return (
      <div className="border border-dashed border-zinc-800 rounded-2xl p-16 text-center text-zinc-500 bg-zinc-900/10 flex flex-col items-center justify-center min-h-[350px]">
        <Film className="w-12 h-12 text-zinc-700 mb-4 animate-pulse" />
        <h3 className="text-sm font-semibold text-zinc-300">Chưa tìm thấy kịch bản hoạt động</h3>
        <p className="text-[10px] text-zinc-500 mt-1 max-w-sm">
          Nhập thông tin sản phẩm ở trang **Sản phẩm (Product)** hoặc nạp mẫu nhanh từ **Dashboard** để kích hoạt trình soạn thảo kịch bản chuyên nghiệp.
        </p>
      </div>
    );
  }

  const selectedScene = script.scenes.find(s => s.id === selectedSceneId) || script.scenes[0];

  // Simulated AI suggestions based on tone
  const getSuggestions = () => {
    const tone = script.hookType.toLowerCase();
    const suggestions = [
      {
        id: "1",
        title: "Tối ưu hóa câu dắt 2s đầu",
        desc: "Đảm bảo câu Hook không chứa từ chào hỏi thừa thãi. Bạn đã làm rất tốt với Hook thuộc thể loại '" + script.hookType + "'.",
        type: "success"
      },
      {
        id: "2",
        title: "Tần suất chữ trên giây (Pacing)",
        desc: "Mật độ âm tiết trong phân cảnh hiện tại phù hợp với tốc độ nói của bộ phát Fish Speech (~3.5 từ/giây).",
        type: "info"
      }
    ];

    if (selectedScene) {
      if (selectedScene.voiceover.length > 100) {
        suggestions.push({
          id: "3",
          title: "Thoại hơi dài",
          desc: "Phân cảnh này chứa nhiều chữ. Hãy cân nhắc tách nhỏ hoặc tăng tốc độ giọng đọc lên 1.1x trong tab Voice.",
          type: "warning"
        });
      } else {
        suggestions.push({
          id: "3",
          title: "Bố cục phụ đề trực quan",
          desc: "Phụ đề ngắn gọn, dễ dàng ghi đè bằng lệnh FFmpeg lên trung tâm khung dọc.",
          type: "success"
        });
      }
    }

    return suggestions;
  };

  const suggestions = getSuggestions();

  // Real-time frontend price safety validation
  const checkLivePriceSafety = (): string[] => {
    const issues: string[] = [];
    
    const pricePatterns = [
      { regex: /\b\d+\s*[kK]\b/i, msg: "Phát hiện ký tự giá dạng 'K' (ví dụ: 99k)" },
      { regex: /\b\d+(?:[.,]\d{3})*\s*(?:[đ₫dD]|VND|VNĐ|Vnd|Vnđ|USD|Usd|usd|\$)\b/i, msg: "Phát hiện giá trị tiền tệ kèm đơn vị (đ, ₫, VND, $)" },
      { regex: /\b\d{5,}\b/, msg: "Phát hiện dãy số lớn có thể là thông tin giá bán" },
      { regex: /\b(?:không|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|chục|trăm|lẻ|linh|mốt|tư|nhăm)\s+(?:không|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|chục|trăm|lẻ|linh|mốt|tư|nhăm|nghìn|ngàn|triệu|tỷ|đồng|k)*\s*(?:nghìn|ngàn|triệu|tỷ|đồng)\b/i, msg: "Phát hiện thông tin giá bằng chữ tiếng Việt" },
      { regex: /(?:giá\s+gốc|giảm\s+còn|flash\s+sale|rẻ\s+nhất\s+thị\s+trường|giá\s+hôm\s+nay|tiết\s+kiệm)/i, msg: "Phát hiện cụm quảng cáo giá cấm" }
    ];

    script.scenes.forEach((sc, idx) => {
      const texts = [sc.voiceover, sc.subtitle, sc.visualAction];
      texts.forEach(txt => {
        if (!txt) return;
        pricePatterns.forEach(pat => {
          if (pat.regex.test(txt)) {
            const matches = txt.match(pat.regex);
            const detail = matches ? ` ("${matches[0]}")` : '';
            issues.push(`Cảnh ${idx + 1}: ${pat.msg}${detail}`);
          }
        });
      });
    });

    return Array.from(new Set(issues));
  };

  const liveIssues = checkLivePriceSafety();
  const allValidationIssues = [
    ...(script.validationIssues || []),
    ...liveIssues
  ];

  return (
    <div className="space-y-5 animate-fadeIn">
      {/* Price Safety Rule Status Alert Box */}
      <div className={`p-4 rounded-xl border flex flex-col md:flex-row md:items-start justify-between gap-3 transition-all ${
        allValidationIssues.length > 0 
          ? 'bg-amber-500/10 border-amber-500/20 text-amber-200' 
          : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-200'
      }`}>
        <div className="flex items-start gap-3">
          {allValidationIssues.length > 0 ? (
            <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5 animate-bounce" />
          ) : (
            <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
          )}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold uppercase tracking-wide">
              {allValidationIssues.length > 0 ? "Cảnh báo An toàn Giá (Price Safety Validation)" : "Hệ thống An toàn Giá - Đạt chuẩn (Price Safety Approved)"}
            </h4>
            <p className="text-[11px] text-zinc-400 leading-relaxed max-w-2xl font-sans">
              {allValidationIssues.length > 0 
                ? "Hệ thống phát hiện hoặc đã tự động lọc nội dung chứa thông tin giá tiền tệ. Vui lòng điều chỉnh hoặc thay thế bằng các thông điệp an toàn được phép (ví dụ: 'Xem mức giá mới nhất tại trang sản phẩm')." 
                : "Kịch bản hoàn toàn không chứa bất kỳ giá trị tiền tệ thô, số tiền hoặc từ khóa định giá nào. Đạt tiêu chuẩn an toàn quảng cáo TikTok/Reels."
              }
            </p>
            {allValidationIssues.length > 0 && (
              <div className="bg-zinc-950/80 border border-zinc-850 rounded-lg p-2.5 max-h-[120px] overflow-y-auto">
                <ul className="list-disc pl-4 space-y-1 text-[10px] text-zinc-400 font-mono">
                  {allValidationIssues.map((issue, i) => (
                    <li key={i}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Visual Hook Header accent */}
      <div className="bg-zinc-950 border border-orange-500/15 p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full bg-orange-500 animate-pulse" />
          <div className="text-xs">
            <span className="text-zinc-400 font-medium">Bố cục tiếp cận: </span>
            <strong className="text-orange-500 font-bold uppercase">{script.hookType}</strong>
            <span className="text-zinc-600 font-mono mx-1.5">|</span>
            <span className="text-zinc-500 italic font-sans">{script.hookExplanation}</span>
          </div>
        </div>
      </div>

      {/* Split layout: Left (List) | Center (Editor) | Right (AI Suggestions) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left pane: Script Scene List */}
        <div className="lg:col-span-3 bg-zinc-900 border border-zinc-850 rounded-xl p-4 space-y-3.5 h-[400px] overflow-y-auto">
          <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block border-b border-zinc-850 pb-2">
            Danh Sách Phân Cảnh
          </span>
          <div className="space-y-2">
            {script.scenes.map((scene, idx) => {
              const isSelected = selectedSceneId === scene.id;
              return (
                <div
                  key={scene.id}
                  onClick={() => onSelectScene(scene.id)}
                  className={`p-2.5 rounded-lg border text-left cursor-pointer transition-all flex items-start gap-2.5 ${
                    isSelected
                      ? 'bg-zinc-800 border-orange-500/40 text-orange-500'
                      : 'bg-zinc-950/60 border-zinc-850 text-zinc-400 hover:bg-zinc-850 hover:text-zinc-200'
                  }`}
                >
                  <span className="w-5 h-5 rounded bg-zinc-900 text-[10px] font-mono font-bold flex items-center justify-center border border-zinc-800 shrink-0">
                    {idx + 1}
                  </span>
                  <div className="truncate flex-1">
                    <span className="text-[9px] font-mono block text-zinc-500">{scene.timecode}</span>
                    <p className="text-xs font-semibold truncate font-sans">{scene.subtitle}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Center pane: Script Scene Editor */}
        <div className="lg:col-span-6 bg-zinc-900 border border-zinc-850 rounded-xl p-5 flex flex-col justify-between h-[400px]">
          <div className="space-y-4 flex-1 overflow-y-auto pr-1">
            <div className="flex items-center justify-between border-b border-zinc-850 pb-2.5">
              <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block">
                Trình Biên Soạn Nội Dung
              </span>
              <span className="text-[10px] font-mono text-zinc-500 bg-zinc-950 px-2 py-0.5 rounded border border-zinc-850">
                Mốc: {selectedScene?.timecode || '00:00'}
              </span>
            </div>

            {selectedScene && (
              <div className="space-y-4 text-xs">
                {/* Visual Description Input */}
                <div>
                  <label className="text-[10px] font-mono font-bold text-zinc-500 block mb-1">CẢNH HÀNH ĐỘNG HÌNH ẢNH (VISUAL ACTION)</label>
                  <textarea
                    rows={2}
                    value={selectedScene.visualAction}
                    onChange={(e) => onUpdateScene(selectedScene.id, { visualAction: e.target.value })}
                    className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded px-3 py-2.5 focus:outline-none focus:border-orange-500 resize-none font-sans"
                    placeholder="Mô tả phân cảnh dọc..."
                  />
                </div>

                {/* Subtitle text */}
                <div>
                  <label className="text-[10px] font-mono font-bold text-zinc-500 block mb-1">CHỮ ĐÈ LÊN KHUNG HÌNH (SUBTITLE TEXT OVERLAY)</label>
                  <input
                    type="text"
                    value={selectedScene.subtitle}
                    onChange={(e) => onUpdateScene(selectedScene.id, { subtitle: e.target.value })}
                    className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded px-3 py-2 focus:outline-none focus:border-orange-500 font-sans"
                    placeholder="Phụ đề viết gọn, lôi cuốn..."
                  />
                </div>

                {/* Voiceover Speech text */}
                <div>
                  <div className="flex justify-between mb-1">
                    <label className="text-[10px] font-mono font-bold text-zinc-500 block">LỜI ĐỌC THOẠI (SPEECH FOR FISH TTS)</label>
                    <span className="text-[9px] font-mono text-zinc-500">Nên viết số bằng chữ</span>
                  </div>
                  <textarea
                    rows={2}
                    value={selectedScene.voiceover}
                    onChange={(e) => onUpdateScene(selectedScene.id, { voiceover: e.target.value })}
                    className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded px-3 py-2.5 focus:outline-none focus:border-orange-500 resize-none font-sans"
                    placeholder="Nói rõ ràng bằng tiếng Việt mượt mà..."
                  />
                </div>
              </div>
            )}
          </div>

          {/* Editor status indicator */}
          <div className="pt-3 border-t border-zinc-850 text-[10px] font-mono text-zinc-500 flex justify-between items-center bg-zinc-900/60 shrink-0">
            <span>* Tự động lưu mọi thay đổi</span>
            <span className="text-orange-500">Sẵn sàng xuất FFmpeg</span>
          </div>
        </div>

        {/* Right pane: AI Suggestions */}
        <div className="lg:col-span-3 bg-zinc-900 border border-zinc-850 rounded-xl p-4 space-y-4 h-[400px] overflow-y-auto">
          <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block border-b border-zinc-850 pb-2">
            Gợi Ý Sáng Tạo (AI)
          </span>
          <div className="space-y-3.5">
            {suggestions.map((sug) => (
              <div
                key={sug.id}
                className={`p-3 rounded-lg border text-xs leading-relaxed space-y-1 ${
                  sug.type === 'warning'
                    ? 'bg-amber-500/5 border-amber-500/15 text-amber-300'
                    : sug.type === 'success'
                    ? 'bg-emerald-500/5 border-emerald-500/15 text-emerald-300'
                    : 'bg-zinc-950 border-zinc-850 text-zinc-400'
                }`}
              >
                <div className="flex items-center gap-1.5 font-bold">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{sug.title}</span>
                </div>
                <p className="text-[11px] leading-relaxed text-zinc-400 font-sans">{sug.desc}</p>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Bottom Timeline segment */}
      <div className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl space-y-3">
        <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block">
          Dòng thời gian tuyến tính (Linear Timeline)
        </span>
        
        {/* Visual blocks segment */}
        <div className="grid grid-cols-5 md:grid-cols-8 gap-1.5 p-1 bg-zinc-950 border border-zinc-850 rounded-lg">
          {script.scenes.map((sc, index) => {
            const isSelected = selectedSceneId === sc.id;
            return (
              <div
                key={sc.id}
                onClick={() => onSelectScene(sc.id)}
                className={`p-2 rounded text-center cursor-pointer transition-all select-none ${
                  isSelected
                    ? 'bg-orange-600 text-white shadow shadow-orange-600/10'
                    : 'bg-zinc-900 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300'
                }`}
              >
                <span className="text-[9px] font-mono font-bold block">CẢNH {index + 1}</span>
                <span className="text-[8px] font-mono opacity-80 block">{sc.timecode}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
