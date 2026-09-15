# ARIA File API

Microservice for File & Directory Management in the ARIA System, running on **Port 8004**.

---

## Features

- **Standard Locations**: Supports `desktop`, `downloads`, `documents`, `pictures`, `music`, and custom paths.
- **Safety Protection**: Blocks accidental or malicious deletion of Windows system directories (`C:\Windows`, `Program Files`, drive roots, user profile roots, critical system files).
- **Graceful Error Handling**: Handles OS errors (`FileNotFoundError`, `PermissionError`, `FileExistsError`, `OSError`) returning proper HTTP status codes.
- **Audit Logging**: Every file and folder operation is recorded in `data/file_history.json`.
- **CORS Enabled**: Configured with CORS middleware to allow ARIA frontend/brain clients.

---

## Project Structure

```
FileAPI/
├── main.py                  # FastAPI application entry point
├── config.py                # Port (8004), Brain URL, paths & safety configs
├── requirements.txt         # Dependencies
├── routes/
│   ├── __init__.py
│   ├── files.py             # File operations endpoints
│   └── folders.py           # Folder creation endpoints
├── services/
│   ├── __init__.py
│   ├── file_service.py      # Core file logic & path resolution
│   └── history_service.py   # Operation logging to data/file_history.json
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic request & response models
└── data/
    └── file_history.json    # Operation history log
```

---

## Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Run the Server

From the project root:

```powershell
python run.py
```

Or from inside the `FileAPI` folder:

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8004 --reload
```

---

## Endpoints

### 1. Health Check
- **GET** `/health`
- Response:
  ```json
  {
    "status": "ok",
    "service": "ARIA File API",
    "port": 8004,
    "brain_api_url": "http://127.0.0.1:8001"
  }
  ```

### 2. Create File
- **POST** `/api/files/create`
- Request:
  ```json
  {
    "name": "test.txt",
    "location": "desktop",
    "content": "Hello World"
  }
  ```

### 3. Delete File / Path
- **POST** `/api/files/delete`
- Request:
  ```json
  {
    "path": "C:/Users/ALLAH/Desktop/test.txt"
  }
  ```
- *Includes safety check blocking critical OS directories.*

### 4. Move File
- **POST** `/api/files/move`
- Request:
  ```json
  {
    "source": "C:/Users/ALLAH/Downloads/file.pdf",
    "destination": "desktop"
  }
  ```

### 5. Copy File
- **POST** `/api/files/copy`
- Request:
  ```json
  {
    "source": "C:/Users/ALLAH/Documents/report.docx",
    "destination": "desktop"
  }
  ```

### 6. Create Folder
- **POST** `/api/folders/create`
- Request:
  ```json
  {
    "name": "New Folder",
    "location": "desktop"
  }
  ```

### 7. List Files
- **GET** `/api/files/list?location=desktop&extension=pdf`
- (Query parameters: `location` [default: `desktop`], `extension` [optional])

### 8. Open File
- **POST** `/api/files/open`
- Request:
  ```json
  {
    "path": "C:/Users/ALLAH/Desktop/file.txt"
  }
  ```
- *Opens the file with the default registered Windows application.*

### 9. Search Files
- **POST** `/api/files/search`
- Request:
  ```json
  {
    "query": "resume",
    "location": "downloads"
  }
  ```

---

## Running Automated Tests

Run the test script to verify all endpoints and safety guardrails:

```powershell
python test_api.py
```
