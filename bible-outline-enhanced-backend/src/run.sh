#!/bin/bash
# Startup script that applies timeout configuration
cd /opt/render/project/src/bible-outline-enhanced-backend/src

# Check if gunicorn_config.py exists, use it if available
if [ -f "gunicorn_config.py" ]; then
    echo "Using gunicorn_config.py with 300s timeout"
    gunicorn --config gunicorn_config.py main:app
else
    echo "Using default configuration with explicit timeout"
    gunicorn main:app --bind 0.0.0.0:$PORT --timeout 300 --workers 1
fi