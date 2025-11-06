#!/bin/bash
# Quick runner for ultra-fast vinyl record animation

cd "$(dirname "$0")"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "Starting Ultra-Fast Vinyl Record Animation (33.3 RPM)..."
echo "30 FPS - Press Ctrl+C to stop"
echo ""

python3 vinyl_ultra_fast.py