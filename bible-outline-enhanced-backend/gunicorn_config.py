"""
Gunicorn configuration file
Increases timeout to handle LLM processing
"""

import os

# Bind to the port provided by Render
bind = f"0.0.0.0:{os.environ.get('PORT', 5004)}"

# Number of worker processes
workers = 1  # Start with 1 worker for Render starter plan

# Worker class
worker_class = 'sync'

# Timeout - increase to 120 seconds for LLM processing
timeout = 120

# Keep alive
keepalive = 5

# Max requests per worker before restart
max_requests = 100
max_requests_jitter = 10

# Logging
loglevel = 'info'
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log to stderr

# Preload app
preload_app = True

# Enable stdout/stderr logging
capture_output = True
enable_stdio_inheritance = True