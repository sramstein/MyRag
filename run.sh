#!/usr/bin/env bash
# MyRag convenience runner script
set -e

# Detect script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Check if .venv exists
if [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "❌ Error: Python not found. Please install Python 3 or set up .venv."
    exit 1
fi

exec "$PYTHON_BIN" -m src.cli "$@"
