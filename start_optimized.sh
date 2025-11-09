#!/bin/bash

#!/usr/bin/env bash

# Optimized startup script for Flask app with OpenRouter and Ollama
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

# Check if OpenRouter API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  OPENROUTER_API_KEY not set in environment"
    echo "   Loading from .env file..."
fi

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/version > /dev/null; then
    echo "⚠️  Warning: Ollama does not appear to be running at localhost:11434"
    echo "   Make sure to start Ollama before using the UnlearningToRest model"
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
