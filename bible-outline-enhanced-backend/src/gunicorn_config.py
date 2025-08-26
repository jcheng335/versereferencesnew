import os

# Gunicorn configuration
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 1
timeout = 300  # 5 minutes for large files
graceful_timeout = 120
keepalive = 5
loglevel = "info"