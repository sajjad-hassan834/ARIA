import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Clock, CheckCircle, XCircle, ArrowRight } from 'lucide-react';

/**
 * CommandLog — Right Side Telemetry Feed
 * Displays the recent commands stream with slide-in animations and status pills.
 */
export const CommandLog = ({ history = [], onSelectCommand }) => {
  const displayedCommands = (history || []).slice(0, 10);

  return (
    <div className="glass-panel hud-corner-tl rounded-xl p-4 sm:p-5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-cyan-500/20 pb-2.5 mb-3">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs sm:text-sm font-bold tracking-wider text-cyan-300 font-orbitron uppercase">
            Command History
          </h3>
        </div>
        <span className="text-[10px] font-mono-code text-slate-500">
          LOGS ({displayedCommands.length})
        </span>
      </div>

      {/* History Stream */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 max-h-[380px]">
        <AnimatePresence initial={false}>
          {displayedCommands.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-48 text-slate-500 font-mono-code text-xs text-center">
              <Terminal className="w-8 h-8 mb-2 opacity-30 text-cyan-400" />
              <span>No command telemetry yet.</span>
              <span className="text-[10px] text-slate-600 mt-1">Speak or type a command to begin.</span>
            </div>
          ) : (
            displayedCommands.map((item, idx) => {
              const isSuccess = item.status === 'success';
              const executedBy = item.executed_by || 'subsystem';
              const timeDisplay = item.time || (item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '0.0s');

              return (
                <motion.div
                  key={item.id || item.timestamp || idx}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.25 }}
                  onClick={() => onSelectCommand && onSelectCommand(item)}
                  className={`p-2.5 rounded-lg border transition-all cursor-pointer group ${
                    isSuccess
                      ? 'bg-slate-950/60 border-cyan-500/15 hover:border-cyan-400/40 hover:bg-cyan-950/20'
                      : 'bg-rose-950/20 border-rose-500/20 hover:border-rose-400/40 hover:bg-rose-950/30'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <p className="text-xs font-medium text-slate-100 line-clamp-2 group-hover:text-cyan-200 transition">
                      "{item.command}"
                    </p>
                    {isSuccess ? (
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                    )}
                  </div>

                  <div className="flex items-center justify-between text-[10px] font-mono-code">
                    <div className="flex items-center gap-1.5">
                      <span className="px-1.5 py-0.5 rounded bg-cyan-950/50 text-cyan-300 border border-cyan-500/30 font-semibold uppercase">
                        {item.intent || 'GENERAL'}
                      </span>
                      <span className="text-slate-500">via</span>
                      <span className="text-slate-400 truncate max-w-[90px]">
                        {executedBy.replace('_api', '')}
                      </span>
                    </div>

                    <div className="flex items-center gap-1 text-slate-500 shrink-0">
                      <Clock className="w-3 h-3" />
                      <span>{timeDisplay}</span>
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

export default CommandLog;
