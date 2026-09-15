@echo off
title ARIA System Launcher
color 0B
echo.
echo  ================================================
echo    ARIA v2.0 -- Advanced Resilient Intelligence
echo    Agent System Starting...
echo  ================================================
echo.

cd /d "%~dp0"

:: 1. Start Ollama in background (minimized)
echo [1/3] Starting Ollama (local LLM fallback)...
start "Ollama Server" /min cmd /k "ollama serve"
timeout /t 2 /nobreak >nul

:: 2. Start Frontend UI in background
echo [2/3] Starting ARIA Frontend (React UI on Port 3000)...
start "ARIA Frontend" cmd /k "cd /d "%~dp0ARIAFrontend" && npm run dev"
timeout /t 2 /nobreak >nul

:: 3. Start All 6 Backend Services in this window with live logs
echo [3/3] Starting All ARIA Backend Services (Ports 8000-8080)...
echo.
python start_backend.py
