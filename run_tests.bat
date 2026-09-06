@echo off
title WiFiSense AI - Automated Test Runner
echo =====================================================================
echo                Running WiFiSense AI Test Suite
echo =====================================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment 'venv' not found.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python -m pytest tests/ -v

echo.
echo =====================================================================
echo Test execution completed.
echo =====================================================================
pause
