#!/bin/bash
# Quick start script for SDL2 development

cd "$(dirname "$0")"

echo "SDL2 Round Project"
echo "=================="
echo ""

# Check if SDL2 is installed
if ! python3 -c "import sdl2" >/dev/null 2>&1; then
    echo "❌ SDL2 not installed. Installing now..."
    echo ""
    cd sdl2
    sudo ./install-sdl2
    cd ..
    echo ""
fi

echo "Choose an option:"
echo "1. Test SDL2 installation"
echo "2. Run SDL2 basic example"
echo "3. Run analog clock"
echo "4. Install/Update SDL2"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Testing SDL2 installation..."
        python3 sdl2/test-sdl2.py
        ;;
    2)
        echo "Running SDL2 basic example..."
        python3 sdl2_example.py
        ;;
    3)
        echo "Starting analog clock..."
        echo "Press 'q' or Ctrl+C to exit the clock"
        python3 analog_clock.py
        ;;
    4)
        echo "Installing/Updating SDL2..."
        cd sdl2
        sudo ./install-sdl2
        ;;
    *)
        echo "Invalid choice. Running analog clock..."
        python3 analog_clock.py
        ;;
esac