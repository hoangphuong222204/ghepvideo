/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import { ProductInfo, MarketingScript, VideoScene, VoiceSettings } from './types';
import { TopToolbar } from './components/TopToolbar';
import { BottomStatusBar } from './components/BottomStatusBar';
import { PreviewPanel } from './components/PreviewPanel';

// Sidebar Workspace Views
import { DashboardView } from './components/DashboardView';
import { ProductView } from './components/ProductView';
import { ScriptView } from './components/ScriptView';
import { VoiceView } from './components/VoiceView';
import { SubtitleView } from './components/SubtitleView';
import { MediaView } from './components/MediaView';
import { RenderView } from './components/RenderView';
import { WorkflowView } from './components/WorkflowView';
import { ProjectsView } from './components/ProjectsView';
import { TemplatesView } from './components/TemplatesView';
import { SettingsView } from './components/SettingsView';
import { LogsView } from './components/LogsView';
import { HelpView } from './components/HelpView';
import { AboutView } from './components/AboutView';

import {
  Activity, ShoppingBag, FileText, Volume2, Subtitles, Film, Video, Layers,
  FolderOpen, Database, Sparkles, Settings, Terminal, HelpCircle, Info, ShieldAlert
} from 'lucide-react';

export default function App() {
  const [activePage, setActivePage] = useState<string>('Dashboard');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [script, setScript] = useState<MarketingScript | null>(null);
  const [selectedSceneId, setSelectedSceneId] = useState<string>('');
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string>('Hệ thống hoạt động ổn định');
  const [workflowStatus, setWorkflowStatus] = useState<'Idle' | 'Generating' | 'Rendering' | 'Completed' | 'Error'>('Idle');

  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>({
    speaker: 'vi-female-warm',
    emotion: 'excited',
    speed: 1.0,
    pitch: 1.0,
  });

  const [formState, setFormState] = useState<ProductInfo>({
    name: "",
    category: "",
    brand: "",
    priceInfo: "",
    promotion: "",
    targetAudience: "",
    desire: "",
    platform: "TikTok Shop",
    videoTone: "asymmetric_hook",
    duration: 30,
    callToAction: "",
    advancedPrompt: "",
    keywords: "",
    forbiddenWords: "",
    keyFeatures: ""
  });

  // Diagnostics logs state
  const [diagnostics, setDiagnostics] = useState<string[]>([]);

  const addLog = (msg: string) => {
    setDiagnostics(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`].slice(-20));
  };

  // Web Speech API for TTS reads
  const handlePlayToggle = () => {
    if (isPlaying) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      addLog("Đã dừng phát thoại.");
      return;
    }

    if (!script) return;
    const selectedScene = script.scenes.find(s => s.id === selectedSceneId) || script.scenes[0];
    if (!selectedScene) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(selectedScene.voiceover);
    utterance.lang = 'vi-VN';
    utterance.rate = voiceSettings.speed;
    utterance.pitch = voiceSettings.pitch;

    utterance.onend = () => {
      setIsPlaying(false);
    };
    utterance.onerror = () => {
      setIsPlaying(false);
    };

    setIsPlaying(true);
    window.speechSynthesis.speak(utterance);
    addLog(`Đang phát đọc thử phân cảnh: "${selectedScene.voiceover.slice(0, 30)}..."`);
  };

  const handleGenerateScript = async (info: ProductInfo) => {
    setIsLoading(true);
    setError(null);
    setWorkflowStatus('Generating');
    setStatusMessage(`Đang biên soạn kịch bản video bằng Gemini cho sản phẩm: ${info.name}...`);
    addLog(`Bắt đầu pipeline lập kịch bản thông minh cho: '${info.name}'`);

    try {
      const response = await fetch('/api/generate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(info),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || 'Failed to generate script.');
      }

      const data = await response.json();
      setScript(data);
      if (data.scenes && data.scenes.length > 0) {
        setSelectedSceneId(data.scenes[0].id);
      }
      setWorkflowStatus('Idle');
      setStatusMessage('Đã tạo kịch bản quảng cáo thành công!');
      addLog(`SUCCESS: Lập kịch bản hoàn tất. Đã khởi tạo ${data.scenes?.length} phân cảnh video.`);
      // Redirect to kịch bản view immediately to see content
      setActivePage('AI Script');
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Một lỗi không xác định đã xảy ra.');
      setWorkflowStatus('Error');
      setStatusMessage('Gặp lỗi khi tạo kịch bản.');
      addLog(`ERROR: Thiết lập kịch bản thất bại. ${err.message || ''}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateScene = (sceneId: string, updatedFields: Partial<VideoScene>) => {
    if (!script) return;
    const updatedScenes = script.scenes.map(s => {
      if (s.id === sceneId) {
        return { ...s, ...updatedFields };
      }
      return s;
    });
    setScript({
      ...script,
      scenes: updatedScenes
    });
    addLog(`CẬP NHẬT: Phân cảnh ${sceneId} đã được chỉnh sửa.`);
  };

  const handleLoadDemo = (demoData: any) => {
    setFormState(demoData);
    setActivePage('Product');
    addLog(`Nạp mẫu thông số sản phẩm: ${demoData.name}`);
  };

  const handleClearScript = () => {
    setScript(null);
    setSelectedSceneId('');
    addLog("Đã dọn dẹp bộ đệm phiên hoạt động.");
  };

  const SIDEBAR_ITEMS = [
    { id: 'Dashboard', label: 'Dashboard', icon: Activity },
    { id: 'Product', label: 'Sản phẩm', icon: ShoppingBag },
    { id: 'AI Script', label: 'Kịch bản AI', icon: FileText },
    { id: 'Voice', label: 'Giọng đọc TTS', icon: Volume2 },
    { id: 'Subtitle', label: 'Phụ đề ASS', icon: Subtitles },
    { id: 'Media', label: 'Kho tư liệu', icon: Film },
    { id: 'Render', label: 'Xuất video', icon: Video },
    { id: 'Workflow', label: 'Workflow', icon: Layers },
    { id: 'Projects', label: 'Dự án', icon: FolderOpen },
    { id: 'Assets', label: 'Kho Assets', icon: Database },
    { id: 'Templates', label: 'Mẫu tối ưu', icon: Sparkles },
    { id: 'Settings', label: 'Thiết lập', icon: Settings },
    { id: 'Logs', label: 'Nhật ký logs', icon: Terminal },
    { id: 'Help', label: 'Trợ giúp', icon: HelpCircle },
    { id: 'About', label: 'Giới thiệu', icon: Info },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans select-none overflow-hidden antialiased">
      {/* Top Toolbar Workspace */}
      <TopToolbar
        currentProjectName={script ? formState.name || 'Dự án tiếp thị' : 'Chưa có kịch bản'}
        engineStatus={{
          gemini: 'active',
          fishSpeech: 'active',
          ffmpeg: 'active'
        }}
        onNewProject={() => {
          setFormState({
            name: "", category: "", brand: "", priceInfo: "", promotion: "",
            targetAudience: "", desire: "", platform: "TikTok Shop",
            videoTone: "asymmetric_hook", duration: 30, callToAction: "",
            advancedPrompt: "", keywords: "", forbiddenWords: "", keyFeatures: ""
          });
          setScript(null);
          setSelectedSceneId('');
          setActivePage('Product');
          addLog("Đã tạo mới phiên làm việc trống.");
        }}
        onImport={() => {
          const input = prompt("Dán chuỗi kịch bản JSON tiếp thị của bạn tại đây:");
          if (input) {
            try {
              const parsed = JSON.parse(input);
              setScript(parsed);
              if (parsed.scenes && parsed.scenes.length > 0) {
                setSelectedSceneId(parsed.scenes[0].id);
              }
              setActivePage('AI Script');
              addLog("Nhập kịch bản JSON thành công.");
            } catch (e) {
              alert("Chuỗi JSON không đúng định dạng!");
            }
          }
        }}
        onExport={() => {
          if (!script) {
            alert("Chưa có kịch bản hoạt động để xuất!");
            return;
          }
          const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(script, null, 2));
          const downloadAnchor = document.createElement('a');
          downloadAnchor.setAttribute("href", dataStr);
          downloadAnchor.setAttribute("download", "aims_marketing_script.json");
          document.body.appendChild(downloadAnchor);
          downloadAnchor.click();
          downloadAnchor.remove();
          addLog("Xuất file JSON kịch bản hoàn tất.");
        }}
      />

      {/* Main Workspace Frame container */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Sidebar panel list */}
        <aside className="w-20 bg-zinc-950 border-r border-zinc-800 flex flex-col items-center py-3 overflow-y-auto shrink-0 select-none z-10 gap-1.5 scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent">
          {SIDEBAR_ITEMS.map((item) => {
            const Icon = item.icon;
            const isSelected = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`w-16 h-14 rounded-lg flex flex-col items-center justify-center gap-1 transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-orange-600 text-white shadow-md shadow-orange-600/10'
                    : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-900/40'
                }`}
                title={item.label}
              >
                <Icon className="w-4.5 h-4.5" />
                <span className="text-[8.5px] scale-[0.9] font-medium truncate max-w-full px-0.5">
                  {item.id}
                </span>
              </button>
            );
          })}
        </aside>

        {/* Dynamic Center Workstation view */}
        <main className="flex-1 overflow-y-auto bg-zinc-950 p-6 flex flex-col">
          
          {/* Error Banner overlay */}
          {error && (
            <div className="bg-red-950/20 border border-red-500/30 rounded-xl p-4 flex gap-3 items-start mb-5 animate-fadeIn">
              <ShieldAlert className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h4 className="text-xs font-black text-red-400 uppercase font-mono tracking-wider">LỖI PIPELINE THỰC THI</h4>
                <p className="text-xs text-zinc-300">{error}</p>
                {error.includes("Secrets") && (
                  <p className="text-xs text-amber-300 mt-1">
                    💡 Để chạy lập kịch bản bằng Gemini AI, hãy thêm biến môi trường <strong>GEMINI_API_KEY</strong> trong menu <strong>Settings</strong> của trình biên tập.
                  </p>
                )}
              </div>
            </div>
          )}

          {/* View Router */}
          <div className="flex-1">
            {activePage === 'Dashboard' && (
              <DashboardView
                script={script}
                isLoading={isLoading}
                error={error}
                onSelectPage={setActivePage}
                onLoadDemo={handleLoadDemo}
                voiceSettings={voiceSettings}
              />
            )}

            {activePage === 'Product' && (
              <ProductView
                onGenerate={handleGenerateScript}
                isLoading={isLoading}
                formState={formState}
                onFormChange={setFormState}
              />
            )}

            {activePage === 'AI Script' && (
              <ScriptView
                script={script}
                selectedSceneId={selectedSceneId}
                onSelectScene={setSelectedSceneId}
                onUpdateScene={handleUpdateScene}
              />
            )}

            {activePage === 'Voice' && (
              <VoiceView
                scenes={script?.scenes || []}
                settings={voiceSettings}
                onUpdateSettings={setVoiceSettings}
                selectedSceneId={selectedSceneId}
                onSelectScene={setSelectedSceneId}
                isPlaying={isPlaying}
                onPlayToggle={handlePlayToggle}
              />
            )}

            {activePage === 'Subtitle' && (
              <SubtitleView
                script={script}
                selectedSceneId={selectedSceneId}
                onSelectScene={setSelectedSceneId}
                onUpdateScene={handleUpdateScene}
              />
            )}

            {activePage === 'Media' && (
              <MediaView
                script={script}
                selectedSceneId={selectedSceneId}
                onSelectScene={setSelectedSceneId}
              />
            )}

            {activePage === 'Render' && (
              <RenderView
                script={script}
                onSetStatusMessage={setStatusMessage}
                onSetWorkflowStatus={setWorkflowStatus}
              />
            )}

            {activePage === 'Workflow' && <WorkflowView />}

            {activePage === 'Projects' && (
              <ProjectsView
                script={script}
                onLoadDemo={handleLoadDemo}
                onClearScript={handleClearScript}
              />
            )}

            {activePage === 'Assets' && (
              <MediaView
                script={script}
                selectedSceneId={selectedSceneId}
                onSelectScene={setSelectedSceneId}
              />
            )}

            {activePage === 'Templates' && <TemplatesView />}

            {activePage === 'Settings' && <SettingsView />}

            {activePage === 'Logs' && <LogsView />}

            {activePage === 'Help' && <HelpView />}

            {activePage === 'About' && <AboutView />}
          </div>
        </main>

        {/* Right side smartphone preview panel */}
        <PreviewPanel
          script={script}
          selectedSceneId={selectedSceneId}
          onSelectScene={setSelectedSceneId}
          voiceSettings={voiceSettings}
          onUpdateVoiceSettings={setVoiceSettings}
          isPlaying={isPlaying}
          onPlayToggle={handlePlayToggle}
        />

      </div>

      {/* Bottom Status Bar */}
      <BottomStatusBar
        currentTask={statusMessage}
        workflowStatus={workflowStatus}
        backendConnected={true}
      />
    </div>
  );
}
