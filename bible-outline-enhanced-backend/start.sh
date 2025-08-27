#!/bin/bash
cd bible-outline-enhanced-backend/src
gunicorn main:app --bind 0.0.0.0:$PORT --timeout 300 --graceful-timeout 120 --keep-alive 5