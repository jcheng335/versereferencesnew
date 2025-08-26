import os

# Gunicorn configuration file
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 1
timeout = 600  # 10 minutes timeout for GPT-5 processing
graceful_timeout = 610
keepalive = 5
worker_class = "sync"
loglevel = "debug"
accesslog = "-"
errorlog = "-"
capture_output = True
enable_stdio_inheritance = True