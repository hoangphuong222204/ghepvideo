import React, { useState } from 'react';
import { ProductInfo } from '../types';
import { 
  Sparkles, 
  ClipboardPaste, 
  Trash2, 
  Upload, 
  AlertTriangle, 
  Check, 
  HelpCircle, 
  Info, 
  ShieldAlert,
  FileText
} from 'lucide-react';

interface ProductViewProps {
  onGenerate: (info: ProductInfo) => void;
  isLoading: boolean;
  formState: ProductInfo;
  onFormChange: (form: ProductInfo) => void;
}

const TEMPLATES = [
  {
    name: "Son Kem Lì Velvet Kiss (Cosmetics)",
    emoji: "💄",
    rawText: "Son Kem Lì Velvet Kiss Beauty - Thương hiệu Velvet Kiss. Ngành hàng Mỹ Phẩm. Giá gốc 299.000đ giảm còn 199K. Flash Sale chỉ hôm nay tặng kèm một mặt nạ môi khi đặt hàng trong livestream! Khách hàng mục tiêu là học sinh sinh viên, nhân viên văn phòng bận rộn. Có nhu cầu giữ môi luôn rạng rỡ, không trôi suốt 12 tiếng ăn uống, dưỡng ẩm cao từ bơ hạt mỡ, mịn môi như nhung. Thường xuyên bị trôi son khi đi tiệc ăn uống để lại vệt son mờ nhạt gây tự tin. Đăng trên TikTok Shop."
  },
  {
    name: "Nồi Chiên Smart Cook (Kitchen)",
    emoji: "🍳",
    rawText: "Nồi Chiên Không Dầu Smart Cook Kitchen - Thương hiệu Smart Cook Kitchen. Ngành hàng Gia dụng. Giá bán một triệu tám trăm nghìn đồng. Tặng kèm bộ khay lót silicon chống dính cao cấp và Freeship toàn quốc! Khách hàng mục tiêu là các bà nội trợ bận rộn muốn chuẩn bị bữa ăn lành mạnh. Giảm lượng dầu mỡ tối đa, nấu nướng nhanh không cần canh chừng, tự ngắt thông minh. Dung tích lớn sáu lít, công nghệ nhiệt đối lưu ba trăm sáu mươi độ, giảm tám mươi lăm phần trăm dầu mỡ thừa. Đăng trên Shopee Video."
  },
  {
    name: "Cáp Sạc Titan Multi (Tech)",
    emoji: "🔌",
    rawText: "Cáp Sạc Nhanh Titan Multi - Thương hiệu Titan Accessories. Ngành hàng Phụ kiện công nghệ. Giá chín mươi chín nghìn đồng một sợi. Bảo hành lỗi một đổi một trong vòng mười hai tháng, giảm ngay 20K hôm nay. Dây bọc dù siêu bền chịu lực kéo hai mươi cân, tích hợp ba đầu sạc khác nhau, sạc nhanh một trăm oát cho cả điện thoại và máy tính xách tay. Đối tượng là người dùng sử dụng nhiều thiết bị công nghệ cùng lúc. Đăng trên Facebook Reels."
  }
];

export const ProductView: React.FC<ProductViewProps> = ({
  onGenerate,
  isLoading,
  formState,
  onFormChange,
}) => {
  const [rawText, setRawText] = useState<string>('');
  const [isExtracting, setIsExtracting] = useState<boolean>(false);
  const [extractError, setExtractError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const applyTemplate = (text: string) => {
    setRawText(text);
    setExtractError(null);
    setSuccessMessage(null);
  };

  const handlePasteClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        setRawText(text);
        setExtractError(null);
      }
    } catch (err) {
      console.error("Clipboard access failed, using fallback alert", err);
      setExtractError("Không thể tự động đọc clipboard. Hãy dùng tổ hợp phím Ctrl+V hoặc Cmd+V để dán trực tiếp.");
    }
  };

  const handleClear = () => {
    setRawText('');
    setExtractError(null);
    setSuccessMessage(null);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      if (text) {
        setRawText(text);
        setExtractError(null);
        setSuccessMessage("✨ Đã tải lên nội dung từ file thành công!");
        setTimeout(() => setSuccessMessage(null), 3000);
      }
    };
    reader.onerror = () => {
      setExtractError("Có lỗi xảy ra khi đọc file.");
    };
    reader.readAsText(file);
  };

  const handleAnalyzeAndGenerate = async () => {
    if (!rawText.trim()) {
      setExtractError("Vui lòng nhập hoặc dán thông tin chi tiết sản phẩm trước khi phân tích.");
      return;
    }

    setIsExtracting(true);
    setExtractError(null);
    setSuccessMessage(null);

    try {
      // Step 1: Call Gemini parser to extract structured information
      const res = await fetch('/api/extract-product-info', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rawText }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || "Gặp lỗi khi kết nối với máy chủ phân tích Gemini.");
      }

      const extractedData = await res.json();
      
      // Update form state parent component
      onFormChange(extractedData);
      setSuccessMessage("✨ Đã phân tách dữ liệu an toàn thành công! Đang tự động lập kịch bản video viral...");

      // Step 2: Trigger immediate script generation for streamlined 1-click UX
      onGenerate(extractedData);
    } catch (err: any) {
      console.error("Extraction error:", err);
      setExtractError(err.message || "Không thể phân tích dữ liệu sản phẩm.");
      setIsExtracting(false);
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      {/* Preset Quick Select bar */}
      <div className="bg-zinc-900/60 border border-zinc-850 p-4 rounded-xl">
        <span className="text-xs font-mono font-bold text-zinc-500 uppercase tracking-wider block mb-3">
          Chọn mẫu kịch bản tối ưu sẵn
        </span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
          {TEMPLATES.map((tmpl) => (
            <button
              key={tmpl.name}
              type="button"
              onClick={() => applyTemplate(tmpl.rawText)}
              className="flex items-center gap-3 text-left p-3 rounded-lg text-xs bg-zinc-950 hover:bg-zinc-800 border border-zinc-850 hover:border-zinc-700 transition-all active:scale-98 cursor-pointer group"
            >
              <span className="text-xl group-hover:scale-110 transition-transform">{tmpl.emoji}</span>
              <div className="truncate">
                <span className="font-bold text-zinc-200 block truncate">{tmpl.name}</span>
                <span className="text-[10px] text-zinc-500 font-mono">Bấm để nạp thông tin thô</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Single Card Workstation */}
      <div className="bg-zinc-950 border border-zinc-800 rounded-2xl overflow-hidden shadow-2xl">
        {/* Card Header */}
        <div className="bg-zinc-900/80 px-6 py-4 border-b border-zinc-850 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-600/10 text-orange-500 rounded-lg">
              <span className="text-xl">📦</span>
            </div>
            <div>
              <h2 className="text-sm font-bold text-zinc-100 uppercase tracking-wide">Thông tin sản phẩm</h2>
              <p className="text-[10px] text-zinc-500 font-mono">Dán mô tả để AI tự động phân tích và bóc tách</p>
            </div>
          </div>
          <span className="text-[10px] font-mono font-bold text-zinc-400 bg-zinc-950 border border-zinc-850 px-2.5 py-1 rounded-md">
            AIMS ENGINE v2.0
          </span>
        </div>

        {/* Card Body */}
        <div className="p-6 space-y-5">
          {/* Main Textarea input */}
          <div className="space-y-2">
            <textarea
              id="raw-product-textarea"
              rows={10}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Dán toàn bộ thông tin sản phẩm từ Shopee, TikTok Shop, Lazada, Website hoặc Facebook vào đây..."
              className="w-full bg-zinc-900/60 border border-zinc-800 text-zinc-200 text-xs rounded-xl p-4 focus:outline-none focus:border-orange-500/80 focus:ring-1 focus:ring-orange-500/50 resize-y font-sans leading-relaxed"
            />
          </div>

          {/* Action Button Bar */}
          <div className="flex flex-wrap gap-2 items-center justify-between bg-zinc-900/40 border border-zinc-850/60 px-4 py-3 rounded-xl">
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={handlePasteClipboard}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-750 text-zinc-300 font-semibold text-xs transition-all cursor-pointer active:scale-95"
              >
                <ClipboardPaste className="w-3.5 h-3.5 text-zinc-400" />
                <span>Dán từ Clipboard</span>
              </button>

              <label
                htmlFor="file-upload"
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-750 text-zinc-300 font-semibold text-xs transition-all cursor-pointer active:scale-95"
              >
                <Upload className="w-3.5 h-3.5 text-zinc-400" />
                <span>Tải file TXT</span>
                <input
                  id="file-upload"
                  type="file"
                  accept=".txt"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </label>

              <button
                type="button"
                onClick={handleClear}
                disabled={!rawText}
                className={`flex items-center gap-1.5 px-3.5 py-2 rounded-lg font-semibold text-xs transition-all cursor-pointer active:scale-95 ${
                  rawText 
                    ? 'bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-red-400 hover:text-red-300' 
                    : 'opacity-50 cursor-not-allowed text-zinc-600'
                }`}
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Xóa sạch</span>
              </button>
            </div>

            <span className="text-[10px] text-zinc-500 font-mono">
              Ký tự: {rawText.length}
            </span>
          </div>

          {/* Status Alert Panels */}
          {extractError && (
            <div className="bg-red-950/25 border border-red-500/30 p-3.5 rounded-xl flex items-start gap-2.5 text-red-400 text-xs">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{extractError}</span>
            </div>
          )}

          {successMessage && (
            <div className="bg-emerald-950/25 border border-emerald-500/30 p-3.5 rounded-xl flex items-start gap-2.5 text-emerald-400 text-xs font-semibold animate-pulse">
              <Check className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{successMessage}</span>
            </div>
          )}

          {/* Guidelines and Safety Warnings in Dual Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            {/* Note Panel */}
            <div className="bg-zinc-900/40 border border-zinc-850 p-4 rounded-xl space-y-2.5">
              <div className="flex items-center gap-2 text-zinc-300 font-bold text-xs">
                <Info className="w-4 h-4 text-sky-500" />
                <span>Hướng dẫn quy trình</span>
              </div>
              <p className="text-zinc-400 text-xs leading-relaxed">
                Hệ thống sẽ tự động phân tích nội dung sản phẩm thô vừa dán và trích xuất chỉ những thông tin có giá trị lâu dài cho kịch bản tiếp thị video.
              </p>
            </div>

            {/* Warning Safety Panel */}
            <div className="bg-orange-950/15 border border-orange-500/20 p-4 rounded-xl space-y-2.5">
              <div className="flex items-center gap-2 text-orange-400 font-bold text-xs">
                <ShieldAlert className="w-4 h-4" />
                <span>LUẬT AN TOÀN GIÁ (PRICE SAFETY RULE)</span>
              </div>
              <div className="space-y-1.5">
                <p className="text-zinc-400 text-[11px] leading-relaxed">
                  Để tránh vi phạm chính sách hiển thị và giá trị lỗi thời, hệ thống sẽ <strong>tự động loại bỏ hoàn toàn</strong>:
                </p>
                <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-zinc-400 text-[11px] pl-3">
                  <div className="flex items-center gap-1.5">• Giá sản phẩm</div>
                  <div className="flex items-center gap-1.5">• Khuyến mãi</div>
                  <div className="flex items-center gap-1.5">• Quà tặng</div>
                  <div className="flex items-center gap-1.5">• Voucher</div>
                  <div className="flex items-center gap-1.5">• Flash Sale</div>
                  <div className="flex items-center gap-1.5">• Freeship</div>
                  <div className="flex items-center gap-1.5 col-span-2">• Các thông tin có thể thay đổi</div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Huge 1-Click Launch Button */}
          <div className="pt-4 border-t border-zinc-900 flex justify-end">
            <button
              id="analyze-generate-btn-redesign"
              type="button"
              onClick={handleAnalyzeAndGenerate}
              disabled={isExtracting || isLoading || !rawText.trim()}
              className={`w-full md:w-auto px-10 py-4.5 rounded-xl font-bold text-sm tracking-wide transition-all duration-300 flex items-center justify-center gap-3 shadow-lg active:scale-98 cursor-pointer ${
                isExtracting || isLoading || !rawText.trim()
                  ? 'bg-zinc-850 border border-zinc-800 text-zinc-500 cursor-not-allowed'
                  : 'bg-orange-600 hover:bg-orange-500 text-white shadow-orange-600/10 hover:shadow-orange-600/20'
              }`}
            >
              {isExtracting || isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <div className="text-left">
                    <span className="block font-bold">AIMS ENGINE ĐANG CHẠY...</span>
                    <span className="block text-[10px] font-normal text-zinc-300 font-mono">Đang trích xuất & lập kịch bản tiếp thị</span>
                  </div>
                </>
              ) : (
                <>
                  <Sparkles className="w-4.5 h-4.5 text-white fill-white animate-pulse" />
                  <div className="text-left">
                    <span className="block font-bold uppercase">Phân tích thông tin & Tạo kịch bản ✨</span>
                    <span className="block text-[10px] font-normal text-orange-200">Bấm 1-Click để chuyển tiếp sang lập kịch bản video</span>
                  </div>
                </>
              )}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};
