import React from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  RefreshCw,
  Radio,
  Mic,
  Brain,
  Globe,
  Monitor,
  Folder,
  Cpu,
} from 'lucide-react';

const ICON_MAP = {
  radio: Radio,
  mic: Mic,
  brain: Brain,
  globe: Globe,
  monitor: Monitor,
  folder: Folder,
  cpu: Cpu,
};

export const APIs = [
  { name: 'Gateway', port: 8080, icon: 'radio' },
  { name: 'Speech', port: 8000, icon: 'mic' },
  { name: 'Brain', port: 8001, icon: 'brain' },
  { name: 'Browser', port: 8002, icon: 'globe' },
  { name: 'Desktop', port: 8003, icon: 'monitor' },
  { name: 'File', port: 8004, icon: 'folder' },
  { name: 'Ollama', port: 11434, icon: 'cpu' },
];

/**
 * Determine online/offline status for a subsystem from gateway telemetry
 */
const getApiStatus = (name, statusData) => {
  if (!statusData) return 'offline';

  const apis = statusData.apis || {};
  const gatewayStatus = statusData.gateway || 'offline';
  const ollamaStatus = statusData.ollama || 'disconnected';

  switch (name.toLowerCase()) {
    case 'gateway':
      return gatewayStatus === 'online' ? 'online' : 'offline';
    case 'speech':
      return (apis.speech_api?.status || apis.speech?.status) === 'online' ? 'online' : 'offline';
    case 'brain':
      return (apis.brain_api?.status || apis.brain?.status) === 'online' ? 'online' : 'offline';
    case 'browser':
      return (apis.browser_api?.status || apis.browser?.status) === 'online' ? 'online' : 'offline';
    case 'desktop':
      return (apis.desktop_api?.status || apis.desktop?.status) === 'online' ? 'online' : 'offline';
    case 'file':
      return (apis.file_api?.status || apis.file?.status) === 'online' ? 'online' : 'offline';
    case 'ollama':
      return (ollamaStatus === 'connected' || ollamaStatus === 'online') ? 'online' : 'offline';
    default:
      return 'offline';
  }
};

/**
 * StatusGrid — Subsystem Telemetry Dashboard Panel
 * Monitors all 7 microservices with full subsystem names, port indicators, icons, and live status dots.
 */
export const StatusGrid = ({ statusData, isLoading, onRefresh }) => {
  const cardsWithStatus = APIs.map((api) => ({
    ...api,
    status: getApiStatus(api.name, statusData),
  }));

  const onlineCount = cardsWithStatus.filter((c) => c.status === 'online').length;

  return (
    <div className="glass-panel hud-corner-tl rounded-xl p-4 sm:p-5 flex flex-col gap-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2.5">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
          <h3 className="text-xs sm:text-sm font-bold tracking-wider text-cyan-300 font-orbitron uppercase">
            Subsystem Telemetry
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono-code px-2 py-0.5 rounded bg-cyan-950/40 border border-cyan-500/30 text-cyan-400">
            {onlineCount}/{APIs.length} ACTIVE
          </span>
          <button
            onClick={onRefresh}
            disabled={isLoading}
            title="Refresh API Status"
            className="p-1 rounded text-slate-400 hover:text-cyan-300 hover:bg-cyan-950/30 transition disabled:opacity-40 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* List of Subsystem Cards */}
      <div className="grid grid-cols-1 gap-2">
        {cardsWithStatus.map((item, idx) => {
          const Icon = ICON_MAP[item.icon] || Radio;
          const isOnline = item.status === 'online';

          if (isLoading && !statusData) {
            // Skeleton Loader
            return (
              <div
                key={item.name}
                className="h-14 rounded-lg bg-slate-900/60 border border-slate-800 animate-pulse"
              />
            );
          }

          return (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.04 }}
              className={`flex items-center justify-between px-3 py-2 rounded-lg border transition-all ${
                isOnline
                  ? 'bg-slate-950/60 border-cyan-500/25 hover:border-cyan-400/50 shadow-[0_0_10px_rgba(0,212,255,0.05)]'
                  : 'bg-rose-950/15 border-rose-500/20 hover:border-rose-500/35'
              }`}
            >
              {/* Left Side: Subsystem Icon + Full Name + Port */}
              <div className="flex items-center gap-2.5 min-w-0">
                <div
                  className={`p-1.5 rounded-md shrink-0 ${
                    isOnline
                      ? 'bg-cyan-950/60 text-cyan-400 border border-cyan-500/30 shadow-[0_0_8px_rgba(0,212,255,0.2)]'
                      : 'bg-rose-950/40 text-rose-400 border border-rose-500/30'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-semibold text-slate-100 tracking-wide font-orbitron whitespace-nowrap">
                    {item.name}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono-code">
                    PORT: {item.port}
                  </span>
                </div>
              </div>

              {/* Right Side: Status Indicator Dot & Label */}
              <div className="flex items-center gap-1.5 shrink-0 pl-2">
                <span className="relative flex h-2.5 w-2.5">
                  {isOnline && (
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  )}
                  <span
                    className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                      isOnline
                        ? 'bg-emerald-400 shadow-[0_0_8px_#00ff88]'
                        : 'bg-rose-500 shadow-[0_0_8px_#ff3366]'
                    }`}
                  />
                </span>
                <span
                  className={`text-[10px] font-bold uppercase tracking-wider font-mono-code ${
                    isOnline ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {isOnline ? 'ONLINE' : 'OFFLINE'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default StatusGrid;
