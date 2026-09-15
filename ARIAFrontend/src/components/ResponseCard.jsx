import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, X, CheckCircle, AlertCircle, Clock, Zap } from 'lucide-react';

/**
 * ResponseCard — Floating Holographic HUD Response Card
 * Displays the execution outcome with typewriter text animation and 5s auto-dismiss.
 */
export const ResponseCard = ({ responseData, onClose, autoDismissSeconds = 6 }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  const fullText = responseData?.response || responseData?.message || 'Command executed.';
  const isSuccess = responseData?.status === 'success';

  useEffect(() => {
    setDisplayedText('');
    setIsTyping(true);

    let currentIndex = 0;
    const interval = setInterval(() => {
      if (currentIndex < fullText.length) {
        setDisplayedText(fullText.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        setIsTyping(false);
        clearInterval(interval);
      }
    }, 20);

    // Auto dismiss timer
    const dismissTimer = setTimeout(() => {
      if (onClose) onClose();
    }, autoDismissSeconds * 1000);

    return () => {
      clearInterval(interval);
      clearTimeout(dismissTimer);
    };
  }, [fullText, autoDismissSeconds, onClose]);

  if (!responseData) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -20, scale: 0.95 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`glass-panel hud-corner-tl rounded-xl p-4 sm:p-5 max-w-xl w-full mx-auto relative overflow-hidden border ${
        isSuccess
          ? 'border-emerald-500/40 shadow-[0_0_30px_rgba(0,255,136,0.2)]'
          : 'border-rose-500/40 shadow-[0_0_30px_rgba(255,51,102,0.2)]'
      }`}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-cyan-950/60 text-cyan-400">
            <Bot className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold font-orbitron tracking-wider text-cyan-300 uppercase">
            ARIA Direct Response
          </span>
        </div>

        <div className="flex items-center gap-2">
          {responseData.time && (
            <span className="text-[10px] font-mono-code px-2 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 flex items-center gap-1">
              <Clock className="w-2.5 h-2.5" />
              {responseData.time}
            </span>
          )}
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition p-1 rounded hover:bg-white/5 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Response Body with Typewriter Effect */}
      <div className="space-y-2.5">
        <div className="text-sm sm:text-base text-slate-100 font-medium leading-relaxed font-space-grotesk flex items-start gap-2">
          {isSuccess ? (
            <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          ) : (
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          )}
          <p className="flex-1">
            {displayedText}
            {isTyping && <span className="inline-block w-2 h-4 ml-1 bg-cyan-400 animate-pulse" />}
          </p>
        </div>

        {/* Action Metadata Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] font-mono-code text-slate-400">
          {responseData.intent && (
            <span className="px-2 py-0.5 rounded bg-purple-950/40 border border-purple-500/30 text-purple-300">
              INTENT: {responseData.intent}
            </span>
          )}
          {responseData.executed_by && (
            <span className="px-2 py-0.5 rounded bg-cyan-950/40 border border-cyan-500/30 text-cyan-300">
              SUBSYSTEM: {responseData.executed_by}
            </span>
          )}
          {responseData.steps_completed !== undefined && (
            <span className="px-2 py-0.5 rounded bg-emerald-950/40 border border-emerald-500/30 text-emerald-300">
              STEPS: {responseData.steps_completed}
            </span>
          )}
        </div>
      </div>

      {/* 5-Second Countdown Indicator Bar */}
      <motion.div
        className={`absolute bottom-0 left-0 h-0.5 ${
          isSuccess ? 'bg-emerald-400 shadow-[0_0_8px_#00ff88]' : 'bg-rose-400 shadow-[0_0_8px_#ff3366]'
        }`}
        initial={{ width: '100%' }}
        animate={{ width: '0%' }}
        transition={{ duration: autoDismissSeconds, ease: 'linear' }}
      />
    </motion.div>
  );
};

export default ResponseCard;
