# ARIA Gateway API (Port 8080)

The **Master Controller** and central orchestration layer for the ARIA multimodal assistant system. The Gateway API acts as the single unified entrypoint for both text and voice commands, routing requests dynamically across all satellite microservices.

---

## Architecture Overview

```
                        User Request (Text or Audio)
                                     │
                                     ▼
                        ┌────────────────────────┐
                        │   Gateway API (8080)   │
                        └────────────┬───────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           │                         │                         │
           ▼                         ▼                         │
   Speech API (8000)          Brain API (8001)                 │
   (Transcribe Audio)       (NLU + Plan Creation)              │
                                     │                         │
                     ┌───────────────┴───────────────┐         │
                     │                               │         │
                     ▼                               ▼         ▼
             Browser API (8002)              Desktop API (8003) File API (8004)
          (Playwright Automation)            (System Controls) (File/Folder Ops)
```

---

## Project Structure

```
GatewayAPI/
├── main.py                     # FastAPI application & startup lifecycle probe
├── config.py                   # Port 8080 & subsystem URLs configuration
├── requirements.txt            # Dependencies
├── test_gateway.py             # Comprehensive test suite
├── routes/
│   ├── __init__.py
│   └── gateway.py              # Text/Audio command, status & history endpoints
├── services/
│   ├── __init__.py
│   └── orchestrator.py         # Subsystem planning, routing & retry engine
├── models/
│   ├── __init__.py
│   └── schemas.py              # Pydantic request & response models
└── data/
    └── gateway_history.json    # Persistent JSON history (latest 50 commands)
```

---

## Features

- **Single Point of Interaction**: Clients only need to communicate with Port 8080.
- **Multimodal Inputs**: Accepts direct text commands or audio voice recordings (`WAV`, `MP3`, `WebM`, `M4A`, `OGG`).
- **Resilience & Retry Logic**: Automatically retries failed requests to downstream APIs once on network or 5xx failures.
- **Graceful Offline Fallbacks**: Detects offline microservices and returns meaningful diagnostics without crashing.
- **History Storage**: Automatically records the last 50 executed commands to `data/gateway_history.json`.
- **System Health Monitoring**: Real-time parallel health check across all 5 satellite APIs and local Ollama instance.
- **CORS & OpenAPI Documentation**: Full Swagger UI docs at `/docs` and `/redoc`.

---

## Subsystem Port Mapping

| Subsystem API | Port | Role |
| :--- | :--- | :--- |
| **Gateway API** | `8080` | Master controller & external client entrypoint |
| **Speech API** | `8000` | Voice transcription (Faster-Whisper) & TTS |
| **Brain API** | `8001` | Intent classification & multi-step plan generation |
| **Browser API** | `8002` | Playwright web automation & media playback |
| **Desktop API** | `8003` | OS automation (apps, screenshots, volume, input) |
| **File API** | `8004` | File & directory management |
| **Ollama LLM** | `11434` | Local LLM intelligence engine |

---

## Endpoints

### 1. Execute Text Command
- **Endpoint**: `POST /api/gateway/command/text`
- **Request Body**:
```json
{
  "command": "YouTube par Arijit Singh ke gaane chalao",
  "language": "auto"
}
```
- **Response**:
```json
{
  "command": "YouTube par Arijit Singh ke gaane chalao",
  "intent": "play_music",
  "executed_by": "browser_api",
  "status": "success",
  "steps_completed": 4,
  "response": "Playing Arijit Singh on YouTube!",
  "time": "3.2s"
}
```

### 2. Execute Audio Command
- **Endpoint**: `POST /api/gateway/command/audio`
- **Content-Type**: `multipart/form-data`
- **Form Field**: `file: <audio_file>`
- **Workflow**: Transcribes voice using Speech API (8000), plans execution with Brain API (8001), and dispatches to the corresponding subsystem.

### 3. Check System Status
- **Endpoint**: `GET /api/gateway/status`
- **Response**:
```json
{
  "gateway": "online",
  "apis": {
    "speech_api": {"status": "online", "port": 8000, "url": "http://127.0.0.1:8000"},
    "brain_api": {"status": "online", "port": 8001, "url": "http://127.0.0.1:8001"},
    "browser_api": {"status": "online", "port": 8002, "url": "http://127.0.0.1:8002"},
    "desktop_api": {"status": "online", "port": 8003, "url": "http://127.0.0.1:8003"},
    "file_api": {"status": "online", "port": 8004, "url": "http://127.0.0.1:8004"}
  },
  "ollama": "connected"
}
```

### 4. Command Execution History
- **Endpoint**: `GET /api/gateway/history?limit=50`
- **Response**:
```json
{
  "total": 1,
  "history": [
    {
      "command": "YouTube par Arijit Singh ke gaane chalao",
      "intent": "play_music",
      "executed_by": "browser_api",
      "status": "success",
      "steps_completed": 4,
      "response": "Playing Arijit Singh on YouTube!",
      "time": "3.2s",
      "timestamp": "2026-09-13T20:50:00.000000"
    }
  ]
}
```

### 5. Health Check
- **Endpoint**: `GET /health`
- **Response**:
```json
{
  "status": "healthy",
  "gateway": "online",
  "port": 8080,
  "apis": {
    "speech_api": "online",
    "brain_api": "online",
    "browser_api": "online",
    "desktop_api": "online",
    "file_api": "online"
  }
}
```

---

## Running the Gateway API

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start Server
```bash
python main.py
```
*The server will run on `http://0.0.0.0:8080`.*
Open interactive Swagger documentation at `http://127.0.0.1:8080/docs`.

### Run Test Suite
```bash
python -m pytest test_gateway.py -v
```
