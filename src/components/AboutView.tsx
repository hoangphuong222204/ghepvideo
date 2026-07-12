import React from 'react';
import { Info, Shield, Cpu, Heart } from 'lucide-react';

export const AboutView: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn select-none">
      
      {/* Product Spec Panel */}
      <div className="bg-zinc-900 border border-zinc-850 p-6 rounded-2xl relative overflow-hidden flex flex-col items-center justify-center text-center shadow-xl max-w-2xl mx-auto min-h-[340px]">
        
        {/* Glowing Orange Backdrop Sphere */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-32 h-32 bg-orange-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="w-14 h-14 bg-gradient-to-br from-orange-600 to-orange-500 rounded-2xl flex items-center justify-center font-black text-xl italic text-white shadow-xl shadow-orange-600/20 mb-4 z-10">
          M
        </div>

        <div className="space-y-1.5 z-10">
          <h3 className="text-sm font-bold text-zinc-100 flex items-center justify-center gap-1.5 font-sans">
            AI MARKETING STUDIO <span className="font-black italic text-orange-500">PRO</span>
          </h3>
          <p className="text-[10px] font-mono font-bold text-zinc-500 tracking-widest uppercase">Version 1.2.0-Release</p>
        </div>

        <p className="text-xs text-zinc-400 font-sans max-w-md mt-4 leading-relaxed">
          Phần mềm biên tập video tiếp thị tự động chuyên dụng cao cấp chạy trên nền tảng máy khách và máy chủ của doanh nghiệp. Đã được tích hợp bộ lọc drawtext song song cùng AI chuyển giọng nói Việt hóa Fish Speech.
        </p>

        {/* Specs breakdown */}
        <div className="grid grid-cols-2 gap-4 border-t border-zinc-850 mt-6 pt-5 w-full max-w-sm text-left text-[11px] font-mono text-zinc-500">
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-zinc-600" />
            <span>Node Core: ESM/CJS</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-zinc-600" />
            <span>Licence: Enterprise PRO</span>
          </div>
        </div>

        {/* Made with love */}
        <div className="flex items-center gap-1 text-[10px] text-zinc-600 font-mono mt-8 z-10">
          <span>Sáng tạo bởi đội ngũ AIMS Engineering</span>
          <Heart className="w-3 h-3 text-red-500 fill-red-500" />
        </div>
      </div>
    </div>
  );
};
