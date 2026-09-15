# ARIA Desktop API

Desktop API for the ARIA system, running on **Port 8003**.

## Features
- **Application Controls**: Open and close desktop applications (Notepad, Calculator, Paint, Explorer, Chrome, VS Code, Word, Excel, Task Manager, CMD, PowerShell).
- **System Automation**: Control volume (up/down/mute), capture screenshots with timestamping, and system power management (shutdown, restart, sleep, lock).
- **Safety Safeguards**: Destructive actions (`shutdown`, `restart`) require explicit `"confirm": true` parameter.
- **Screen Automation**: Type text at variable speeds, mouse clicks at (x, y) coordinates with button selection (left, right, middle, double), and mouse scrolling.
- **Brain API Plan Execution**: Batch orchestrator executing multi-step action plans sent by the ARIA Brain API.
- **Audit Logging**: Every action and status is atomically recorded to `data/action_history.json`.

---

## Getting Started

### 1. Requirements
Ensure Python 3.10+ is installed.

```bash
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 2. Running the Server
```bash
.\.venv\Scripts\python main.py
```
Or with uvicorn directly:
```bash
.\.venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8003
```

API Documentation will be available at:
- Swagger UI: `http://localhost:8003/docs`
- ReDoc: `http://localhost:8003/redoc`

---

## API Endpoints

### Health Check
- `GET /health`

### Application Management
- `POST /api/desktop/app/open`
  ```json
  {"app": "notepad"}
  ```
- `POST /api/desktop/app/close`
  ```json
  {"app": "notepad"}
  ```

### System Controls
- `POST /api/desktop/system/volume`
  ```json
  {"action": "up", "level": 5}
  ```
- `POST /api/desktop/system/screenshot`
  ```json
  {"save_to": "desktop"}
  ```
- `POST /api/desktop/system/power`
  ```json
  {"action": "shutdown", "confirm": true}
  ```

### Screen Automation
- `POST /api/desktop/screen/type`
  ```json
  {"text": "Hello World", "speed": "normal"}
  ```
- `POST /api/desktop/screen/click`
  ```json
  {"x": 500, "y": 300, "button": "left"}
  ```
- `POST /api/desktop/screen/scroll`
  ```json
  {"direction": "down", "amount": 3}
  ```

### Plan Execution (Brain API Integration)
- `POST /api/desktop/execute-plan`
  ```json
  {
    "steps": [
      {"action": "app_open", "params": {"app": "notepad"}},
      {"action": "wait", "params": {"seconds": 1.0}},
      {"action": "type", "params": {"text": "Hello from ARIA!", "speed": "normal"}},
      {"action": "screenshot", "params": {"save_to": "desktop"}}
    ]
  }
  ```

---

## Testing
Run the test suite:
```bash
.\.venv\Scripts\pytest -v test_desktop_api.py
```
