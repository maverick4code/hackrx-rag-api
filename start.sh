    #!/usr/bin/env bash
    # This script tells Render to activate the virtual environment and run the app.

    # Exit immediately if a command exits with a non-zero status.
    set -e

    # Activate the virtual environment
    source .venv/bin/activate

    # Run the uvicorn command
    uvicorn main:app --host 0.0.0.0 --port $PORT
    