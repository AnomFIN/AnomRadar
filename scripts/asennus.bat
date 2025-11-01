@echo off
REM AnomRadar v2 Interactive Installer for Windows
REM asennus.bat

echo ============================================================
echo      AnomRadar v2 Installer (Windows)
echo ============================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [OK] Python is installed
echo.

REM Check pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found. Please install pip and try again.
    pause
    exit /b 1
)

echo [OK] pip is available
echo.

REM Ask for confirmation
echo This installer will:
echo   - Install Python dependencies
echo   - Create configuration files
echo   - Set up AnomRadar v2
echo.
set /p CONFIRM="Continue with installation? (Y/n): "
if /i "%CONFIRM%"=="n" (
    echo Installation cancelled.
    exit /b 0
)

echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Create config files
echo Setting up configuration...

if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo [OK] Created .env from .env.example
    )
) else (
    echo [SKIP] .env already exists
)

if not exist anomradar.toml (
    if exist anomradar.toml.example (
        copy anomradar.toml.example anomradar.toml >nul
        echo [OK] Created anomradar.toml from anomradar.toml.example
    )
) else (
    echo [SKIP] anomradar.toml already exists
)

echo.

REM Create directories
echo Creating directories...
if not exist "%USERPROFILE%\.anomradar" mkdir "%USERPROFILE%\.anomradar"
if not exist "%USERPROFILE%\.anomradar\cache" mkdir "%USERPROFILE%\.anomradar\cache"
if not exist "%USERPROFILE%\.anomradar\data" mkdir "%USERPROFILE%\.anomradar\data"
if not exist "%USERPROFILE%\.anomradar\logs" mkdir "%USERPROFILE%\.anomradar\logs"
echo [OK] Directories created
echo.

REM Install package in development mode
echo Setting up CLI entry point...
python -m pip install -e . >nul 2>&1
if errorlevel 1 (
    echo [WARN] Could not create CLI entry point
    echo       You can still run: python -m anomradar.cli
) else (
    echo [OK] CLI entry point created
)
echo.

REM Run self-check
echo Running self-check...
python -m anomradar.cli self-check
echo.

echo ============================================================
echo      Installation completed successfully!
echo ============================================================
echo.
echo Next steps:
echo.
echo 1. Customize configuration (optional):
echo    - Edit .env for environment variables
echo    - Edit anomradar.toml for advanced settings
echo.
echo 2. Run a test scan:
echo    python -m anomradar.cli scan example.com
echo.
echo 3. Launch the TUI:
echo    python -m anomradar.cli tui
echo.
echo 4. Get help:
echo    python -m anomradar.cli --help
echo.
echo Happy scanning!
echo.
pause
