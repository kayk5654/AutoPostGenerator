@echo off
REM Windows batch script for Auto Post Generator Launcher
REM This script provides easy execution of the Universal Python Launcher on Windows

setlocal EnableDelayedExpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and ensure it's in your PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call "venv\Scripts\activate.bat"
) else if exist ".venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call ".venv\Scripts\activate.bat"
) else (
    echo ⚠️  No virtual environment found. Using system Python.
    echo Consider creating a virtual environment with: python -m venv venv
)

REM Check if run.py exists
if not exist "run.py" (
    echo ❌ run.py not found in current directory
    echo Please ensure you're in the Auto Post Generator project directory
    pause
    exit /b 1
)

REM Default to development mode if no arguments provided
if "%~1"=="" (
    echo 🚀 Starting Auto Post Generator in Development Mode
    echo Use 'run.bat production' for production mode
    echo Use 'run.bat docker' for Docker mode
    echo.
    python run.py dev
) else (
    REM Pass all arguments to Python script
    python run.py %*
)

REM Check exit code
if errorlevel 1 (
    echo.
    echo ❌ Auto Post Generator exited with error code %errorlevel%
    echo.
    echo Common solutions:
    echo - Check if all dependencies are installed: pip install -r requirements.txt
    echo - Ensure port 8501 is not in use by another application
    echo - Check the logs above for specific error messages
    echo.
    pause
    exit /b %errorlevel%
) else (
    echo.
    echo ✅ Auto Post Generator stopped normally
)

endlocal