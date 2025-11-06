#!/bin/bash
# Simple runner script for the vinyl record animation

cd "$(dirname "$0")"

echo "Vinyl Record Animation"
echo "====================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "Choose animation:"
echo "1. Ultra-fast vinyl record (vinyl_ultra_fast.py) - Recommended"
echo "2. Simple vinyl record (vinyl_simple.py) - Lightweight"
echo "3. Static blue circle (direct_fb_circle.py)"
echo "4. FPS benchmark test (fps_benchmark.py)"
echo ""
read -p "Enter choice (1-4, default=1): " choice

case ${choice:-1} in
    1)
        echo "Running ultra-fast vinyl record animation at 33.3 RPM..."
        python3 vinyl_ultra_fast.py
        ;;
    2)
        echo "Running simple vinyl record animation..."
        python3 vinyl_simple.py
        ;;
    3)
        echo "Running static blue circle..."
        python3 direct_fb_circle.py
        ;;
    4)
        echo "Running FPS benchmark..."
        python3 fps_benchmark.py
        ;;
    *)
        echo "Invalid choice, running ultra-fast vinyl record..."
        python3 vinyl_ultra_fast.py
        ;;
esac