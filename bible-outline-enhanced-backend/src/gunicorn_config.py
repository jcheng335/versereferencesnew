import os

# Gunicorn configuration for Bible Outline Backend
# CRITICAL: These settings prevent worker timeout during LLM processing
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"
workers = 1
timeout = 300  # 5 minutes - REQUIRED for GPT-5 API calls
graceful_timeout = 120
keepalive = 5
loglevel = "info"
worker_class = "sync"  # Use sync workers for simplicity
max_requests = 100  # Restart workers after 100 requests to prevent memory leaks
max_requests_jitter = 10