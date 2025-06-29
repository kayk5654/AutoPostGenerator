@echo off
REM Auto Post Generator - Quick Start
REM Run this to start the application in development mode

setlocal EnableDelayedExpansion
echo.
echo ================================================================
echo  Auto Post Generator - Quick Start
echo ================================================================
echo.

REM Get script directory and set as working directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Colors for output (Windows 11 supports ANSI colors in newer terminals)
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

echo %GREEN%🚀 Starting Auto Post Generator in Development Mode...%NC%
echo.

REM Check if run.bat exists
if not exist "run.bat" (
    echo %RED%❌ run.bat not found%NC%
    echo Please ensure you're in the Auto Post Generator project directory
    echo.
    pause
    exit /b 1
)

REM Run the launcher in development mode
echo %BLUE%📡 Launching application...%NC%
echo %YELLOW%💡 The application will open in your browser automatically%NC%
echo %YELLOW%🛑 Press Ctrl+C in this window to stop the application%NC%
echo.

call run.bat dev

REM Check exit code
if errorlevel 1 (
    echo.
    echo %RED%❌ Application failed to start%NC%
    echo Please check the error messages above
    echo.
    pause
    exit /b 1
)

echo.
echo %GREEN%✅ Application stopped successfully%NC%
pause

endlocal