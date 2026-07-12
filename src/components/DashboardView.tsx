import React from 'react';
import {
  Activity, Play, FileText, Volume2, Subtitles, Video, RefreshCw, Layers, ArrowRight, Sparkles, CheckCircle, Flame, ShieldAlert
} from 'lucide-react';
import { MarketingScript, VoiceSettings } from '../types';

interface DashboardViewProps {
  script: MarketingScript | null;
  isLoading: boolean;
  error: string | null;
  onSelectPage: (page: string) => void;
  onLoadDemo: (data: any) => void;
  voiceSettings: VoiceSettings;
}

const RECENT_DEMOS = [
  {
    name: "Son Kem Lì Velvet Kiss",
    category: "Mỹ Phẩm",
    emoji: "💄",
    tone: "asymmetric_hook",
    duration: 30,
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
    name: "Nồi Chiên Không Dầu Smart Cook",
    category: "Gia dụng",
    emoji: "🍳",
    tone: "problem_solving",
    duration: 30,
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
    name: "Cáp Sạc Nhanh Titan Multi",
    category: "Phụ kiện công nghệ",
    emoji: "🔌",
    tone: "hype",
    duration: 15,
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

export const DashboardView: React.FC<DashboardViewProps> = ({
  script,
  isLoading,
  error,
  onSelectPage,
  onLoadDemo,
  voiceSettings
}) => {
  const calculateTotalWords = () => {
    if (!script) return 0;
    return script.scenes.reduce((acc, s) => acc + s.voiceover.split(/\s+/).filter(Boolean).length, 0);
  };

  return (
    <div className="space-y-6 select-none animate-fadeIn">
      {/* Intro Welcome Banner */}
      <div className="bg-gradient-to-r from-zinc-900 to-zinc-950 border border-zinc-850 p-5 rounded-xl relative overflow-hidden shadow-md">
        <div className="absolute top-0 right-0 p-3 font-mono text-[9px] tracking-widest text-zinc-700 uppercase font-semibold">
          AIMS CORE v1.2
        </div>
        <div className="flex items-start gap-4">
          <div className="p-3 bg-orange-500/10 text-orange-500 rounded-xl border border-orange-500/20 shadow-inner">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div className="space-y-1">
            <h2 className="text-base font-bold text-zinc-100 tracking-tight">AI Marketing Studio PRO - Bảng điều khiển tích hợp</h2>
            <p className="text-xs text-zinc-400 max-w-2xl leading-relaxed">
              Thiết kế video ngắn TikTok, Shorts, Reels quảng cáo bán hàng chuyên nghiệp. Sử dụng trí tuệ nhân tạo **Gemini 3.5 Flash** lập kịch bản thông minh, kết hợp với bộ phát giọng nói **Fish Speech** thuần Việt tự nhiên nhất.
            </p>
          </div>
        </div>
      </div>

      {/* Grid of System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Current Project */}
        <div className="bg-zinc-900/60 border border-zinc-850 p-4 rounded-xl flex flex-col justify-between h-28">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-wider">Dự Án Hiện Tại</span>
            <Video className="w-4 h-4 text-orange-500" />
          </div>
          <div className="mt-2">
            <h3 className="text-sm font-bold text-zinc-200 truncate">{script ? 'Video Quảng Cáo Sản Phẩm' : 'Chưa Tạo Dự Án'}</h3>
            <span className="text-[10px] font-mono text-zinc-500 block mt-0.5">
              {script ? `Độ dài: ${script.totalDuration}s | ${script.scenes.length} Phân cảnh` : 'Sẵn sàng sáng tạo'}
            </span>
          </div>
        </div>

        {/* Workflow Progress */}
        <div className="bg-zinc-900/60 border border-zinc-850 p-4 rounded-xl flex flex-col justify-between h-28">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-wider">Tiến Trình Workflow</span>
            <Layers className="w-4 h-4 text-[#3B82F6]" />
          </div>
          <div className="mt-2 space-y-1">
            <div className="flex justify-between text-[10px] font-mono text-zinc-400">
              <span>Trạng thái:</span>
              <span className="text-[#3B82F6] font-semibold">{script ? 'Kịch Bản Hoàn Tất' : 'Đang Đợi Dữ Liệu'}</span>
            </div>
            <div className="w-full bg-zinc-950 h-1 rounded overflow-hidden">
              <div className={`h-full ${script ? 'w-4/6 bg-[#3B82F6]' : 'w-1/6 bg-zinc-800'}`} />
            </div>
          </div>
        </div>

        {/* Backend Health Status */}
        <div className="bg-zinc-900/60 border border-zinc-850 p-4 rounded-xl flex flex-col justify-between h-28">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-wider">Sức Khỏe Hệ Thống</span>
            <Activity className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="grid grid-cols-2 gap-1 text-[9px] font-mono text-zinc-400">
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Gemini API</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>Fish Local</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>FFmpeg</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span>FastAPI</span>
            </div>
          </div>
        </div>

        {/* Quick Actions Widget */}
        <div className="bg-zinc-900/60 border border-zinc-850 p-4 rounded-xl flex flex-col justify-between h-28">
          <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-wider block">Thao Tác Nhanh</span>
          <div className="grid grid-cols-2 gap-1.5">
            <button
              onClick={() => onSelectPage('Product')}
              className="py-1 px-2 text-[10px] font-bold text-zinc-300 hover:text-white bg-zinc-950 hover:bg-zinc-800 rounded border border-zinc-800 transition-all text-left truncate cursor-pointer flex items-center justify-between"
            >
              <span>Tạo Kịch Bản</span>
              <ArrowRight className="w-2.5 h-2.5" />
            </button>
            <button
              onClick={() => onSelectPage('Render')}
              className="py-1 px-2 text-[10px] font-bold text-zinc-300 hover:text-white bg-zinc-950 hover:bg-zinc-800 rounded border border-zinc-800 transition-all text-left truncate cursor-pointer flex items-center justify-between"
            >
              <span>Biên Tập Video</span>
              <ArrowRight className="w-2.5 h-2.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Details + Recent Project catalog */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Components Overview */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-widest block">Thành phần phương tiện hiện tại</h3>

          {script ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Script card */}
              <div
                onClick={() => onSelectPage('AI Script')}
                className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl cursor-pointer hover:border-orange-500/40 hover:bg-zinc-900/80 transition-all space-y-2.5"
              >
                <div className="flex items-center justify-between border-b border-zinc-850 pb-1.5">
                  <span className="text-xs font-bold text-zinc-300 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-orange-500" />
                    Kịch Bản (Gemini)
                  </span>
                  <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-1.5 py-0.2 rounded font-bold">READY</span>
                </div>
                <div className="text-xs text-zinc-400 space-y-1 font-sans">
                  <p><strong className="text-zinc-300">Cách Hook:</strong> {script.hookType}</p>
                  <p><strong className="text-zinc-300">Tổng số cảnh:</strong> {script.scenes.length} phân cảnh ({script.totalDuration}s)</p>
                  <p className="line-clamp-2 text-[11px] italic text-zinc-500">"{script.hookExplanation}"</p>
                </div>
              </div>

              {/* Voice card */}
              <div
                onClick={() => onSelectPage('Voice')}
                className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl cursor-pointer hover:border-orange-500/40 hover:bg-zinc-900/80 transition-all space-y-2.5"
              >
                <div className="flex items-center justify-between border-b border-zinc-850 pb-1.5">
                  <span className="text-xs font-bold text-zinc-300 flex items-center gap-1.5">
                    <Volume2 className="w-3.5 h-3.5 text-[#3B82F6]" />
                    Giọng Đọc (Fish TTS)
                  </span>
                  <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-1.5 py-0.2 rounded font-bold">ACTIVE</span>
                </div>
                <div className="text-xs text-zinc-400 space-y-1">
                  <p><strong className="text-zinc-300">Giọng đọc chính:</strong> {voiceSettings.speaker === 'vi-female-warm' ? 'Nữ Miền Bắc' : voiceSettings.speaker === 'vi-male-natural' ? 'Nam Miền Bắc' : 'Giọng Miền Nam'}</p>
                  <p><strong className="text-zinc-300">Cảm xúc:</strong> {voiceSettings.emotion}</p>
                  <p><strong className="text-zinc-300">Nhịp độ phát:</strong> {voiceSettings.speed}x (Pitch: {voiceSettings.pitch}x)</p>
                </div>
              </div>

              {/* Subtitles card */}
              <div
                onClick={() => onSelectPage('Subtitle')}
                className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl cursor-pointer hover:border-orange-500/40 hover:bg-zinc-900/80 transition-all space-y-2.5"
              >
                <div className="flex items-center justify-between border-b border-zinc-850 pb-1.5">
                  <span className="text-xs font-bold text-zinc-300 flex items-center gap-1.5">
                    <Subtitles className="w-3.5 h-3.5 text-amber-500" />
                    Phụ Đề (Style ASS)
                  </span>
                  <span className="text-[10px] text-zinc-500 font-mono bg-zinc-800 px-1.5 py-0.2 rounded font-bold">BURNT-IN</span>
                </div>
                <div className="text-xs text-zinc-400 space-y-1">
                  <p><strong className="text-zinc-300">Màu chữ chính:</strong> Vàng chanh</p>
                  <p><strong className="text-zinc-300">Kiểu viền rộng:</strong> 3.5px Stroke (Đen)</p>
                  <p><strong className="text-zinc-300">Dữ liệu tệp xuất:</strong> Hỗ trợ định dạng SRT / ASS</p>
                </div>
              </div>

              {/* Video rendering card */}
              <div
                onClick={() => onSelectPage('Render')}
                className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl cursor-pointer hover:border-orange-500/40 hover:bg-zinc-900/80 transition-all space-y-2.5"
              >
                <div className="flex items-center justify-between border-b border-zinc-850 pb-1.5">
                  <span className="text-xs font-bold text-zinc-300 flex items-center gap-1.5">
                    <Video className="w-3.5 h-3.5 text-emerald-500" />
                    Bản Dịch Video (FFmpeg)
                  </span>
                  <span className="text-[10px] text-zinc-500 font-mono bg-zinc-800 px-1.5 py-0.2 rounded font-bold">LOCAL</span>
                </div>
                <div className="text-xs text-zinc-400 space-y-1">
                  <p><strong className="text-zinc-300">Kích cỡ khung dọc:</strong> 1080 x 1920 (TikTok)</p>
                  <p><strong className="text-zinc-300">Tốc độ khung hình:</strong> 30 FPS</p>
                  <p><strong className="text-zinc-300">Bộ mã hóa GPU:</strong> h264_nvenc (Cực nhanh)</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="border border-dashed border-zinc-850 rounded-2xl p-8 text-center text-zinc-500 bg-zinc-900/20">
              <Sparkles className="w-8 h-8 text-orange-500 mx-auto mb-2 animate-pulse" />
              <p className="text-xs font-semibold text-zinc-300">Kịch bản quảng cáo chưa được sáng tạo</p>
              <p className="text-[10px] text-zinc-500 mt-1 max-w-sm mx-auto">
                Hãy click vào tab **Sản phẩm (Product)** bên trái, điền một vài dòng thông tin sơ bộ để bắt đầu sáng tạo bằng Gemini AI.
              </p>
            </div>
          )}
        </div>

        {/* Demo / Sample Catalog */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-widest block">Thư viện mẫu kịch bản demo</h3>
          <div className="space-y-3">
            {RECENT_DEMOS.map((demo) => (
              <div
                key={demo.name}
                onClick={() => onLoadDemo(demo.data)}
                className="bg-zinc-900 border border-zinc-850 p-3 rounded-xl hover:border-orange-500/35 transition-all cursor-pointer flex items-center justify-between"
              >
                <div className="flex items-center gap-3 truncate">
                  <span className="text-xl bg-zinc-950 w-9 h-9 rounded-lg flex items-center justify-center border border-zinc-850 shrink-0">
                    {demo.emoji}
                  </span>
                  <div className="truncate">
                    <h4 className="text-xs font-bold text-zinc-200 truncate">{demo.name}</h4>
                    <span className="text-[9px] font-mono text-zinc-500 block mt-0.5">
                      {demo.category} • {demo.duration}s • {demo.tone === 'hype' ? 'Giảm giá sốc' : demo.tone === 'problem_solving' ? 'Giải quyết đau khổ' : 'Mở đầu phá cách'}
                    </span>
                  </div>
                </div>
                <div className="text-[10px] font-bold text-orange-500 bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/25 shrink-0 ml-2">
                  Nạp mẫu
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
