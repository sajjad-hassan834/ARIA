import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

/**
 * WaveAnimation — 24 audio equalizer frequency bars
 * Displays dynamic animated waveforms during listening / processing states
 */
export const WaveAnimation = ({ isActive = false, state = 'idle' }) => {
  const barCount = 24;
  const [barHeights, setBarHeights] = useState(() => Array(barCount).fill(4));

  useEffect(() => {
    let interval;
    if (isActive || state === 'listening' || state === 'processing') {
      interval = setInterval(() => {
        setBarHeights(
          Array.from({ length: barCount }, (_, i) => {
            // Harmonic wave formula with randomness for organic Siri/Assistant effect
            const center = barCount / 2;
            const dist = Math.abs(i - center) / center;
            const factor = Math.cos(dist * (Math.PI / 2));
            const randomMultiplier = state === 'listening' ? Math.random() * 45 + 10 : Math.random() * 25 + 5;
            return Math.max(6, Math.floor(factor * randomMultiplier));
          })
        );
      }, 70);
    } else {
      setBarHeights(Array(barCount).fill(4));
    }

    return () => clearInterval(interval);
  }, [isActive, state]);

  // Color dynamic gradient based on state
  const getBarColor = (index) => {
    if (state === 'error') return 'bg-rose-500 shadow-[0_0_8px_#ff3366]';
    if (state === 'success') return 'bg-emerald-400 shadow-[0_0_8px_#00ff88]';
    if (state === 'processing') return 'bg-purple-500 shadow-[0_0_8px_#7c3aed]';
    if (index % 2 === 0) return 'bg-cyan-400 shadow-[0_0_8px_#00d4ff]';
    return 'bg-blue-500 shadow-[0_0_8px_#3b82f6]';
  };

  return (
    <div className="flex items-center justify-center gap-1 h-16 w-full max-w-md px-4">
      {barHeights.map((height, i) => (
        <motion.div
          key={i}
          className={`w-1 rounded-full transition-all duration-75 ${getBarColor(i)}`}
          animate={{ height: `${height}px` }}
          transition={{ duration: 0.08, ease: 'easeInOut' }}
          style={{ opacity: isActive || state === 'listening' ? 0.9 : 0.25 }}
        />
      ))}
    </div>
  );
};

export default WaveAnimation;
