import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Mic, Send, Cpu, RefreshCw, CornerDownLeft,
  Zap, Radio, Brain, Globe, Monitor, Folder,
  Activity, Terminal, CheckCircle, XCircle,
  Clock, Bot, X, AlertCircle, CheckCircle2,
  AlertTriangle, MicOff,
} from 'lucide-react';

import ParticleBackground from './components/ParticleBackground';
import {
  sendTextCommand,
  sendAudioCommand,
  getSystemStatus,
  getHistory,
} from './services/api';

/* ========================================================
   CONFIG
   ======================================================== */
const QUICK_PROMPTS = [
  'Arijit Singh ke gaane chalao',
  'Take a screenshot and save to desktop',
  'Open notepad',
  'Desktop par Work folder banao',
  'System volume up',
];

const APIS = [
  { name: 'Gateway', port: 8080, key: 'gateway', Icon: Radio },
  { name: 'Speech',  port: 8000, key: 'speech',  Icon: Mic },
  { name: 'Brain',   port: 8001, key: 'brain',   Icon: Brain },
  { name: 'Browser', port: 8002, key: 'browser', Icon: Globe },
  { name: 'Desktop', port: 8003, key: 'desktop', Icon: Monitor },
  { name: 'File',    port: 8004, key: 'file',    Icon: Folder },
  { name: 'Ollama',  port: 11434, key: 'ollama', Icon: Cpu },
];

const getApiStatus = (key, statusData) => {
  if (!statusData) return false;
  const apis = statusData.apis || {};
  if (key === 'gateway') return statusData.gateway === 'online';
  if (key === 'ollama') {
    const o = statusData.ollama || '';
    return o === 'connected' || o === 'online';
  }
  const v = apis[`${key}_api`]?.status || apis[key]?.status;
  return v === 'online';
};

/* ========================================================
   SUB-COMPONENTS
   ======================================================== */

/** Animated cyber status dot */
const StatusDot = ({ online }) => (
  <span className="relative flex h-2.5 w-2.5">
    {online && (
      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-70" />
    )}
    <span
      className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
        online
          ? 'bg-emerald-400 shadow-[0_0_8px_#00ff88]'
          : 'bg-rose-500 shadow-[0_0_7px_#ff3366]'
      }`}
    />
  </span>
);

/** Left panel: Subsystem telemetry */
const TelemetryPanel = ({ statusData, isLoading, onRefresh }) => {
  const cards = APIS.map(api => ({
    ...api,
    online: getApiStatus(api.key, statusData),
  }));
  const onlineCount = cards.filter(c => c.online).length;

  return (
    <div className="glass-panel hud-corner rounded-2xl p-4 flex flex-col gap-2.5 h-full">
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-cyan-500/15">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <h3 className="text-[11px] font-bold tracking-widest text-cyan-300 font-orbitron uppercase">
            Subsystem Telemetry
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-cyan-950/40 border border-cyan-500/20 text-cyan-400">
            {onlineCount}/{APIS.length} ACTIVE
          </span>
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-1 rounded text-slate-500 hover:text-cyan-400 transition disabled:opacity-40 cursor-pointer"
            title="Refresh"
          >
            <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Cards */}
      <div className="flex flex-col gap-1.5 flex-1 overflow-y-auto scrollbar-none">
        {cards.map((item, idx) => (
          <motion.div
            key={item.name}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.045 }}
            className={`flex items-center justify-between px-2.5 py-2 rounded-lg border transition-all ${
              item.online
                ? 'bg-slate-950/50 border-cyan-500/18 hover:border-cyan-400/40'
                : 'bg-rose-950/10 border-rose-500/18 hover:border-rose-500/30'
            }`}
          >
            <div className="flex items-center gap-2 min-w-0">
              <div className={`p-1.5 rounded-md shrink-0 ${
                item.online
                  ? 'bg-cyan-950/60 text-cyan-400 border border-cyan-500/25 shadow-[0_0_8px_rgba(0,212,255,0.18)]'
                  : 'bg-rose-950/40 text-rose-400/70 border border-rose-500/20'
              }`}>
                <item.Icon className="w-3.5 h-3.5" />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-[11px] font-semibold text-slate-100 tracking-wide font-orbitron">
                  {item.name}
                </span>
                <span className="text-[9px] text-slate-500 font-mono-code">
                  PORT: {item.port}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1.5 shrink-0 pl-2">
              <StatusDot online={item.online} />
              <span className={`text-[9px] font-bold font-mono-code uppercase tracking-wider ${
                item.online ? 'text-emerald-400' : 'text-rose-400'
              }`}>
                {item.online ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

/** Central orb */
const VoiceOrb = ({ state, onClick }) => {
  const cfgs = {
    idle: {
      grad: 'radial-gradient(circle, rgba(0,212,255,0.7) 0%, rgba(14,116,144,0.25) 45%, transparent 80%)',
      glow: '0 0 40px rgba(0,212,255,0.45), inset 0 0 30px rgba(0,212,255,0.55)',
      ring: 'border-cyan-500/30',
      label: 'SYSTEM READY',
      sub: 'Click orb or press Space to voice command',
      badge: 'text-cyan-400 border-cyan-500/30 bg-cyan-950/20',
      icon: <Mic className="w-9 h-9 text-cyan-200" />,
    },
    listening: {
      grad: 'radial-gradient(circle, rgba(0,212,255,0.95) 0%, rgba(6,182,212,0.5) 50%, transparent 80%)',
      glow: '0 0 70px rgba(0,212,255,0.8), inset 0 0 40px rgba(0,212,255,0.85)',
      ring: 'border-cyan-400/80',
      label: 'LISTENING...',
      sub: 'Speak clearly into your microphone',
      badge: 'text-cyan-200 border-cyan-400 bg-cyan-900/40 animate-pulse',
      icon: <Mic className="w-10 h-10 text-white animate-bounce" />,
    },
    processing: {
      grad: 'radial-gradient(circle, rgba(124,58,237,0.9) 0%, rgba(91,33,182,0.45) 50%, transparent 80%)',
      glow: '0 0 60px rgba(124,58,237,0.7), inset 0 0 35px rgba(124,58,237,0.75)',
      ring: 'border-purple-500/60',
      label: 'NEURAL PROCESSING...',
      sub: 'Brain API synthesizing execution plan',
      badge: 'text-purple-300 border-purple-500 bg-purple-950/40',
      icon: <Cpu className="w-9 h-9 text-purple-200 animate-spin" />,
    },
    success: {
      grad: 'radial-gradient(circle, rgba(0,255,136,0.9) 0%, rgba(5,150,105,0.45) 50%, transparent 80%)',
      glow: '0 0 65px rgba(0,255,136,0.75), inset 0 0 38px rgba(0,255,136,0.8)',
      ring: 'border-emerald-400',
      label: 'COMMAND EXECUTED',
      sub: 'Subsystem execution complete',
      badge: 'text-emerald-200 border-emerald-400 bg-emerald-950/40',
      icon: <CheckCircle2 className="w-10 h-10 text-emerald-200" />,
    },
    error: {
      grad: 'radial-gradient(circle, rgba(255,51,102,0.88) 0%, rgba(190,18,60,0.42) 50%, transparent 80%)',
      glow: '0 0 65px rgba(255,51,102,0.72), inset 0 0 38px rgba(255,51,102,0.75)',
      ring: 'border-rose-500',
      label: 'EXECUTION FAILED',
      sub: 'Review error details in telemetry feed',
      badge: 'text-rose-300 border-rose-500 bg-rose-950/40',
      icon: <AlertTriangle className="w-10 h-10 text-rose-200" />,
    },
  };
  const c = cfgs[state] || cfgs.idle;

  return (
    <div className="relative flex flex-col items-center justify-center select-none">
      <div className="relative w-64 h-64 flex items-center justify-center">
        {/* Outer dashed ring */}
        <motion.div
          className={`absolute inset-0 rounded-full border border-dashed ${c.ring} opacity-60`}
          animate={{ rotate: state === 'processing' ? -360 : -180 }}
          transition={{ duration: state === 'processing' ? 3.5 : 22, repeat: Infinity, ease: 'linear' }}
        />
        {/* Mid tick ring */}
        <motion.div
          className="absolute inset-4 rounded-full border border-slate-700/35"
          animate={{ rotate: 360 }}
          transition={{ duration: 28, repeat: Infinity, ease: 'linear' }}
        >
          <div className="absolute -top-0.5 left-1/2 -translate-x-1/2 w-3 h-0.5 bg-cyan-400 rounded-full shadow-[0_0_8px_#00d4ff]" />
          <div className="absolute -bottom-0.5 left-1/2 -translate-x-1/2 w-3 h-0.5 bg-cyan-400 rounded-full shadow-[0_0_8px_#00d4ff]" />
          <div className="absolute top-1/2 -right-0.5 -translate-y-1/2 h-3 w-0.5 bg-purple-500 rounded-full shadow-[0_0_8px_#7c3aed]" />
        </motion.div>

        {/* Listening ripple */}
        <AnimatePresence>
          {(state === 'listening' || state === 'success') && (
            <motion.div
              className="absolute inset-0 rounded-full border border-cyan-400/40"
              initial={{ scale: 0.88, opacity: 0.8 }}
              animate={{ scale: 1.45, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: 'easeOut' }}
            />
          )}
        </AnimatePresence>

        {/* Main Orb Button */}
        <motion.button
          onClick={onClick}
          className="relative z-10 w-44 h-44 rounded-full cursor-pointer flex items-center justify-center focus:outline-none active:scale-95"
          animate={
            state === 'listening'
              ? { scale: [1, 1.1, 1], boxShadow: ['0 0 30px #00d4ff80', '0 0 75px #00d4ff', '0 0 30px #00d4ff80'] }
              : state === 'processing'
              ? { scale: [1, 1.04, 1], boxShadow: ['0 0 28px #7c3aed80', '0 0 60px #7c3aed', '0 0 28px #7c3aed80'] }
              : state === 'error'
              ? { scale: [1, 1.07, 0.98, 1], boxShadow: ['0 0 20px #ff336680', '0 0 55px #ff3366', '0 0 20px #ff336680'] }
              : { scale: [1, 1.04, 1], boxShadow: ['0 0 28px rgba(0,212,255,0.4)', '0 0 50px rgba(0,212,255,0.65)', '0 0 28px rgba(0,212,255,0.4)'] }
          }
          transition={{
            duration: state === 'listening' ? 0.7 : state === 'processing' ? 2 : 3.2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          style={{ background: c.grad, boxShadow: c.glow }}
        >
          {/* Core aperture */}
          <div className="w-28 h-28 rounded-full bg-black/65 backdrop-blur-md border border-white/15 flex items-center justify-center shadow-inner relative overflow-hidden">
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/12 to-transparent -skew-x-12"
              animate={{ x: ['-150%', '150%'] }}
              transition={{ duration: 2.8, repeat: Infinity, ease: 'easeInOut' }}
            />
            <div className="relative z-10">{c.icon}</div>
          </div>
        </motion.button>
      </div>

      {/* HUD Badge */}
      <div className="mt-4 flex flex-col items-center gap-1.5 text-center">
        <div className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase border ${c.badge} flex items-center gap-1.5 font-mono-code`}>
          <span className="w-1.5 h-1.5 rounded-full bg-current animate-ping" />
          {c.label}
        </div>
        <p className="text-[11px] text-slate-500 font-mono-code">{c.sub}</p>
      </div>
    </div>
  );
};

/** Wave bars */
const WaveBars = ({ active }) => (
  <div className="flex items-end gap-0.5 h-8 justify-center mt-2">
    {Array.from({ length: 18 }).map((_, i) => (
      <motion.div
        key={i}
        className={`w-0.5 rounded-full ${active ? 'bg-cyan-400' : 'bg-slate-700'}`}
        animate={
          active
            ? { height: [`${8 + Math.random() * 22}px`, `${4 + Math.random() * 28}px`, `${6 + Math.random() * 18}px`] }
            : { height: '3px' }
        }
        transition={{ duration: active ? 0.35 + Math.random() * 0.25 : 0.4, repeat: Infinity, ease: 'easeInOut', delay: i * 0.04 }}
      />
    ))}
  </div>
);

/** Response card with typewriter */
const ResponseCard = ({ data, onClose }) => {
  const [typed, setTyped] = useState('');
  const [typing, setTyping] = useState(true);
  const full = data?.response || data?.message || 'Command executed.';
  const ok = data?.status === 'success';

  useEffect(() => {
    setTyped(''); setTyping(true);
    let i = 0;
    const t = setInterval(() => {
      if (i < full.length) { setTyped(full.slice(0, ++i)); }
      else { setTyping(false); clearInterval(t); }
    }, 18);
    const d = setTimeout(() => onClose && onClose(), 7000);
    return () => { clearInterval(t); clearTimeout(d); };
  }, [full]);

  return (
    <motion.div
      initial={{ opacity: 0, y: -16, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -16, scale: 0.96 }}
      transition={{ duration: 0.28 }}
      className={`relative overflow-hidden rounded-xl p-4 border ${
        ok
          ? 'bg-emerald-950/25 border-emerald-500/35 shadow-[0_0_28px_rgba(0,255,136,0.18)]'
          : 'bg-rose-950/25 border-rose-500/35 shadow-[0_0_28px_rgba(255,51,102,0.18)]'
      }`}
    >
      <div className="flex items-center justify-between mb-2.5">
        <div className="flex items-center gap-2">
          <div className={`p-1 rounded ${ok ? 'bg-emerald-950/60 text-emerald-400' : 'bg-rose-950/60 text-rose-400'}`}>
            <Bot className="w-3.5 h-3.5" />
          </div>
          <span className="text-[10px] font-bold font-orbitron tracking-widest text-slate-300 uppercase">
            ARIA Response
          </span>
        </div>
        <div className="flex items-center gap-2">
          {data?.time && (
            <span className="text-[9px] font-mono-code px-2 py-0.5 rounded bg-slate-900/80 border border-slate-700/60 text-slate-400 flex items-center gap-1">
              <Clock className="w-2.5 h-2.5" />{data.time}
            </span>
          )}
          <button onClick={onClose} className="text-slate-500 hover:text-white transition p-0.5 rounded cursor-pointer">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="flex items-start gap-2 text-sm text-slate-100 leading-relaxed font-space-grotesk">
        {ok
          ? <CheckCircle className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
          : <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />}
        <p>{typed}{typing && <span className="inline-block w-1.5 h-4 ml-0.5 bg-cyan-400 animate-pulse align-middle" />}</p>
      </div>

      {(data?.intent || data?.executed_by) && (
        <div className="flex flex-wrap gap-1.5 mt-2.5 text-[10px] font-mono-code">
          {data.intent && (
            <span className="px-2 py-0.5 rounded bg-purple-950/50 border border-purple-500/25 text-purple-300">
              {data.intent}
            </span>
          )}
          {data.executed_by && (
            <span className="px-2 py-0.5 rounded bg-cyan-950/50 border border-cyan-500/25 text-cyan-300">
              {data.executed_by}
            </span>
          )}
          {data.steps_completed !== undefined && (
            <span className="px-2 py-0.5 rounded bg-slate-900/60 border border-slate-700/40 text-slate-400">
              {data.steps_completed} steps
            </span>
          )}
        </div>
      )}

      {/* countdown bar */}
      <motion.div
        className={`absolute bottom-0 left-0 h-0.5 ${ok ? 'bg-emerald-400 shadow-[0_0_6px_#00ff88]' : 'bg-rose-400 shadow-[0_0_6px_#ff3366]'}`}
        initial={{ width: '100%' }}
        animate={{ width: '0%' }}
        transition={{ duration: 7, ease: 'linear' }}
      />
    </motion.div>
  );
};

/** Command history panel */
const HistoryPanel = ({ history, onSelect }) => {
  const items = (history || []).slice(0, 12);
  return (
    <div className="glass-panel hud-corner rounded-2xl p-4 flex flex-col h-full">
      <div className="flex items-center justify-between pb-2.5 border-b border-cyan-500/15 mb-3">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <h3 className="text-[11px] font-bold tracking-widest text-cyan-300 font-orbitron uppercase">
            Command History
          </h3>
        </div>
        <span className="text-[9px] font-mono-code text-slate-500">LOGS ({items.length})</span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-1.5 scrollbar-none">
        <AnimatePresence initial={false}>
          {items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-slate-600 font-mono-code text-xs text-center gap-2">
              <Terminal className="w-8 h-8 opacity-20 text-cyan-500" />
              <span className="text-slate-500">No command telemetry yet.</span>
              <span className="text-[10px] text-slate-600">Speak or type a command to begin.</span>
            </div>
          ) : (
            items.map((item, idx) => {
              const ok = item.status === 'success';
              const time = item.time || (item.timestamp
                ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                : '—');
              return (
                <motion.div
                  key={item.id || item.timestamp || idx}
                  initial={{ opacity: 0, x: 16 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -16 }}
                  transition={{ duration: 0.22 }}
                  onClick={() => onSelect && onSelect(item)}
                  className={`p-2.5 rounded-lg border cursor-pointer group transition-all ${
                    ok
                      ? 'bg-slate-950/50 border-cyan-500/12 hover:border-cyan-400/35 hover:bg-cyan-950/15'
                      : 'bg-rose-950/15 border-rose-500/15 hover:border-rose-400/35 hover:bg-rose-950/25'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <p className="text-[11px] font-medium text-slate-200 line-clamp-2 group-hover:text-cyan-200 transition leading-snug">
                      "{item.command}"
                    </p>
                    {ok
                      ? <CheckCircle className="w-3 h-3 text-emerald-400 shrink-0 mt-0.5" />
                      : <XCircle className="w-3 h-3 text-rose-400 shrink-0 mt-0.5" />}
                  </div>
                  <div className="flex items-center justify-between text-[9px] font-mono-code">
                    <div className="flex items-center gap-1">
                      <span className="px-1.5 py-0.5 rounded bg-cyan-950/60 text-cyan-400 border border-cyan-500/20 uppercase font-semibold">
                        {item.intent || 'CMD'}
                      </span>
                    </div>
                    <div className="flex items-center gap-1 text-slate-600">
                      <Clock className="w-2.5 h-2.5" />
                      <span>{time}</span>
                    </div>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

/* ========================================================
   ROOT APP
   ======================================================== */
export function App() {
  const [orbState, setOrbState]       = useState('idle');
  const [inputText, setInputText]     = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [lastResponse, setLastResponse] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);
  const [history, setHistory]         = useState([]);
  const [isStatusLoading, setIsStatusLoading] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef   = useRef([]);
  const recognitionRef   = useRef(null);
  const transcriptRef    = useRef('');

  const fetchStatus = async () => {
    setIsStatusLoading(true);
    const d = await getSystemStatus();
    setSystemStatus(d);
    setIsStatusLoading(false);
  };

  const fetchHistory = async () => {
    const d = await getHistory(50);
    if (d?.history) setHistory(d.history);
  };

  useEffect(() => {
    fetchStatus();
    fetchHistory();
    const si = setInterval(fetchStatus, 20000); // 20s peaceful polling
    return () => clearInterval(si);
  }, []);

  // Space bar voice toggle
  useEffect(() => {
    const fn = (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        toggleVoice();
      }
    };
    window.addEventListener('keydown', fn);
    return () => window.removeEventListener('keydown', fn);
  }, [isRecording, orbState]);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    const cmd = inputText.trim();
    if (!cmd || orbState === 'processing') return;
    setInputText('');
    setOrbState('processing');
    const result = await sendTextCommand(cmd);
    setLastResponse(result);
    setOrbState(result.status === 'success' ? 'success' : 'error');
    fetchHistory();
    setTimeout(() => setOrbState('idle'), 4500);
  };

  const toggleVoice = async () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (isRecording) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (e) {}
      }
      if (mediaRecorderRef.current?.state !== 'inactive') {
        try { mediaRecorderRef.current?.stop(); } catch (e) {}
      }
      setIsRecording(false);
      setOrbState('processing');
      return;
    }

    // 1. First Priority: Browser Native Web Speech API (Instant real-time transcription)
    if (SpeechRecognition) {
      try {
        const reco = new SpeechRecognition();
        reco.continuous = false;
        reco.interimResults = true;
        reco.lang = 'en-US'; // Also handles Roman Urdu / English mixed terms
        transcriptRef.current = '';

        reco.onstart = () => {
          setIsRecording(true);
          setOrbState('listening');
          setInputText('Listening... bolain...');
        };

        reco.onresult = (event) => {
          const current = Array.from(event.results)
            .map(r => r[0].transcript)
            .join('');
          transcriptRef.current = current;
          setInputText(current);
        };

        reco.onend = async () => {
          setIsRecording(false);
          const finalCmd = transcriptRef.current.trim();
          if (finalCmd) {
            setOrbState('processing');
            const result = await sendTextCommand(finalCmd);
            setLastResponse(result);
            setOrbState(result.status === 'success' ? 'success' : 'error');
            fetchHistory();
            setTimeout(() => setOrbState('idle'), 4500);
          } else {
            setInputText('');
            setOrbState('idle');
          }
        };

        reco.onerror = (e) => {
          console.warn('WebSpeech event error, using MediaRecorder fallback:', e.error);
          setIsRecording(false);
          if (e.error === 'not-allowed') {
            setLastResponse({ command: '[Voice]', intent: 'error', status: 'error', response: 'Microphone permission denied in Chrome. Click lock icon next to URL to allow microphone.', time: '0.0s' });
            setOrbState('error');
            setTimeout(() => setOrbState('idle'), 4000);
          } else {
            startMediaRecorderFallback();
          }
        };

        recognitionRef.current = reco;
        reco.start();
        return;
      } catch (err) {
        console.warn('SpeechRecognition failed to start, falling back to MediaRecorder:', err);
      }
    }

    // 2. Fallback: MediaRecorder stream upload to Gateway
    startMediaRecorderFallback();
  };

  const startMediaRecorderFallback = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];
      const mr = new MediaRecorder(stream);
      mediaRecorderRef.current = mr;
      mr.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
      mr.onstop = async () => {
        stream.getTracks().forEach(t => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setOrbState('processing');
        const result = await sendAudioCommand(blob, 'voice_command.webm');
        setLastResponse(result);
        setOrbState(result.status === 'success' ? 'success' : 'error');
        fetchHistory();
        setTimeout(() => setOrbState('idle'), 4500);
      };
      mr.start();
      setIsRecording(true);
      setOrbState('listening');
    } catch (err) {
      setLastResponse({ command: '[Voice]', intent: 'error', status: 'error', response: `Mic error: ${err.message}. Please allow microphone permissions in Chrome.`, time: '0.0s' });
      setOrbState('error');
      setTimeout(() => setOrbState('idle'), 3500);
    }
  };

  const isGatewayOnline = systemStatus?.gateway === 'online';

  return (
    <div className="relative w-screen h-screen bg-cyber-grid text-slate-100 flex flex-col overflow-hidden select-none">
      {/* Particle BG */}
      <ParticleBackground />

      {/* Scanlines */}
      <div className="fixed inset-0 scanlines pointer-events-none z-10" />

      {/* ═══════════════ HEADER ═══════════════ */}
      <header className="relative z-20 w-full shrink-0 border-b border-cyan-500/15 bg-black/75 backdrop-blur-xl px-5 py-3 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative w-8 h-8 rounded-lg bg-cyan-950/60 border border-cyan-400/40 flex items-center justify-center shadow-[0_0_14px_rgba(0,212,255,0.4)]">
            <Cpu className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_6px_#00d4ff]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-black tracking-widest aria-brand font-orbitron">ARIA</h1>
              <span className="text-[9px] font-mono-code px-1.5 py-0.5 rounded bg-purple-950/60 border border-purple-500/25 text-purple-300">
                v2.0 CORE
              </span>
            </div>
            <p className="text-[9px] text-slate-500 font-mono-code hidden sm:block">
              Advanced Resilient Intelligence Agent
            </p>
          </div>
        </div>

        {/* Center: time */}
        <div className="hidden md:flex items-center gap-1 font-mono-code text-[10px] text-slate-500">
          <Clock className="w-3 h-3" />
          <span>{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        </div>

        {/* Gateway status */}
        <div className="flex items-center gap-2 font-mono-code text-[10px]">
          <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${
            isGatewayOnline
              ? 'border-emerald-500/30 bg-emerald-950/20'
              : 'border-rose-500/25 bg-rose-950/15'
          }`}>
            <StatusDot online={isGatewayOnline} />
            <span className={`font-bold ${isGatewayOnline ? 'text-emerald-400' : 'text-rose-400'}`}>
              GATEWAY :8080 {isGatewayOnline ? 'ONLINE' : 'OFFLINE'}
            </span>
          </div>
        </div>
      </header>

      {/* ═══════════════ MAIN 3-COL GRID ═══════════════ */}
      <main className="relative z-20 flex-1 grid grid-cols-[260px_1fr_260px] gap-4 px-4 py-4 overflow-hidden max-h-full">

        {/* ─── LEFT: Telemetry ─── */}
        <div className="overflow-hidden">
          <TelemetryPanel
            statusData={systemStatus}
            isLoading={isStatusLoading}
            onRefresh={fetchStatus}
          />
        </div>

        {/* ─── CENTER: Orb + Response ─── */}
        <div className="flex flex-col items-center justify-center gap-4 overflow-hidden">
          {/* Response notification */}
          <div className="w-full max-w-lg min-h-[64px] flex items-center">
            <AnimatePresence mode="wait">
              {lastResponse ? (
                <div className="w-full">
                  <ResponseCard data={lastResponse} onClose={() => setLastResponse(null)} />
                </div>
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="w-full text-center font-mono-code text-[10px] text-slate-600"
                >
                  ── AWAITING COMMAND ──
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Central Orb */}
          <VoiceOrb state={orbState} onClick={toggleVoice} />

          {/* Wave bars */}
          <WaveBars active={isRecording} />
        </div>

        {/* ─── RIGHT: History ─── */}
        <div className="overflow-hidden">
          <HistoryPanel
            history={history}
            onSelect={(item) => setInputText(item.command)}
          />
        </div>
      </main>

      {/* ═══════════════ FOOTER: Input Dock ═══════════════ */}
      <footer className="relative z-20 w-full shrink-0 border-t border-cyan-500/15 bg-black/80 backdrop-blur-xl px-5 py-3 flex flex-col items-center gap-2">
        {/* Quick pills */}
        <div className="flex items-center gap-2 overflow-x-auto w-full max-w-3xl scrollbar-none">
          <span className="text-[9px] text-cyan-500 font-mono-code shrink-0">QUICK:</span>
          {QUICK_PROMPTS.map((p, i) => (
            <button key={i} onClick={() => setInputText(p)} className="quick-pill px-2.5 py-1 rounded-full shrink-0 cursor-pointer">
              {p}
            </button>
          ))}
        </div>

        {/* Input row */}
        <form onSubmit={handleSubmit} className="w-full max-w-3xl flex items-center gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={inputText}
              onChange={e => setInputText(e.target.value)}
              placeholder="Ask ARIA anything or state a command..."
              disabled={orbState === 'processing'}
              className="aria-input w-full pl-4 pr-11 py-3 rounded-xl text-sm font-space-grotesk disabled:opacity-50"
            />
            <button
              type="button"
              onClick={toggleVoice}
              title={isRecording ? 'Stop Recording' : 'Voice (Space)'}
              className={`absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-lg transition cursor-pointer ${
                isRecording
                  ? 'bg-rose-500 text-white animate-pulse shadow-[0_0_10px_#ff3366]'
                  : 'text-cyan-400/70 hover:text-cyan-300 hover:bg-cyan-950/50'
              }`}
            >
              <Mic className="w-4 h-4" />
            </button>
          </div>

          <button
            type="submit"
            disabled={!inputText.trim() || orbState === 'processing'}
            className="send-btn px-5 py-3 rounded-xl text-sm flex items-center gap-1.5 shrink-0 cursor-pointer"
          >
            <span>SEND</span>
            <CornerDownLeft className="w-3.5 h-3.5" />
          </button>
        </form>
      </footer>
    </div>
  );
}

export default App;
