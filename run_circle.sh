#!/bin/bash
# Simple runner script for the framebuffer circle program

cd "$(dirname "$0")"

echo "Blue Circle Display Program"
echo "=========================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python3 -c "import pygame" >/dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "Running direct framebuffer circle program..."
echo "The blue circle should appear on your display."
echo ""

python3 direct_fb_circle.py