#!/bin/bash
# Unix shell script for Auto Post Generator Launcher
# This script provides easy execution of the Universal Python Launcher on Unix systems

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Get script directory and change to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is available
if ! command -v python3 >/dev/null 2>&1; then
    if ! command -v python >/dev/null 2>&1; then
        print_error "Python is not installed or not in PATH"
        echo "Please install Python 3.8+ and ensure it's in your PATH"
        echo "On Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "On macOS: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
MAJOR_VERSION=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR_VERSION=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR_VERSION" -lt 3 ] || ([ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -lt 8 ]); then
    print_error "Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

# Check and activate virtual environment
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    print_status "Activating virtual environment..."
    source "venv/bin/activate"
elif [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
    print_status "Activating virtual environment..."
    source ".venv/bin/activate"
else
    print_warning "No virtual environment found. Using system Python."
    echo "Consider creating a virtual environment with: python3 -m venv venv"
fi

# Check if run.py exists
if [ ! -f "run.py" ]; then
    print_error "run.py not found in current directory"
    echo "Please ensure you're in the Auto Post Generator project directory"
    exit 1
fi

# Make run.py executable if it isn't already
if [ ! -x "run.py" ]; then
    chmod +x "run.py"
fi

# Default to development mode if no arguments provided
if [ $# -eq 0 ]; then
    echo "🚀 Starting Auto Post Generator in Development Mode"
    echo "Use 'run.sh production' for production mode"
    echo "Use 'run.sh docker' for Docker mode"
    echo ""
    $PYTHON_CMD run.py dev
else
    # Pass all arguments to Python script
    $PYTHON_CMD run.py "$@"
fi

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    print_error "Auto Post Generator exited with error code $EXIT_CODE"
    echo ""
    echo "Common solutions:"
    echo "- Check if all dependencies are installed: pip install -r requirements.txt"
    echo "- Ensure port 8501 is not in use by another application"
    echo "- Check the logs above for specific error messages"
    echo ""
    exit $EXIT_CODE
else
    echo ""
    print_status "Auto Post Generator stopped normally"
fi