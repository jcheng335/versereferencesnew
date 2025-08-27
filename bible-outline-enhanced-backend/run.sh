#!/bin/bash
# Run script with explicit timeout settings per CLAUDE.md requirements
cd /opt/render/project/src/bible-outline-enhanced-backend/src
exec gunicorn main:app \
    --bind 0.0.0.0:$PORT \
    --timeout 300 \
    --graceful-timeout 120 \
    --workers 1 \
    --worker-class sync \
    --keepalive 5 \
    --log-level info