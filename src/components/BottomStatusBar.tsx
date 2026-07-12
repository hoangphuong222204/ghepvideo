import React, { useEffect, useState } from 'react';
import { Cpu, Zap, Activity, HardDrive, Clock } from 'lucide-react';

interface BottomStatusBarProps {
  currentTask: string;
  workflowStatus: 'Idle' | 'Generating' | 'Rendering' | 'Completed' | 'Error';
  backendConnected: boolean;
}

export const BottomStatusBar: React.FC<BottomStatusBarProps> = ({
  currentTask,
  workflowStatus,
  backendConnected,
}) => {
  const [metrics, setMetrics] = useState({
    cpu: 18,
    gpu: 5,
    ram: 4.8,
  });

  const [elapsedTime, setElapsedTime] = useState(0);

  // Generate slightly fluctuating resource metrics for realism
  useEffect(() => {
    const timer = setInterval(() => {
      setMetrics(prev => {
        let cpuTarget = 15;
        let gpuTarget = 4;
        
        if (workflowStatus === 'Generating') {
          cpuTarget = 45;
          gpuTarget = 20;
        } else if (workflowStatus === 'Rendering') {
          cpuTarget = 85;
          gpuTarget = 75;
        }

        const deltaCpu = (Math.random() * 10 - 5) + (cpuTarget - prev.cpu) * 0.2;
        const deltaGpu = (Math.random() * 8 - 4) + (gpuTarget - prev.gpu) * 0.2;
        const deltaRam = (Math.random() * 0.2 - 0.1);

        const nextCpu = Math.max(2, Math.min(99, Math.round(prev.cpu + deltaCpu)));
        const nextGpu = Math.max(0, Math.min(99, Math.round(prev.gpu + deltaGpu)));
        const nextRam = Math.max(2.1, Math.min(15.8, parseFloat((prev.ram + deltaRam).toFixed(1))));

        return { cpu: nextCpu, gpu: nextGpu, ram: nextRam };
      });
    }, 2000);

    return () => clearInterval(timer);
  }, [workflowStatus]);

  // Elapsed stopwatch
  useEffect(() => {
    const clockTimer = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);
    return () => clearInterval(clockTimer);
  }, []);

  const formatTime = (secs: number) => {
    const h = Math.floor(secs / 3600).toString().padStart(2, '0');
    const m = Math.floor((secs % 3600) / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${h}:${m}:${s}`;
  };

  return (
    <footer className="h-7 bg-zinc-950 border-t border-zinc-800 flex items-center justify-between px-3 text-[10px] font-mono text-zinc-400 select-none shrink-0 z-20">
      {/* Left side: server health indicators */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <Activity className={`w-3 h-3 ${backendConnected ? 'text-emerald-500' : 'text-red-500 animate-pulse'}`} />
          <span className="text-zinc-500 font-bold uppercase">Backend:</span>
          <span className="text-zinc-300">{backendConnected ? 'Kết nối' : 'Mất kết nối'}</span>
        </div>

        <div className="h-3 w-[1px] bg-zinc-800" />

        <div className="flex items-center gap-1.5">
          <Zap className="w-3 h-3 text-[#3B82F6]" />
          <span className="text-zinc-500 font-bold uppercase">FastAPI:</span>
          <span className="text-zinc-300">Đang chạy (Cục bộ)</span>
        </div>

        <div className="h-3 w-[1px] bg-zinc-800" />

        <div className="flex items-center gap-1.5">
          <span className="text-zinc-500 font-bold uppercase">Workflow:</span>
          <span className={`px-1.5 py-0.2 rounded font-semibold text-[9px] uppercase ${
            workflowStatus === 'Idle' ? 'bg-zinc-800/80 text-zinc-300' :
            workflowStatus === 'Generating' ? 'bg-orange-500/20 text-orange-500 border border-orange-500/20 animate-pulse' :
            workflowStatus === 'Rendering' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/20 animate-pulse' :
            workflowStatus === 'Completed' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/20' :
            'bg-red-500/20 text-red-400 border border-red-500/20'
          }`}>
            {workflowStatus}
          </span>
        </div>
      </div>

      {/* Middle: Current Task indicator */}
      <div className="hidden md:flex items-center gap-2 truncate max-w-[30%] lg:max-w-[40%]">
        <span className="text-orange-500 font-semibold uppercase animate-pulse">●</span>
        <span className="text-zinc-500 uppercase font-bold">Nhiệm vụ:</span>
        <span className="text-zinc-200 truncate">{currentTask || 'Sẵn sàng'}</span>
      </div>

      {/* Right side: system hardware meters & elapsed stopwatch */}
      <div className="flex items-center gap-4">
        {/* CPU */}
        <div className="flex items-center gap-1">
          <Cpu className="w-3 h-3 text-zinc-500" />
          <span className="text-zinc-500">CPU:</span>
          <span className="text-zinc-300 font-semibold">{metrics.cpu}%</span>
        </div>

        {/* GPU */}
        <div className="flex items-center gap-1">
          <Zap className="w-3 h-3 text-zinc-500" />
          <span className="text-zinc-500">GPU:</span>
          <span className="text-zinc-300 font-semibold">{metrics.gpu}%</span>
        </div>

        {/* RAM */}
        <div className="flex items-center gap-1">
          <HardDrive className="w-3 h-3 text-zinc-500" />
          <span className="text-zinc-500">RAM:</span>
          <span className="text-zinc-300 font-semibold">{metrics.ram} GB</span>
        </div>

        <div className="h-3 w-[1px] bg-zinc-800" />

        {/* Stopwatch */}
        <div className="flex items-center gap-1.5 text-orange-500">
          <Clock className="w-3 h-3" />
          <span className="font-semibold">{formatTime(elapsedTime)}</span>
        </div>
      </div>
    </footer>
  );
};
