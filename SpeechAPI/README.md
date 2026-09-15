# Speech Recognition & Voice Interaction REST API (SpeechAPI)

A standalone, high-performance Speech Recognition & Voice Interaction REST API built with **FastAPI**, **OpenAI Whisper**, **RapidFuzz**, and **gTTS**. Designed as a modular backend microservice ready to integrate with web, desktop (Electron / PyQt), mobile, and IoT applications.

---

## 🌟 Key Features

- **NLU Intent Pipeline with Ollama (`phi3:mini`)**: 3-tier hybrid intent understanding:
  1. **Exact Hardcoded Match** (instant return)
  2. **RapidFuzz Match (>75%)** (sub-millisecond typo & word-order tolerance)
  3. **Ollama `phi3:mini` LLM Fallback** (complex dynamic understanding in English, Urdu, and Roman Urdu)
  - **Graceful Fallback**: Automatically falls back to fuzzy matching if Ollama is not running.
- **Speech-to-Text (`/api/speech/transcribe`)**: High-accuracy transcription using OpenAI Whisper (`base` model) with confidence score calculation and language detection.
- **Voice Command Execution (`/api/speech/command`)**: End-to-end pipeline: Audio $\rightarrow$ Whisper STT $\rightarrow$ NLU Intent Extraction $\rightarrow$ Action Dispatch $\rightarrow$ Persistent History.
- **Text-to-Speech (`/api/tts/speak`)**: High-quality speech audio synthesis returning streamed MP3 files.
- **Audit & Command History (`/api/speech/history`)**: Real-time sliding window (last 50 commands) saved atomically in `data/command_history.json`.
- **Real-Time WebSocket Streaming (`/ws/voice-stream`)**: Stream live audio chunks and receive event-driven progress (`transcribing`, `recognized`, `executing`, `done`).
- **Singleton Model Lifecycle**: Whisper model is preloaded **once** on FastAPI server startup and cached in memory for sub-second inference.
- **Production-Ready**: CORS enabled, interactive Swagger documentation (`/docs`), request latency logging middleware, and global exception handlers.


---

## 📁 Project Structure

```
SpeechAPI/
├── main.py                     # Application entry point, lifespan, CORS, middleware, routers
├── config.py                   # Central configuration & parameters
├── requirements.txt            # Project dependencies
├── routes/
│   ├── speech_to_text.py       # POST /api/speech/transcribe
│   ├── text_to_speech.py       # POST /api/tts/speak
│   ├── voice_command.py        # POST /api/speech/command, GET /api/speech/history, POST /api/speech/intent
│   └── websocket_stream.py     # WebSocket /ws/voice-stream
├── services/
│   ├── whisper_service.py      # Cached Whisper singleton, audio decoder, language detector
│   ├── tts_service.py          # gTTS / pyttsx3 speech synthesis engine
│   ├── command_processor.py    # Intent dispatcher & history persistence
│   └── nlu_service.py          # RapidFuzz fuzzy matcher & Roman Urdu engine
├── models/
│   └── schemas.py              # Pydantic data validation schemas
├── data/
│   └── command_history.json    # Persistent command execution history
└── README.md                   # API documentation and curl examples
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or 3.11+
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone or navigate to SpeechAPI directory
cd SpeechAPI

# Install dependencies
pip install -r requirements.txt
```

> **Note on FFmpeg**: `imageio-ffmpeg` is automatically bundled and configured in `services/whisper_service.py`, so audio decoding works seamlessly on Windows, macOS, and Linux without requiring separate system package installation.

### 3. Run the Server

```bash
python main.py
```
Or with Uvicorn CLI directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Once started:
- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **Alternative ReDoc**: `http://localhost:8000/redoc`

---

## 📡 API Endpoints & cURL Examples

### 1. Transcribe Audio (`POST /api/speech/transcribe`)
Upload an audio file (`.wav`, `.mp3`, `.webm`, `.m4a`, `.ogg`) and receive text, confidence, and language.

```bash
curl -X POST "http://localhost:8000/api/speech/transcribe" \
  -F "file=@sample_audio.wav"
```

**Response (200 OK):**
```json
{
  "text": "open browser",
  "confidence": 0.95,
  "language": "en",
  "processing_time": 0.384
}
```

---

### 2. Process Voice Command (`POST /api/speech/command`)
Upload spoken audio, transcribe via Whisper, match intent via NLU, execute action, and record to history.

```bash
curl -X POST "http://localhost:8000/api/speech/command" \
  -F "file=@voice_command.wav"
```

**Response (200 OK):**
```json
{
  "raw_text": "awaz barha",
  "intent": "volume_up",
  "action": "volume_up",
  "response": "Increasing volume",
  "success": true,
  "timestamp": "2026-09-13T12:20:00.000000+00:00"
}
```

---

### 3. Extract Intent from Text (`POST /api/speech/intent`)
Analyze raw text (English or Roman Urdu) to extract intent and match confidence.

```bash
curl -X POST "http://localhost:8000/api/speech/intent" \
  -H "Content-Type: application/json" \
  -d '{"text": "awaz barha"}'
```

**Response (200 OK):**
```json
{
  "input": "awaz barha",
  "intent": "volume_up",
  "confidence": 0.92,
  "language": "roman_urdu"
}
```

#### Supported Roman Urdu / English Sample Commands:
| Input Phrase | Intent | Action | Friendly Response |
| :--- | :--- | :--- | :--- |
| `"kholo"` / `"browser kholo"` | `open_browser` | `open_browser` | Opening browser now |
| `"band karo"` / `"close window"` | `close_app` | `close_window` | Closing the application now |
| `"awaz barha"` / `"volume up"` | `volume_up` | `volume_up` | Increasing volume |
| `"awaz kam karo"` / `"lower volume"` | `volume_down` | `volume_down` | Decreasing volume |
| `"screenshot lo"` / `"take screenshot"` | `screenshot` | `capture_screen` | Taking screenshot now |
| `"time kya hua hai"` / `"what time is it"` | `time_check` | `check_time` | Checking current time |
| `"salam"` / `"hello"` | `greeting` | `greet_user` | Hello! How can I assist you today? |

---

### 4. Text-to-Speech (`POST /api/tts/speak`)
Synthesizes speech audio from text using Google TTS and returns a playable/downloadable MP3 audio stream.

```bash
curl -X POST "http://localhost:8000/api/tts/speak" \
  -H "Content-Type: application/json" \
  -d '{"text": "Opening browser now", "language": "en"}' \
  --output response.mp3
```

---

### 5. Command Execution History (`GET /api/speech/history`)
Retrieve up to the last 50 executed commands with timestamps and metadata.

```bash
curl -X GET "http://localhost:8000/api/speech/history?limit=50"
```

**Response (200 OK):**
```json
{
  "total": 1,
  "history": [
    {
      "raw_text": "awaz barha",
      "intent": "volume_up",
      "action": "volume_up",
      "response": "Increasing volume",
      "success": true,
      "timestamp": "2026-09-13T12:20:00.000000+00:00",
      "confidence": 0.95,
      "language": "roman_urdu"
    }
  ]
}
```

---

### 6. Real-Time WebSocket Voice Stream (`WS /ws/voice-stream`)

Connect over WebSocket to stream live audio chunks and receive events.

#### Connection:
`ws://localhost:8000/ws/voice-stream`

#### Client Payload Options:
- **Binary audio chunks**: Send raw bytes of audio as recorded from microphone.
- **JSON chunks**: `{"action": "chunk", "data": "<base64_audio>"}`
- **Commit**: `{"action": "commit"}` triggers immediate transcription and execution of buffered audio.
- **Reset**: `{"action": "reset"}` clears the current buffer.

#### Server Emitted Events:
1. `connected`: Initial handshake confirmation.
2. `transcribing`: Emitted during buffer accumulation and processing.
3. `recognized`: Emitted when Whisper decodes speech to text.
4. `executing`: Emitted when NLU matches intent and dispatches action.
5. `done`: Emitted with full command result and feedback.

**Example JavaScript Client:**
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/voice-stream");

ws.onopen = () => console.log("Connected to voice stream");

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  switch (msg.event) {
    case "transcribing":
      console.log("Transcribing in progress...", msg.data);
      break;
    case "recognized":
      console.log("Recognized text:", msg.data.text);
      break;
    case "executing":
      console.log("Executing intent:", msg.data.intent);
      break;
    case "done":
      console.log("Finished:", msg.data.response);
      break;
    case "error":
      console.error("Error:", msg.message);
      break;
  }
};
```

---

## ⚙️ Configuration (`config.py`)

All core parameters can be configured in `config.py`:

```python
WHISPER_MODEL = "base"      # "tiny", "base", "small", "medium", "large"
LANGUAGE = "en"             # Default transcription language
FUZZY_THRESHOLD = 75        # RapidFuzz threshold (0-100)
MAX_HISTORY = 50            # Sliding window size for command history
API_HOST = "0.0.0.0"        # Host binding
API_PORT = 8000             # Server port
```
