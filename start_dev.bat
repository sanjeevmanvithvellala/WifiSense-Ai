@echo off
title WiFiSense AI - Local Dev Launcher
echo =====================================================================
echo                Starting WiFiSense AI Platform
echo =====================================================================
echo.

:: Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found.
    echo Please create it using: python -m venv venv
    pause
    exit /b 1
)

echo [1/3] Activating Python Virtual Environment...
call venv\Scripts\activate.bat

echo [2/3] Checking and seeding database...
python -m backend.app.services.seed

echo [3/3] Launching Backend Server on port 8000 and Frontend on port 5173...
echo.
echo - Backend API: http://localhost:8000/api
echo - Swagger Docs: http://localhost:8000/docs
echo - Frontend HUD: http://localhost:5173
echo.

:: Start backend in new command window
start "WiFiSense Backend" cmd /k "venv\Scripts\activate.bat && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

:: Start frontend in new command window
start "WiFiSense Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Services launched successfully in separate terminal windows!
echo Press any key to exit this launcher...
pause >nul
