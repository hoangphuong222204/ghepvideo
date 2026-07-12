import React from 'react';
import { HelpCircle, Keyboard, BookOpen, AlertCircle } from 'lucide-react';

export const HelpView: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn select-none">
      
      {/* Intro visual banner */}
      <div className="bg-gradient-to-r from-zinc-900 to-zinc-950 border border-zinc-850 p-5 rounded-xl flex items-center gap-3.5 shadow-md">
        <HelpCircle className="w-5 h-5 text-orange-500 animate-pulse" />
        <div className="space-y-0.5">
          <h3 className="text-sm font-bold text-zinc-200">Trọng tâm trợ giúp biên tập (Help Center)</h3>
          <p className="text-[10px] text-zinc-500">Tìm kiếm câu trả lời nhanh chóng cho các cấu hình âm học và bộ lọc FFmpeg</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 text-xs">
        
        {/* Help Docs */}
        <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl space-y-4 shadow-xl">
          <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-widest border-b border-zinc-850 pb-2 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-orange-500" />
            <span>Tài liệu vận hành nhanh</span>
          </h3>

          <div className="space-y-3.5 leading-relaxed text-zinc-400 font-sans">
            <div className="space-y-1">
              <strong className="text-zinc-200">1. Làm thế nào để lập kịch bản viral?</strong>
              <p>Hãy truy cập tab **Sản phẩm (Product)**, nạp thử mẫu nhanh hoặc nhập đầy đủ nỗi đau của khách hàng (pain points). Gemini AI sẽ dựa vào đó để đề xuất cấu trúc giữ chân tối ưu nhất.</p>
            </div>
            <div className="space-y-1">
              <strong className="text-zinc-200">2. Cấu hình Fish Speech như thế nào?</strong>
              <p>Đảm bảo đã viết các chữ số bằng chữ (ví dụ: 'chín mươi chín nghìn' thay vì '99k') để tránh việc AI đọc vấp hoặc đọc thiếu. Bạn cũng có thể kéo chỉnh thanh gạt tốc độ và cao độ phù hợp mảng video review dồn dập.</p>
            </div>
          </div>
        </div>

        {/* Keyboard Shortcuts */}
        <div className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl space-y-4 shadow-xl">
          <h3 className="text-xs font-bold text-zinc-300 uppercase tracking-widest border-b border-zinc-850 pb-2 flex items-center gap-2">
            <Keyboard className="w-4 h-4 text-orange-500" />
            <span>Phím tắt thao tác nhanh (Shortcuts)</span>
          </h3>

          <div className="space-y-3 font-mono">
            <div className="flex justify-between items-center py-1 border-b border-zinc-850/60 text-zinc-400">
              <span>Phát / Dừng thử giọng nói:</span>
              <span className="bg-zinc-950 text-orange-500 px-1.5 py-0.5 rounded border border-zinc-800 font-bold">Spacebar</span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-zinc-850/60 text-zinc-400">
              <span>Đổi nhanh phân cảnh:</span>
              <span className="bg-zinc-950 text-orange-500 px-1.5 py-0.5 rounded border border-zinc-800 font-bold">Ctrl + Tab</span>
            </div>
            <div className="flex justify-between items-center py-1 text-zinc-400">
              <span>Bắt đầu Render FFmpeg:</span>
              <span className="bg-zinc-950 text-orange-500 px-1.5 py-0.5 rounded border border-zinc-800 font-bold">Ctrl + Enter</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
