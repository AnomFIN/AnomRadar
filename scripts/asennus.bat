@echo off
REM AnomRadar v2 Windows Installation Wrapper
REM This script launches the Python installer on Windows

echo ============================================================
echo AnomRadar v2 - Windows Installation Wrapper
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python found. Starting installation wizard...
echo.

REM Run the Python installer
python scripts\asennus.py

if errorlevel 1 (
    echo.
    echo Installation failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo To use AnomRadar:
echo   1. Activate virtual environment: .venv\Scripts\activate
echo   2. Run: python -m anomradar.cli scan example.com
echo.
pause
