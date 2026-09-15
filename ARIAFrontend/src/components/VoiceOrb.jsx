import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Cpu, CheckCircle2, AlertTriangle, Sparkles } from 'lucide-react';

/**
 * VoiceOrb — Futuristic Cybernetic Central Intelligence Orb
 * Handles user voice interactions, audio states & holographic animations
 */
export const VoiceOrb = ({ state = 'idle', onClick, isRecording = false }) => {
  // State-specific visual styling & glow properties
  const config = {
    idle: {
      color: '#00d4ff',
      gradient: 'radial-gradient(circle, rgba(0,212,255,0.75) 0%, rgba(14,116,144,0.3) 45%, rgba(0,0,0,0.1) 80%)',
      ringColor: 'border-cyan-500/30',
      glow: '0 0 35px rgba(0, 212, 255, 0.4), inset 0 0 25px rgba(0, 212, 255, 0.5)',
      statusText: 'SYSTEM READY',
      subText: 'Click orb or press Space to voice command',
      badgeClass: 'text-cyan-400 border-cyan-500/30 bg-cyan-950/20',
      icon: <Mic className="w-9 h-9 text-cyan-200" />,
    },
    listening: {
      color: '#00d4ff',
      gradient: 'radial-gradient(circle, rgba(0,212,255,0.9) 0%, rgba(6,182,212,0.45) 50%, rgba(0,0,0,0.2) 80%)',
      ringColor: 'border-cyan-400/80',
      glow: '0 0 65px rgba(0, 212, 255, 0.75), inset 0 0 35px rgba(0, 212, 255, 0.8)',
      statusText: 'LISTENING...',
      subText: 'Speak clearly into your microphone',
      badgeClass: 'text-cyan-300 border-cyan-400 bg-cyan-950/40 animate-pulse',
      icon: <Mic className="w-10 h-10 text-cyan-100 animate-bounce" />,
    },
    processing: {
      color: '#7c3aed',
      gradient: 'radial-gradient(circle, rgba(124,58,237,0.85) 0%, rgba(91,33,182,0.4) 50%, rgba(0,0,0,0.2) 80%)',
      ringColor: 'border-purple-500/60',
      glow: '0 0 55px rgba(124, 58, 237, 0.65), inset 0 0 30px rgba(124, 58, 237, 0.7)',
      statusText: 'NEURAL PROCESSING...',
      subText: 'Brain API synthesizing execution plan',
      badgeClass: 'text-purple-300 border-purple-500 bg-purple-950/40',
      icon: <Cpu className="w-9 h-9 text-purple-200 animate-spin" />,
    },
    success: {
      color: '#00ff88',
      gradient: 'radial-gradient(circle, rgba(0,255,136,0.9) 0%, rgba(5,150,105,0.4) 50%, rgba(0,0,0,0.2) 80%)',
      ringColor: 'border-emerald-400',
      glow: '0 0 60px rgba(0, 255, 136, 0.7), inset 0 0 35px rgba(0, 255, 136, 0.8)',
      statusText: 'COMMAND EXECUTED',
      subText: 'Subsystem execution complete',
      badgeClass: 'text-emerald-300 border-emerald-400 bg-emerald-950/40',
      icon: <CheckCircle2 className="w-10 h-10 text-emerald-200" />,
    },
    error: {
      color: '#ff3366',
      gradient: 'radial-gradient(circle, rgba(255,51,102,0.85) 0%, rgba(190,18,60,0.4) 50%, rgba(0,0,0,0.2) 80%)',
      ringColor: 'border-rose-500',
      glow: '0 0 60px rgba(255, 51, 102, 0.7), inset 0 0 35px rgba(255, 51, 102, 0.7)',
      statusText: 'EXECUTION FAILED',
      subText: 'Review error details in telemetry feed',
      badgeClass: 'text-rose-300 border-rose-500 bg-rose-950/40',
      icon: <AlertTriangle className="w-10 h-10 text-rose-200" />,
    },
  };

  const current = config[state] || config.idle;

  return (
    <div className="relative flex flex-col items-center justify-center select-none py-6">
      {/* Outer Holographic Energy Field */}
      <div className="relative w-64 h-64 sm:w-72 sm:h-72 flex items-center justify-center">
        {/* Outer Ring 1 - Fast dashed counter-rotation */}
        <motion.div
          className={`absolute inset-0 rounded-full border border-dashed ${current.ringColor}`}
          animate={{ rotate: state === 'processing' ? -360 : -180 }}
          transition={{ duration: state === 'processing' ? 4 : 20, repeat: Infinity, ease: 'linear' }}
        />

        {/* Outer Ring 2 - Segmented HUD ring */}
        <motion.div
          className="absolute inset-4 rounded-full border border-slate-700/40"
          animate={{ rotate: 360 }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
        >
          <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-1 bg-cyan-400 rounded-full shadow-[0_0_8px_#00d4ff]" />
          <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-3 h-1 bg-cyan-400 rounded-full shadow-[0_0_8px_#00d4ff]" />
        </motion.div>

        {/* Dynamic Ripple Shockwave on Success or Listening */}
        <AnimatePresence>
          {(state === 'listening' || state === 'success') && (
            <motion.div
              className="absolute inset-0 rounded-full border border-cyan-400/50"
              initial={{ scale: 0.9, opacity: 0.8 }}
              animate={{ scale: 1.4, opacity: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 1.4, repeat: Infinity, ease: 'easeOut' }}
            />
          )}
        </AnimatePresence>

        {/* Interactive Center Orb Button */}
        <motion.button
          onClick={onClick}
          className="relative z-10 w-44 h-44 sm:w-52 sm:h-52 rounded-full cursor-pointer flex flex-col items-center justify-center focus:outline-none transition-transform active:scale-95"
          animate={
            state === 'listening'
              ? { scale: [1, 1.12, 1], boxShadow: ['0 0 30px #00d4ff', '0 0 75px #00d4ff', '0 0 30px #00d4ff'] }
              : state === 'processing'
              ? { scale: [1, 1.04, 1], rotate: [0, 180, 360], boxShadow: ['0 0 30px #7c3aed', '0 0 65px #7c3aed', '0 0 30px #7c3aed'] }
              : state === 'error'
              ? { scale: [1, 1.08, 0.98, 1], boxShadow: ['0 0 20px #ff3366', '0 0 55px #ff3366', '0 0 20px #ff3366'] }
              : { scale: [1, 1.05, 1], boxShadow: ['0 0 25px rgba(0,212,255,0.4)', '0 0 45px rgba(0,212,255,0.6)', '0 0 25px rgba(0,212,255,0.4)'] }
          }
          transition={{
            duration: state === 'listening' ? 0.7 : state === 'processing' ? 2 : 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          style={{
            background: current.gradient,
            boxShadow: current.glow,
          }}
        >
          {/* Cyber Core Aperture */}
          <div className="w-28 h-28 sm:w-32 sm:h-32 rounded-full bg-black/60 backdrop-blur-md border border-white/20 flex items-center justify-center shadow-inner relative overflow-hidden">
            {/* Scan Sweep Reflection */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/15 to-transparent -skew-x-12"
              animate={{ x: ['-150%', '150%'] }}
              transition={{ duration: 2.5, repeat: Infinity, ease: 'easeInOut' }}
            />
            <div className="relative z-10">{current.icon}</div>
          </div>
        </motion.button>
      </div>

      {/* State Status HUD Badge */}
      <div className="mt-4 flex flex-col items-center gap-1 text-center">
        <div className={`px-3 py-1 rounded-full text-xs font-bold tracking-widest uppercase border ${current.badgeClass} flex items-center gap-1.5`}>
          <span className="w-1.5 h-1.5 rounded-full bg-current animate-ping" />
          {current.statusText}
        </div>
        <p className="text-xs text-slate-400 font-mono-code">{current.subText}</p>
      </div>
    </div>
  );
};

export default VoiceOrb;
