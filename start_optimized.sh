#!/bin/bash

#!/usr/bin/env bash

# Optimized startup script for Flask app with Hugging Face
# Handles concurrent users efficiently

echo "=========================================="
echo "Starting Flask Application"
echo "=========================================="
echo ""

cd "$(dirname "$0")" || exit 1

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

source venv/bin/activate

# Check if Hugging Face token is set
if [ -z "$HUGGINGFACE_API_TOKEN" ]; then
    echo "⚠️  HUGGINGFACE_API_TOKEN not set in environment"
    echo "   Loading from .env file..."
fi

# Start with Gunicorn for better concurrency
if command -v gunicorn &> /dev/null; then
    echo "Starting with Gunicorn (8 workers)..."
    gunicorn -w 8 \
        -b 0.0.0.0:5000 \
        --timeout 120 \
        --access-logfile logs/access.log \
        --error-logfile logs/error.log \
        'backend.app:create_app()'
else
    echo "Gunicorn not found, starting with Flask dev server..."
    echo "⚠️  For 30+ users, install Gunicorn: pip install gunicorn"
    cd backend && python app.py
fi

