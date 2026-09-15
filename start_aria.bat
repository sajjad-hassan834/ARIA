@echo off
title ARIA System Launcher
color 0B
echo.
echo  ================================================
echo    ARIA v2.0 — Advanced Resilient Intelligence
echo    Agent System Starting...
echo  ================================================
echo.

cd /d "%~dp0"

:: ── 1. Ollama ──────────────────────────────────────────────────────────────
echo [1/8] Starting Ollama (local LLM fallback)...
start "Ollama Server" /min cmd /k "ollama serve"
timeout /t 3 /nobreak >nul

:: ── 2. Speech API ───────────────────────────────────────────────────────────
echo [2/8] Starting Speech API  on Port 8000...
start "ARIA Speech API :8000" /min cmd /k "cd /d "%~dp0SpeechAPI" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 2 /nobreak >nul

:: ── 3. Brain API ────────────────────────────────────────────────────────────
echo [3/8] Starting Brain API   on Port 8001...
start "ARIA Brain API :8001" /min cmd /k "cd /d "%~dp0BrainAPI" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8001 --reload"
timeout /t 2 /nobreak >nul

:: ── 4. Browser API ──────────────────────────────────────────────────────────
echo [4/8] Starting Browser API on Port 8002...
start "ARIA Browser API :8002" /min cmd /k "cd /d "%~dp0Browser API" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8002 --reload"
timeout /t 2 /nobreak >nul

:: ── 5. Desktop API ──────────────────────────────────────────────────────────
echo [5/8] Starting Desktop API on Port 8003...
start "ARIA Desktop API :8003" /min cmd /k "cd /d "%~dp0DesktopAPI" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8003 --reload"
timeout /t 2 /nobreak >nul

:: ── 6. File API ─────────────────────────────────────────────────────────────
echo [6/8] Starting File API    on Port 8004...
start "ARIA File API :8004" /min cmd /k "cd /d "%~dp0File API" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8004 --reload"
timeout /t 2 /nobreak >nul

:: ── 7. Gateway API ──────────────────────────────────────────────────────────
echo [7/8] Starting Gateway API on Port 8080...
start "ARIA Gateway API :8080" /min cmd /k "cd /d "%~dp0GatewayAPI" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8080 --reload"
timeout /t 4 /nobreak >nul

:: ── 8. React Frontend ───────────────────────────────────────────────────────
echo [8/8] Starting React Frontend...
start "ARIA Frontend :3000" cmd /k "cd /d "%~dp0ARIAFrontend" && npm run dev"
timeout /t 3 /nobreak >nul

:: ── Done ────────────────────────────────────────────────────────────────────
echo.
echo  ================================================
echo   ALL ARIA SERVICES STARTED!
echo.
echo   Frontend  : http://localhost:3000   (React UI)
echo   Gateway   : http://localhost:8080   (Main API)
echo   API Docs  : http://localhost:8080/docs
echo.
echo   Speech API  : http://localhost:8000
echo   Brain API   : http://localhost:8001
echo   Browser API : http://localhost:8002
echo   Desktop API : http://localhost:8003
echo   File API    : http://localhost:8004
echo  ================================================
echo.
echo  TIP: If APIs show OFFLINE in UI, wait 10-15s for them to boot.
echo  Press any key to close this launcher window...
pause >nul
