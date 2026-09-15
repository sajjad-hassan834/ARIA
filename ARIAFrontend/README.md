# ARIA Futuristic AI Frontend

A futuristic cybernetic user interface for the **ARIA Multimodal AI Agent System** built with **React**, **Tailwind CSS**, **Framer Motion**, and **Lucide Icons**.

---

## Visual Aesthetics & Design System

- **Background**: Deep Void Black (`#000000`) with dynamic 60fps neural network particles
- **Primary Accent**: Electric Cyan (`#00d4ff`)
- **Secondary Accent**: Cyber Violet (`#7c3aed`)
- **Success Accent**: Emerald Green (`#00ff88`)
- **Error Accent**: Crimson Red (`#ff3366`)
- **Typography**: `Orbitron` (HUD Headers & Titles), `Space Grotesk` (Body & Inputs), `JetBrains Mono` (Telemetry & Ports)
- **Effects**: Glassmorphism cards (`backdrop-blur-md`), neon glowing borders, subtle scanline overlay, and HUD corner brackets.

---

## Core Components

1. **`VoiceOrb.jsx`**:
   - Central glowing cybernetic sphere with multi-layer concentric orbital rings.
   - States:
     - `idle`: Gentle breathing neon pulse.
     - `listening`: Expanding reactive aura with shockwave ripples.
     - `processing`: Rotational spinner with violet energy aura.
     - `success`: Emerald flash with radial completion wave.
     - `error`: Warning red pulse.
   - Interactive: Click orb or press `Space` to start/stop microphone voice recording.
2. **`WaveAnimation.jsx`**:
   - 24-channel reactive equalizer audio waveform visualizer responding dynamically during voice commands.
3. **`StatusGrid.jsx`**:
   - Real-time telemetry monitoring for:
     - **Gateway API** (`Port 8080`)
     - **Speech API** (`Port 8000`)
     - **Brain API** (`Port 8001`)
     - **Browser API** (`Port 8002`)
     - **Desktop API** (`Port 8003`)
     - **File API** (`Port 8004`)
     - **Ollama LLM** (`Port 11434`)
   - Auto-refreshes every 5 seconds with pulsing status dots and skeleton loaders.
4. **`CommandLog.jsx`**:
   - Slide-in real-time command telemetry stream displaying the last 10 commands with intent tags, subsystem indicators, status pills, and execution times.
5. **`ResponseCard.jsx`**:
   - Holographic floating modal presenting ARIA's execution response with typewriter typing effect, execution telemetry, and 6-second auto-dismiss countdown.
6. **`ParticleBackground.jsx`**:
   - Hardware-accelerated 60fps HTML5 Canvas neural network particle graph with distance-based synaptic lines.

---

## Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
Open **`http://localhost:3000`** in your browser.

### 3. Build for Production
```bash
npm run build
```

---

## Gateway API Integration

The frontend connects to the ARIA Master Gateway on `http://127.0.0.1:8080`:
- Text commands $\rightarrow$ `POST /api/gateway/command/text`
- Voice recordings $\rightarrow$ `POST /api/gateway/command/audio`
- Telemetry health $\rightarrow$ `GET /api/gateway/status`
- Command history $\rightarrow$ `GET /api/gateway/history`
