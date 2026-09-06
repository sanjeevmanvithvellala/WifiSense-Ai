# WiFiSense AI - PowerShell Dev Launcher
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "               Starting WiFiSense AI Platform                        " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Check venv
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment 'venv' not found." -ForegroundColor Red
    Write-Host "Please create it using: python -m venv venv"
    exit 1
}

Write-Host "[1/3] Activating Virtual Environment and running seeder..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
python -m backend.app.services.seed

Write-Host "[2/3] Launching Backend Server on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "[3/3] Launching Frontend UI on port 5173..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "WiFiSense AI is running!" -ForegroundColor Green
Write-Host "- Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "- Backend:  http://localhost:8000/api" -ForegroundColor Green
Write-Host "- Docs:     http://localhost:8000/docs" -ForegroundColor Green
