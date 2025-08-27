#!/usr/bin/env python
"""
Startup script that ensures proper Gunicorn configuration
Per CLAUDE.md requirements - 300 second timeout for GPT-5 processing
"""
import os
import sys

# CRITICAL: Set timeout for Gunicorn workers
# This must be done before Gunicorn starts
os.environ['GUNICORN_CMD_ARGS'] = '--timeout 300 --graceful-timeout 120 --workers 1 --worker-class sync'

# Import and run the app
from main import app

if __name__ == '__main__':
    # This will be picked up by Gunicorn
    application = app