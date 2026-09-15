Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  ARIA v2.0 — Advanced Resilient Intelligence" -ForegroundColor Cyan
Write-Host "  Agent System Starting (OpenAI Engine)..." -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

# 1. Frontend UI (Port 3000)
Write-Host "[1/2] Starting ARIA Frontend (React UI on Port 3000)..." -ForegroundColor Yellow
Start-Process "cmd.exe" -ArgumentList "/k cd /d `"$ScriptDir\ARIAFrontend`" && npm run dev"
Start-Sleep -Seconds 2

# 2. All Backend Services
Write-Host "[2/2] Starting All ARIA Backend Services (Ports 8000-8080)...`n" -ForegroundColor Yellow
python "$ScriptDir\start_backend.py"
