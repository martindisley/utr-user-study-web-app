#!/bin/bash

# Run script for Unlearning to Rest User Study Web App

echo "Starting Unlearning to Rest User Study Server..."
echo ""

# Navigate to project root
cd "$(dirname "$0")" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the application
python backend/app.py
