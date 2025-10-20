#!/bin/bash

# Setup script for Unlearning to Rest User Study Web App

echo "=========================================="
echo "Unlearning to Rest - Setup Script"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Warning: Ollama is not installed or not in PATH"
    echo "   Please install Ollama from https://ollama.ai"
else
    echo "✓ Ollama found"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install -r backend/requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the server:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  1. source venv/bin/activate"
echo "  2. python backend/app.py"
echo ""
