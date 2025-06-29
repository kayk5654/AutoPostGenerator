@echo off
REM Auto Post Generator - Windows 11 Setup Script
REM This script sets up the virtual environment and dependencies for first-time use

setlocal EnableDelayedExpansion
echo.
echo ================================================================
echo  Auto Post Generator - Windows 11 Setup Script
echo ================================================================
echo.
echo This script will:
echo  1. Check Python installation
echo  2. Create virtual environment
echo  3. Install dependencies
echo  4. Verify setup
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

REM Function to print colored output
REM Note: Using simple echo for wider compatibility

echo Step 1: Checking Python installation...
echo ----------------------------------------

REM Check if Python is installed and accessible
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Python is not installed or not in PATH%NC%
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to:
    echo  - Check "Add Python to PATH" during installation
    echo  - Choose "pip" installation option
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% found

REM Check Python version (basic check for 3.x)
echo %PYTHON_VERSION% | findstr /r "^3\." >nul
if errorlevel 1 (
    echo %RED%❌ Python 3.x required, found %PYTHON_VERSION%%NC%
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM More detailed version check
for /f "tokens=1,2 delims=." %%a in ('echo %PYTHON_VERSION%') do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% LSS 3 (
    echo %RED%❌ Python 3.8+ required, found %PYTHON_VERSION%%NC%
    pause
    exit /b 1
)

if %MAJOR% EQU 3 if %MINOR% LSS 8 (
    echo %RED%❌ Python 3.8+ required, found %PYTHON_VERSION%%NC%
    pause
    exit /b 1
)

echo ✅ Python version is compatible
echo.

echo Step 2: Setting up virtual environment...
echo ------------------------------------------

REM Check if virtual environment already exists
if exist "venv\" (
    echo ⚠️  Virtual environment already exists
    set /p "RECREATE=Recreate virtual environment? This will delete existing venv (y/N): "
    if /i "!RECREATE!"=="y" (
        echo 🗑️  Removing existing virtual environment...
        rmdir /s /q "venv" 2>nul
        if exist "venv\" (
            echo %RED%❌ Failed to remove existing virtual environment%NC%
            echo Please manually delete the 'venv' folder and try again
            pause
            exit /b 1
        )
    ) else (
        echo ℹ️  Using existing virtual environment
        goto :ActivateVenv
    )
)

echo 🔨 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo %RED%❌ Failed to create virtual environment%NC%
    echo.
    echo Common solutions:
    echo  - Ensure you have write permissions in this directory
    echo  - Try running as administrator
    echo  - Check if antivirus is blocking the operation
    echo.
    pause
    exit /b 1
)

echo ✅ Virtual environment created successfully

:ActivateVenv
echo.
echo Step 3: Activating virtual environment...
echo -----------------------------------------

if not exist "venv\Scripts\activate.bat" (
    echo %RED%❌ Virtual environment activation script not found%NC%
    echo The virtual environment may be corrupted
    pause
    exit /b 1
)

echo ✅ Activating virtual environment...
call "venv\Scripts\activate.bat"

echo ✅ Virtual environment activated
echo.

echo Step 4: Upgrading pip...
echo -------------------------

echo 🔄 Upgrading pip to latest version...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo %YELLOW%⚠️  Pip upgrade failed, continuing with existing version%NC%
) else (
    echo ✅ Pip upgraded successfully
)

echo.

echo Step 5: Installing dependencies...
echo ----------------------------------

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo %RED%❌ requirements.txt not found%NC%
    echo Please ensure you're running this script from the Auto Post Generator directory
    pause
    exit /b 1
)

echo 📦 Installing dependencies from requirements.txt...
echo This may take a few minutes...
echo.

python -m pip install -r requirements.txt
if errorlevel 1 (
    echo %RED%❌ Failed to install dependencies%NC%
    echo.
    echo Common solutions:
    echo  - Check your internet connection
    echo  - Try running: python -m pip install --upgrade pip
    echo  - Try running as administrator
    echo  - Check if antivirus is blocking downloads
    echo.
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully
echo.

echo Step 6: Verifying installation...
echo ----------------------------------

echo 🔍 Verifying core dependencies...

REM Check critical dependencies
set "DEPS_OK=1"

echo Checking streamlit...
python -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)" 2>nul
if errorlevel 1 (
    echo %RED%❌ Streamlit not found%NC%
    set "DEPS_OK=0"
)

echo Checking pandas...
python -c "import pandas; print('✅ Pandas:', pandas.__version__)" 2>nul
if errorlevel 1 (
    echo %RED%❌ Pandas not found%NC%
    set "DEPS_OK=0"
)

echo Checking psutil...
python -c "import psutil; print('✅ Psutil:', psutil.__version__)" 2>nul
if errorlevel 1 (
    echo %RED%❌ Psutil not found%NC%
    set "DEPS_OK=0"
)

if %DEPS_OK% EQU 0 (
    echo %RED%❌ Some dependencies are missing%NC%
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Step 7: Testing launcher...
echo ---------------------------

echo 🧪 Testing Universal Python Launcher...

REM Check if run.py exists
if not exist "run.py" (
    echo %RED%❌ run.py not found%NC%
    echo Please ensure you have the Phase 7.1 launcher files
    pause
    exit /b 1
)

REM Test launcher help
python run.py --help >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Launcher test failed%NC%
    echo The launcher may have issues
    pause
    exit /b 1
)

echo ✅ Launcher is working correctly
echo.

echo Step 8: Final verification...
echo ------------------------------

echo 🔍 Running final system check...

REM Check project structure
set "STRUCTURE_OK=1"

if not exist "app.py" (
    echo %YELLOW%⚠️  app.py not found - main application file missing%NC%
    set "STRUCTURE_OK=0"
)

if not exist "config.py" (
    echo %YELLOW%⚠️  config.py not found - configuration file missing%NC%
    set "STRUCTURE_OK=0"
)

if not exist "services\" (
    echo %YELLOW%⚠️  services directory not found%NC%
    set "STRUCTURE_OK=0"
)

if %STRUCTURE_OK% EQU 0 (
    echo %YELLOW%⚠️  Some project files are missing%NC%
    echo The setup completed, but the project structure may be incomplete
    echo.
)

echo.
echo ================================================================
echo  🎉 Setup Complete!
echo ================================================================
echo.
echo ✅ Virtual environment created and activated
echo ✅ Dependencies installed successfully  
echo ✅ Universal Python Launcher is ready
echo.
echo %GREEN%Next steps:%NC%
echo.
echo  1. To start the application in development mode:
echo     run.bat
echo.
echo  2. To start with specific options:
echo     run.bat dev --port 8080
echo     run.bat production
echo.
echo  3. To stop the application:
echo     stop.bat
echo.
echo  4. For help and more options:
echo     python run.py --help
echo.
echo %BLUE%Documentation:%NC%
echo  - See LAUNCHER.md for detailed usage guide
echo  - See README.md for general project information
echo.
echo %YELLOW%Note:%NC% This terminal session has the virtual environment activated.
echo For future sessions, the launcher will auto-activate it for you.
echo.

REM Create a simple usage reminder file
echo REM Auto Post Generator - Quick Start > quick_start.bat
echo REM Run this to start the application in development mode >> quick_start.bat
echo @echo off >> quick_start.bat
echo call run.bat >> quick_start.bat

echo ✅ Created quick_start.bat for easy access
echo.

echo Setup completed successfully! 🚀
echo.
pause

endlocal