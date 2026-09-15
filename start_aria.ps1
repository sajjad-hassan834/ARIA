Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  ARIA v2.0 — Advanced Resilient Intelligence" -ForegroundColor Cyan
Write-Host "  Agent System Starting..." -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# 1. Ollama
Write-Host "[1/8] Starting Ollama..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k ollama serve" -WindowStyle Minimized
Start-Sleep -Seconds 3

# 2. Speech API (Port 8000)
Write-Host "[2/8] Starting Speech API (8000)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\SpeechAPI`" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8000 --reload" -WindowStyle Minimized
Start-Sleep -Seconds 2

# 3. Brain API (Port 8001)
Write-Host "[3/8] Starting Brain API (8001)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\BrainAPI`" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8001 --reload" -WindowStyle Minimized
Start-Sleep -Seconds 2

# 4. Browser API (Port 8002)
Write-Host "[4/8] Starting Browser API (8002)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\Browser API`" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8002 --reload" -WindowStyle Minimized
Start-Sleep -Seconds 2

# 5. Desktop API (Port 8003)
Write-Host "[5/8] Starting Desktop API (8003)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\DesktopAPI`" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8003 --reload" -WindowStyle Minimized
Start-Sleep -Seconds 2

# 6. File API (Port 8004)
Write-Host "[6/8] Starting File API (8004)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\File API`" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8004 --reload" -WindowStyle Minimized
Start-Sleep -Seconds 2

# 7. Gateway API (Port 8080)
Write-Host "[7/8] Starting Gateway API (8080)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\GatewayAPI`" && (if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) else (if exist ..\venv\Scripts\activate.bat (call ..\venv\Scripts\activate.bat))) && uvicorn main:app --host 127.0.0.1 --port 8080 --reload" -WindowStyle Minimized
Start-Sleep -Seconds 3

# 8. Frontend UI (Port 3000)
Write-Host "[8/8] Starting ARIA Frontend..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\ARIAFrontend`" && npm run dev"
Start-Sleep -Seconds 2

Write-Host "`n================================================" -ForegroundColor Green
Write-Host "  ALL ARIA SERVICES STARTED!" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend : http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Gateway  : http://localhost:8080" -ForegroundColor Cyan
Write-Host "  Docs     : http://localhost:8080/docs" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Green
