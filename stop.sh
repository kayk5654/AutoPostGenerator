#!/bin/bash
# Unix shell script for stopping Auto Post Generator
# This script provides easy stopping of Auto Post Generator processes on Unix systems

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
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check and activate virtual environment
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    print_status "Activating virtual environment..."
    source "venv/bin/activate"
elif [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
    print_status "Activating virtual environment..."
    source ".venv/bin/activate"
fi

# Check if stop.py exists
if [ ! -f "stop.py" ]; then
    print_error "stop.py not found in current directory"
    echo "Please ensure you're in the Auto Post Generator project directory"
    exit 1
fi

# Make stop.py executable if it isn't already
if [ ! -x "stop.py" ]; then
    chmod +x "stop.py"
fi

# Run the stop script with all provided arguments
if [ $# -eq 0 ]; then
    echo "🛑 Stopping all Auto Post Generator processes..."
    $PYTHON_CMD stop.py
else
    $PYTHON_CMD stop.py "$@"
fi

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo ""
    print_error "Stop script exited with error code $EXIT_CODE"
    exit $EXIT_CODE
else
    echo ""
    print_status "Stop script completed successfully"
fi