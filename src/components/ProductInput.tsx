/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { ProductInfo } from '../types';
import { Sparkles, ShoppingBag, HelpCircle, Flame, GraduationCap, Compass, HelpCircle as HelpIcon, Smile } from 'lucide-react';

interface ProductInputProps {
  onGenerate: (info: ProductInfo) => void;
  isLoading: boolean;
}

const TEMPLATES: Array<{
  name: string;
  data: ProductInfo;
  emoji: string;
}> = [
  {
    name: "Son Kem Lì Mịn Môi (Cosmetics)",
    emoji: "💄",
    data: {
      name: "Son Kem Lì Velvet Kiss",
      category: "Mỹ Phẩm",
      keyFeatures: "Siêu lì suốt mười hai giờ, không trôi khi ăn uống, dưỡng ẩm cao từ bơ hạt mỡ, mịn môi như nhung.",
      targetAudience: "Học sinh sinh viên, nhân viên văn phòng bận rộn thích vẻ ngoài tự nhiên tươi tắn.",
      videoTone: "asymmetric_hook",
      duration: 30,
      priceInfo: "Hai trăm chín mươi chín nghìn đồng, đang giảm giá còn một trăm chín mươi chín nghìn đồng.",
      callToAction: "Nhấn vào giỏ hàng màu vàng góc trái màn hình nhận ngay ưu đãi số lượng có hạn!"
    }
  },
  {
    name: "Nồi Chiên Không Dầu Smart (Kitchen)",
    emoji: "🍳",
    data: {
      name: "Nồi Chiên Không Dầu Smart Cook",
      category: "Gia dụng",
      keyFeatures: "Dung tích lớn sáu lít, công nghệ nhiệt đối lưu ba trăm sáu mươi độ, giảm tám mươi lăm phần trăm dầu mỡ thừa, tự động ngắt điện.",
      targetAudience: "Các bà nội trợ bận rộn muốn chuẩn bị bữa ăn lành mạnh, an toàn và nhanh gọn cho cả gia đình.",
      videoTone: "problem_solving",
      duration: 30,
      priceInfo: "Một triệu tám trăm nghìn đồng, quà tặng kèm bộ khay lót silicon.",
      callToAction: "Mua ngay hôm nay để được miễn phí vận chuyển toàn quốc!"
    }
  },
  {
    name: "Cáp Sạc Nhanh Đa Năng 3-in-1 (Tech)",
    emoji: "🔌",
    data: {
      name: "Cáp Sạc Nhanh Titan Multi",
      category: "Phụ kiện công nghệ",
      keyFeatures: "Dây bọc dù siêu bền chịu lực kéo hai mươi cân, tích hợp ba đầu sạc khác nhau, sạc nhanh một trăm oát cho cả điện thoại và máy tính xách tay.",
      targetAudience: "Người dùng sử dụng nhiều thiết bị công nghệ cùng lúc, hay di chuyển và yêu thích sự gọn gàng.",
      videoTone: "hype",
      duration: 15,
      priceInfo: "Chín mươi chín nghìn đồng một sợi.",
      callToAction: "Đặt ngay tại nút mua bên dưới, cam kết bảo hành lỗi một đổi một trong vòng mười hai tháng!"
    }
  }
];

export const ProductInput: React.FC<ProductInputProps> = ({ onGenerate, isLoading }) => {
  const [form, setForm] = useState<ProductInfo>({
    name: '',
    category: '',
    keyFeatures: '',
    targetAudience: '',
    videoTone: 'problem_solving',
    duration: 30,
    priceInfo: '',
    callToAction: ''
  });

  const applyTemplate = (template: ProductInfo) => {
    setForm(template);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate(form);
  };

  const updateField = (key: keyof ProductInfo, value: any) => {
    setForm(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div id="product-input-card" className="bg-[#151515] border border-white/5 rounded-xl p-6 shadow-xl relative overflow-hidden">
      {/* Background radial accent */}
      <div className="absolute -top-24 -left-24 w-48 h-48 bg-[#FF3E00]/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-[#FF3E00]/10 rounded-lg text-[#FF3E00] border border-[#FF3E00]/20">
            <ShoppingBag className="w-5 h-5" />
          </div>
          <h2 className="text-xl font-semibold text-slate-100">Thông Tin Sản Phẩm</h2>
        </div>
        <span className="text-xs font-mono text-slate-500 bg-slate-950 px-2 py-1 rounded">VĨNH VIỄN MIỄN PHÍ</span>
      </div>

      {/* Templates Selector */}
      <div className="mb-6">
        <span className="text-xs font-medium text-slate-400 block mb-2">Chọn Mẫu Demo Nhanh:</span>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          {TEMPLATES.map((tmpl) => (
            <button
              id={`tmpl-btn-${tmpl.name.replace(/\s+/g, '-').toLowerCase()}`}
              key={tmpl.name}
              type="button"
              onClick={() => applyTemplate(tmpl.data)}
              className="flex items-center gap-2 text-left p-2.5 rounded-lg text-xs bg-slate-950/60 hover:bg-slate-800/80 text-slate-300 border border-slate-800/80 transition-all duration-150 active:scale-95"
            >
              <span>{tmpl.emoji}</span>
              <span className="truncate font-medium">{tmpl.name}</span>
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Name and Category */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Tên sản phẩm <span className="text-[#FF3E00]">*</span></label>
            <input
              id="product-name-input"
              type="text"
              required
              value={form.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="Ví dụ: Tai Nghe Không Dây Pro"
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#FF3E00]/60 focus:ring-1 focus:ring-[#FF3E00]/30 transition-all"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Ngành hàng / Phân loại</label>
            <input
              id="product-category-input"
              type="text"
              value={form.category}
              onChange={(e) => updateField('category', e.target.value)}
              placeholder="Ví dụ: Phụ kiện Điện thoại"
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#FF3E00]/60 focus:ring-1 focus:ring-[#FF3E00]/30 transition-all"
            />
          </div>
        </div>

        {/* Features */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="text-xs font-semibold text-slate-400">Các tính năng nổi bật (Dùng chữ thay vì ký hiệu số)</label>
            <span className="text-[10px] text-slate-500 italic">Ví dụ: sáu tiếng pin, không phải 6h</span>
          </div>
          <textarea
            id="product-features-input"
            rows={3}
            value={form.keyFeatures}
            onChange={(e) => updateField('keyFeatures', e.target.value)}
            placeholder="Mô tả các tính năng ưu việt, cách sử dụng. Để Fish Speech đọc mượt mà nhất, hãy ghi rõ số bằng chữ (ví dụ: 'mười hai giờ' thay vì '12h')."
            className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#FF3E00]/60 focus:ring-1 focus:ring-[#FF3E00]/30 transition-all resize-none"
          />
        </div>

        {/* Target Audience */}
        <div>
          <label className="text-xs font-semibold text-slate-400 block mb-1">Khách hàng mục tiêu</label>
          <input
            id="product-audience-input"
            type="text"
            value={form.targetAudience}
            onChange={(e) => updateField('targetAudience', e.target.value)}
            placeholder="Ví dụ: Nhân viên văn phòng thường bị đau mỏi vai gáy..."
            className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#FF3E00]/60 focus:ring-1 focus:ring-[#FF3E00]/30 transition-all"
          />
        </div>

        {/* Tone and Duration */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Cấu trúc / Tone kịch bản</label>
            <select
              id="product-tone-select"
              value={form.videoTone}
              onChange={(e) => updateField('videoTone', e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#FF3E00]/60 focus:ring-1 focus:ring-[#FF3E00]/30 transition-all"
            >
              <option value="problem_solving">Giải quyết vấn đề (Pain Point Focus)</option>
              <option value="asymmetric_hook">Mở đầu phá cách (Asymmetric Hook)</option>
              <option value="hype">Hype bùng nổ / Giảm giá sốc (Flash Sale)</option>
              <option value="educational">Chia sẻ kiến thức bổ ích (Educational)</option>
              <option value="storytelling">Kể chuyện trải nghiệm chân thật (Storytelling)</option>
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Thời lượng video (Dự kiến)</label>
            <div className="grid grid-cols-3 gap-2">
              {[15, 30, 60].map((t) => (
                <button
                  id={`duration-btn-${t}`}
                  key={t}
                  type="button"
                  onClick={() => updateField('duration', t)}
                  className={`py-2 text-xs font-mono font-medium rounded-lg border transition-all ${
                    form.duration === t
                      ? 'bg-[#FF3E00]/20 text-[#FF3E00] border-[#FF3E00]/40'
                      : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  {t} Giây
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Pricing & Call to Action */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Giá bán / Ưu đãi (Nên viết bằng chữ)</label>
            <input
              id="product-price-input"
              type="text"
              value={form.priceInfo}
              onChange={(e) => updateField('priceInfo', e.target.value)}
              placeholder="Ví dụ: chỉ chín mươi chín nghìn đồng..."
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#FF3E00]/60 focus:ring-1 focus:ring-[#FF3E00]/30 transition-all"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-400 block mb-1">Lời kêu gọi hành động (CTA)</label>
            <input
              id="product-cta-input"
              type="text"
              value={form.callToAction}
              onChange={(e) => updateField('callToAction', e.target.value)}
              placeholder="Ví dụ: Nhấn vào giỏ hàng bên dưới..."
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-[#FF3E00]/60 focus:ring-1 focus:ring-[#FF3E00]/30 transition-all"
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          id="generate-script-btn"
          type="submit"
          disabled={isLoading || !form.name}
          className={`w-full py-3 px-4 mt-2 font-semibold text-sm rounded-xl transition-all flex items-center justify-center gap-2 cursor-pointer ${
            isLoading || !form.name
              ? 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
              : 'bg-[#FF3E00] hover:bg-[#E03700] text-white hover:shadow-lg hover:shadow-[#FF3E00]/20 hover:-translate-y-[1px] active:translate-y-[1px]'
          }`}
        >
          {isLoading ? (
            <>
              <div className="w-5 h-5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
              <span>Đang Sáng Tạo Kịch Bản Bằng Gemini...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 text-slate-950 fill-slate-950 animate-pulse" />
              <span>Sáng Tạo Kịch Bản Viral Với Gemini AI</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
