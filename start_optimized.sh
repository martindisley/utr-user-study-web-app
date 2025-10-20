#!/bin/bash

#!/usr/bin/env bash

# Optimized startup script for Ollama + Flask app
# Handles concurrent users efficiently

echo "=========================================="
echo "Starting Ollama with Optimized Settings"
echo "=========================================="
echo ""

# Ollama Configuration for 30 concurrent users
export OLLAMA_NUM_PARALLEL=8        # Process 8 requests simultaneously
export OLLAMA_MAX_LOADED_MODELS=2   # Keep both models in memory
export OLLAMA_MAX_QUEUE=512         # Queue up to 512 requests (default)

# Optional: If using GPU
# export OLLAMA_CUDA=1

echo "Ollama Settings:"
echo "  OLLAMA_NUM_PARALLEL: $OLLAMA_NUM_PARALLEL"
echo "  OLLAMA_MAX_LOADED_MODELS: $OLLAMA_MAX_LOADED_MODELS"
echo "  OLLAMA_MAX_QUEUE: $OLLAMA_MAX_QUEUE"
echo ""

# Check if Ollama is already running
if pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama is already running. Stopping it..."
    pkill ollama
    sleep 2
    echo "✅ Ollama stopped"
    echo ""
fi

# Start Ollama in background
echo "Starting Ollama server..."
ollama serve > logs/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 3

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Failed to start Ollama"
    exit 1
fi

echo "✅ Ollama started successfully (PID: $OLLAMA_PID)"
echo ""

# Check available models
echo "Available models:"
ollama list
echo ""

# Start Flask app
echo "=========================================="
echo "Starting Flask Application"
echo "=========================================="
echo ""

cd "$(dirname "$0")" || exit 1

# Activate virtual environment
source venv/bin/activate

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
