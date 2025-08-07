#!/usr/bin/env bash
# This script tells Render to run your app on startup.

# Run the uvicorn command
uvicorn main:app --host 0.0.0.0 --port $PORT