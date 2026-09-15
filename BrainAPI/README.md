# ARIA Brain API 🧠

Intelligence and Planning layer for the ARIA Assistant System.

## Features
- **Rule-based & LLM Planner**: Understands English & Hinglish commands, breaks requests into discrete action steps.
- **Intent Classifier**: Maps utterances to target APIs (`browser_api`, `desktop_api`, `file_api`) and port mappings.
- **Context & Memory**: Keeps last 10 conversation commands and executes repeat commands (*"wahi karo phir"*, *"again"*).
- **Task History**: Stores last 20 planned tasks.
- **System Health Probes**: Real-time status checks for Brain API, Speech API, Browser API, Desktop API, File API, and Ollama.
- **FastAPI + Swagger Docs**: Interactive API documentation at `/docs`.

## Port & Target Endpoints
- **Brain API Port**: `8001`
- **Swagger Documentation**: `http://localhost:8001/docs`

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | System health & connected microservices |
| `/api/brain/plan` | POST | Plan steps from user utterance |
| `/api/brain/classify` | POST | Classify user utterance to target API |
| `/api/brain/context` | POST/GET | Manage / fetch conversation context |
| `/api/brain/history` | GET | Retrieve last 20 planned tasks |

## Quick Start

```bash
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Running Tests
```bash
python tests/test_brain_api.py
```
