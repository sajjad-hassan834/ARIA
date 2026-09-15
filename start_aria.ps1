Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  ARIA v2.0 — Advanced Resilient Intelligence" -ForegroundColor Cyan
Write-Host "  Agent System Starting..." -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# 1. Ollama
Write-Host "[1/3] Starting Ollama..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k ollama serve" -WindowStyle Minimized
Start-Sleep -Seconds 2

# 2. Frontend UI (Port 3000)
Write-Host "[2/3] Starting ARIA Frontend (React UI on Port 3000)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\ARIAFrontend`" && npm run dev"
Start-Sleep -Seconds 2

# 3. All Backend Services
Write-Host "[3/3] Starting All ARIA Backend Services (Ports 8000-8080)...`n" -ForegroundColor Yellow
python "$ScriptDir\start_backend.py"
