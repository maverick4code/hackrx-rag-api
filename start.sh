#!/usr/bin/env bash
# This script runs the uvicorn server.

# Exit immediately if a command exits with a non-zero status.
set -e

# Use the Python interpreter from the virtual environment to run uvicorn
./.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port $PORT
    
    