import React, { useState } from 'react';
import { MarketingScript, VideoScene, BackgroundAsset } from '../types';
import {
  Folder, Search, UploadCloud, Film, Music, Check, ArrowRight, Play, CheckCircle
} from 'lucide-react';

interface MediaViewProps {
  script: MarketingScript | null;
  selectedSceneId: string;
  onSelectScene: (id: string) => void;
}

const STOCK_ASSETS: BackgroundAsset[] = [
  { id: '1', name: 'son_kem_moi_closeup.mp4', url: '#', type: 'video', category: 'cosmetic' },
  { id: '2', name: 'model_female_smiling.mp4', url: '#', type: 'video', category: 'cosmetic' },
  { id: '3', name: 'kitchen_fry_cook.mp4', url: '#', type: 'video', category: 'food' },
  { id: '4', name: 'fry_chicken_crispy.mp4', url: '#', type: 'video', category: 'food' },
  { id: '5', name: 'usb_cable_strength.mp4', url: '#', type: 'video', category: 'tech' },
  { id: '6', name: 'power_charging_meter.mp4', url: '#', type: 'video', category: 'tech' },
  { id: '7', name: 'lof_beat_upbeat.mp3', url: '#', type: 'image', category: 'minimal' },
  { id: '8', name: 'cash_register_ding.mp3', url: '#', type: 'image', category: 'minimal' },
];

export const MediaView: React.FC<MediaViewProps> = ({
  script,
  selectedSceneId,
  onSelectScene,
}) => {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<'all' | 'tech' | 'cosmetic' | 'food' | 'minimal'>('all');
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  // Filter Stock Assets
  const filteredAssets = STOCK_ASSETS.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || asset.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  // Simulated Drag-and-Drop file upload
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const fileName = e.dataTransfer.files[0].name;
      simulateUpload(fileName);
    }
  };

  const simulateUpload = (fileName: string) => {
    setUploadProgress(0);
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev !== null && prev >= 100) {
          clearInterval(interval);
          setUploadedFiles(old => [...old, fileName]);
          return null;
        }
        return (prev || 0) + 20;
      });
    }, 150);
  };

  return (
    <div className="space-y-6 animate-fadeIn select-none">
      
      {/* Top Asset Filter & Search */}
      <div className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl flex flex-col md:flex-row gap-3 items-center justify-between shadow-md">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm kiếm tư liệu..."
            className="w-full bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded pl-9 pr-3 py-2 focus:outline-none focus:border-orange-500/80"
          />
        </div>

        {/* Category Filter pills */}
        <div className="flex gap-1.5 flex-wrap">
          {[
            { key: 'all', label: 'Tất cả' },
            { key: 'cosmetic', label: 'Mỹ phẩm' },
            { key: 'food', label: 'Đồ bếp' },
            { key: 'tech', label: 'Công nghệ' },
            { key: 'minimal', label: 'Âm thanh / SFX' },
          ].map(pill => (
            <button
              key={pill.key}
              onClick={() => setCategoryFilter(pill.key as any)}
              className={`py-1 px-3 text-[10px] font-bold rounded-full transition-all cursor-pointer ${
                categoryFilter === pill.key
                  ? 'bg-orange-600 text-white'
                  : 'bg-zinc-950 text-zinc-400 hover:text-zinc-200 border border-zinc-850 hover:border-zinc-700'
              }`}
            >
              {pill.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* Left: Stock Asset Grid */}
        <div className="lg:col-span-8 bg-zinc-900 border border-zinc-850 p-4.5 rounded-xl space-y-4 h-[350px] overflow-y-auto shadow-xl">
          <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block border-b border-zinc-850 pb-2">
            Thư viện tệp phương tiện có sẵn
          </span>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {filteredAssets.map(asset => (
              <div
                key={asset.id}
                className="bg-zinc-950 rounded-lg p-2.5 border border-zinc-850 flex flex-col justify-between hover:border-orange-500/30 transition-all cursor-pointer h-24"
              >
                <div className="flex justify-between items-start">
                  <span className="text-zinc-500">
                    {asset.type === 'video' ? <Film className="w-4 h-4 text-orange-500/80" /> : <Music className="w-4 h-4 text-sky-500/80" />}
                  </span>
                  <span className="text-[7.5px] font-mono uppercase bg-zinc-900 border border-zinc-850 px-1 rounded text-zinc-500">
                    {asset.category}
                  </span>
                </div>
                <p className="text-[10.5px] font-mono text-zinc-300 truncate font-semibold block mt-2">{asset.name}</p>
                <span className="text-[8px] font-mono text-zinc-600 block mt-0.5">Sẵn sàng kéo</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Upload Drag & Drop and simulated status */}
        <div className="lg:col-span-4 bg-zinc-900 border border-zinc-850 p-5 rounded-xl flex flex-col justify-between h-[350px] shadow-xl">
          <div className="space-y-4 flex-1">
            <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block border-b border-zinc-850 pb-2">
              Kéo thả / Tải tệp lên
            </span>

            {/* Upload Area */}
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`border border-dashed rounded-lg p-5 text-center flex flex-col items-center justify-center transition-all min-h-[140px] cursor-pointer ${
                dragActive
                  ? 'border-orange-500 bg-orange-500/5'
                  : 'border-zinc-800 hover:border-zinc-700 bg-zinc-950/60'
              }`}
            >
              <UploadCloud className="w-8 h-8 text-zinc-500 mb-2" />
              <p className="text-xs text-zinc-300 font-bold">Kéo thả video hoặc âm thanh mồi</p>
              <p className="text-[9px] text-zinc-500 font-mono mt-1">Hỗ trợ tệp MP4, WAV, MP3</p>

              {uploadProgress !== null && (
                <div className="w-full mt-3 space-y-1">
                  <div className="flex justify-between text-[8px] font-mono text-zinc-400">
                    <span>Đang nạp file...</span>
                    <span>{uploadProgress}%</span>
                  </div>
                  <div className="w-full bg-zinc-900 h-1 rounded overflow-hidden">
                    <div className="h-full bg-orange-500 transition-all" style={{ width: `${uploadProgress}%` }} />
                  </div>
                </div>
              )}
            </div>

            {/* Uploaded tệp list */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-1.5">
                <span className="text-[8px] font-mono text-zinc-500 uppercase block font-bold">Tệp vừa tải lên</span>
                <div className="space-y-1">
                  {uploadedFiles.map(file => (
                    <div key={file} className="flex items-center gap-1.5 text-[10.5px] font-mono text-emerald-400 bg-emerald-500/5 border border-emerald-500/10 p-1.5 rounded">
                      <CheckCircle className="w-3.5 h-3.5" />
                      <span className="truncate">{file}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="text-[9px] font-mono text-zinc-500 leading-relaxed bg-zinc-950/60 p-2.5 rounded border border-zinc-850 shrink-0">
            💡 **Ghép nối kịch bản Python:** Mọi tệp bạn tải lên ở đây sẽ tự động được gán vào kịch bản Python subprocess offline khi bạn click chạy render tệp.
          </div>
        </div>

      </div>

      {/* Multitrack Timeline block representing sequence tracks */}
      {script && (
        <div className="bg-zinc-900 border border-zinc-850 p-4 rounded-xl space-y-3.5 shadow-md">
          <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-widest block">
            Bảng rãnh biên tập đa lớp (Multitrack Timeline Tracks)
          </span>

          <div className="space-y-2 bg-zinc-950 border border-zinc-850 p-2.5 rounded-lg">
            
            {/* Row 1: Video Track */}
            <div className="flex items-center gap-3">
              <span className="w-16 text-[9px] font-mono font-bold text-zinc-500 uppercase shrink-0">Video Track:</span>
              <div className="flex-1 flex gap-1 items-center">
                {script.scenes.map((sc) => (
                  <div
                    key={sc.id}
                    onClick={() => onSelectScene(sc.id)}
                    className={`h-6 rounded text-[9.5px] font-mono flex items-center justify-center border truncate cursor-pointer transition-all ${
                      selectedSceneId === sc.id
                        ? 'bg-orange-600/15 border-orange-500 text-orange-500'
                        : 'bg-zinc-900 border-zinc-850 text-zinc-500'
                    }`}
                    style={{ width: `${100 / script.scenes.length}%` }}
                  >
                    Clips {sc.id}
                  </div>
                ))}
              </div>
            </div>

            {/* Row 2: Voice TTS Track */}
            <div className="flex items-center gap-3">
              <span className="w-16 text-[9px] font-mono font-bold text-zinc-500 uppercase shrink-0">Voice TTS:</span>
              <div className="flex-1 flex gap-1 items-center">
                {script.scenes.map((sc) => (
                  <div
                    key={sc.id}
                    onClick={() => onSelectScene(sc.id)}
                    className={`h-6 rounded text-[9.5px] font-mono flex items-center justify-center border truncate cursor-pointer transition-all ${
                      selectedSceneId === sc.id
                        ? 'bg-sky-500/15 border-sky-500 text-sky-500'
                        : 'bg-zinc-900 border-zinc-850 text-zinc-500'
                    }`}
                    style={{ width: `${100 / script.scenes.length}%` }}
                  >
                    Audio {sc.id}
                  </div>
                ))}
              </div>
            </div>

            {/* Row 3: Subtitles Track */}
            <div className="flex items-center gap-3">
              <span className="w-16 text-[9px] font-mono font-bold text-zinc-500 uppercase shrink-0">Subtitles:</span>
              <div className="flex-1 flex gap-1 items-center">
                {script.scenes.map((sc) => (
                  <div
                    key={sc.id}
                    onClick={() => onSelectScene(sc.id)}
                    className={`h-6 rounded text-[9.5px] font-mono flex items-center justify-center border truncate cursor-pointer transition-all ${
                      selectedSceneId === sc.id
                        ? 'bg-amber-500/15 border-amber-500 text-amber-500'
                        : 'bg-zinc-900 border-zinc-850 text-zinc-500'
                    }`}
                    style={{ width: `${100 / script.scenes.length}%` }}
                  >
                    Sub {sc.id}
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      )}
    </div>
  );
};
