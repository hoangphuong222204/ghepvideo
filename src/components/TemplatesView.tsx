import React from 'react';
import { Sparkles, PlayCircle, Star, HelpCircle } from 'lucide-react';

export const TemplatesView: React.FC = () => {
  const formulas = [
    {
      id: "f1",
      name: "Công thức Hook Bất Đối Xứng (Asymmetric Hook)",
      desc: "Chặn đứng người xem bằng một câu vô lý hoặc một hình ảnh nghịch lý ngay trong 1.5 giây đầu tiên. Phù hợp cho TikTok Shop mảng mỹ phẩm và thời trang.",
      metrics: "Giữ chân 3s đầu: +35% • Tỷ lệ click: Cao"
    },
    {
      id: "f2",
      name: "Công thức Giải Quyết Đau Khổ (Pain Point Focus)",
      desc: "Phơi bày rắc rối cực kỳ ức chế mà khách hàng thường xuyên gặp phải, sau đó từ từ đưa sản phẩm ra như một vị cứu tinh duy nhất. Phù hợp cho hàng gia dụng, công nghệ.",
      metrics: "Tỷ lệ chuyển đổi: +18% • Uy tín: Cao"
    },
    {
      id: "f3",
      name: "Công thức Đánh Nhanh Rút Gọn (Flash Sale Hype)",
      desc: "Tập trung bùng nổ hiệu ứng âm thanh, dồn dập đưa ra quà tặng lớn, deal sốc giảm giá kịch sàn để hối thúc đặt hàng lập tức. Phù hợp livestream và ads kéo phễu.",
      metrics: "Tỷ lệ thêm giỏ hàng: +28% • Pacing: Cực nhanh"
    },
    {
      id: "f4",
      name: "Công thức Review Khoa Học (Educational Tech)",
      desc: "Khai thác trực diện vào số liệu kỹ thuật, bằng chứng thực tế, so sánh trực quan độ bền, nguồn gốc xuất xứ rõ ràng để thuyết phục khách hàng khó tính.",
      metrics: "Độ tin cậy: Tuyệt đối • Đăng ký mua: Tốt"
    }
  ];

  return (
    <div className="space-y-6 animate-fadeIn select-none">
      
      {/* Visual blueprint bar */}
      <div className="bg-zinc-950 border border-zinc-800 p-4 rounded-xl flex items-center justify-between shadow-md">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 bg-orange-600/15 text-orange-500 rounded">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-zinc-200">Kho công thức copywriting viral</h3>
            <p className="text-[10px] text-zinc-500">Bộ khung kịch bản đã được kiểm nghiệm thực tế giúp bùng nổ doanh số tiếp thị</p>
          </div>
        </div>
      </div>

      {/* Grid of formulas card widgets */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {formulas.map((item) => (
          <div
            key={item.id}
            className="bg-zinc-900 border border-zinc-850 p-5 rounded-xl hover:border-orange-500/30 transition-all flex flex-col justify-between"
          >
            <div className="space-y-2.5">
              <div className="flex justify-between items-start">
                <h4 className="text-xs font-bold text-zinc-200 leading-snug">{item.name}</h4>
                <Star className="w-3.5 h-3.5 text-orange-500 fill-orange-500 shrink-0" />
              </div>
              <p className="text-[11px] leading-relaxed text-zinc-400 font-sans">{item.desc}</p>
            </div>

            <div className="border-t border-zinc-850/60 mt-4 pt-3 flex justify-between items-center text-[10px] font-mono">
              <span className="text-zinc-500">{item.metrics}</span>
              <button
                onClick={() => alert("Đã áp dụng định hướng viết kịch bản!")}
                className="text-orange-500 hover:text-orange-400 font-bold cursor-pointer"
              >
                Áp dụng
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
