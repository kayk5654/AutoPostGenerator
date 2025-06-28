@echo off
REM Windows batch script for stopping Auto Post Generator
REM This script provides easy stopping of Auto Post Generator processes on Windows

setlocal EnableDelayedExpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and ensure it's in your PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call ".venv\Scripts\activate.bat"
)

REM Check if stop.py exists
if not exist "stop.py" (
    echo ❌ stop.py not found in current directory
    echo Please ensure you're in the Auto Post Generator project directory
    pause
    exit /b 1
)

REM Run the stop script with all provided arguments
if "%~1"=="" (
    echo 🛑 Stopping all Auto Post Generator processes...
    python stop.py
) else (
    python stop.py %*
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Stop script exited with error code %errorlevel%
    pause
    exit /b %errorlevel%
) else (
    echo.
    echo ✅ Stop script completed successfully
)

endlocal
timeout /t 2 /nobreak >nul