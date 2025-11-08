# HiFiBerry VU Meter

SDL2-based VU meter display with real-time audio monitoring for embedded systems and Raspberry Pi.

## Overview

HiFiBerry VU Meter is a professional VU meter display application with real-time ALSA audio monitoring. Built with SDL2 for high-performance graphics rendering on embedded systems, particularly Raspberry Pi and other Linux devices with framebuffer support.

## Features

- **Real-time VU Monitoring**: Live ALSA audio input with configurable update rates (5-60 Hz)
- **Multiple Display Modes**: Demo animation, real-time audio, or fixed needle position
- **Configurable Audio Channels**: Left, right, stereo average, or maximum level
- **Smooth Needle Movement**: Configurable averaging for fluid display (1-20 readings)
- **Customizable VU Scales**: Configurable dB ranges and needle parameters per configuration
- **Multiple VU Meter Images**: Support for different VU meter faces and scales
- **Display Rotation**: 0°, 90°, 180°, 270° rotation support for various mounting orientations
- **SDL2 Hardware Acceleration**: High-performance graphics with framebuffer support
- **Professional VU Metering**: Industry-standard VU level calculations with proper dB scaling
- **Song Detection**: AcoustID integration for automatic song identification from audio input

## Installation

### Automated Installation (Recommended)

Install all system dependencies including SDL2, PortAudio, and ALSA:

```bash
sudo ./install-dependencies
```

This will install:
- SDL2 core libraries and extensions
- PortAudio libraries (required for PyAudio)
- ALSA development libraries
- Python development headers
- All necessary build tools

Then install the Python package:

```bash
# Ensure proper permissions for user install directory
mkdir -p ~/.local/bin
chmod 755 ~/.local/bin

# Install the package
pip3 install --break-system-packages -e .
```

If you encounter permission errors, fix the permissions:

```bash
# Fix permissions on existing files
chmod -R u+w ~/.local/bin ~/.local/lib

# Then retry installation
pip3 install --break-system-packages -e .
```

### Manual Installation

If you prefer to install components separately:

```bash
# System packages
sudo apt update
sudo apt install -y \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    portaudio19-dev \
    libasound2-dev \
    alsa-utils

# Python bindings
pip3 install --break-system-packages PySDL2

# Ensure proper permissions
mkdir -p ~/.local/bin
chmod 755 ~/.local/bin

# Install the package
pip3 install --break-system-packages -e .
```

### Verification

Test the installation:

```bash
# Test SDL2
cd sdl2
python3 test-sdl2.py

# Test all imports
python3 -c "import sdl2; import pyaudio; import alsaaudio; print('All imports successful!')"

# Run the VU meter
hifiberry-vu
```

## Project Structure

```
round/
├── sdl2/                   # SDL2 installation and testing
│   ├── install-sdl2        # Automated installation script
│   ├── test-sdl2.py        # SDL2 functionality test
│   └── README.md           # SDL2 documentation
├── analog_clock.py         # Analog clock application
├── sdl2_example.py         # Basic SDL2 example
├── run.sh                  # Main project launcher
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── .gitignore             # Git ignore rules
```

## Getting Started

### Quick Start

```bash
# Run the main launcher
./run.sh

# Or run applications directly:
python3 analog_clock.py      # Analog clock with smooth second hand
python3 sdl2_example.py      # Basic SDL2 test pattern
python3 sdl2/test-sdl2.py    # SDL2 installation test
```

### Analog Clock Application

The included analog clock features:
- **700px diameter** clock on 720x720px screen
- **Smooth second hand** movement (updates continuously, not just every second)
- Hour and minute marks with proper proportions
- Real-time display using system time
- Exit with 'q' key or Ctrl+C

### Basic SDL2 Setup for Framebuffer

```python
import sdl2
import os

# Configure for framebuffer rendering
os.environ['SDL_VIDEODRIVER'] = 'KMSDRM'  # or 'fbcon'
os.environ['SDL_FBDEV'] = '/dev/fb0'

# Initialize SDL2
sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)

# Create window/surface
window = sdl2.SDL_CreateWindow(
    b"SDL2 App",
    sdl2.SDL_WINDOWPOS_UNDEFINED,
    sdl2.SDL_WINDOWPOS_UNDEFINED,
    720, 720,
    sdl2.SDL_WINDOW_SHOWN
)
```

### Available Video Drivers

The SDL2 installation supports multiple video drivers:
- **KMSDRM**: Kernel Mode Setting Direct Rendering Manager (recommended)
- **fbcon**: Direct framebuffer console
- **x11**: X11 windowing system (if available)
- **wayland**: Wayland compositor (if available)
- **dummy**: Software-only rendering

## Development Workflow

1. **Install SDL2**: Run `sudo ./sdl2/install-sdl2`
2. **Test Setup**: Run `python3 sdl2/test-sdl2.py`
3. **Create Application**: Build your SDL2-based graphics application
4. **Configure Environment**: Set SDL video driver for target platform

## System Requirements

- **OS**: Debian/Ubuntu or compatible Linux distribution
- **Hardware**: ARM or x86_64 with framebuffer support
- **Permissions**: User in `video` group for framebuffer access
- **Python**: 3.7+ with pip

## Framebuffer Configuration

For direct framebuffer rendering:

```bash
# Check framebuffer device
ls -la /dev/fb*

# Check resolution and color depth
cat /sys/class/graphics/fb0/virtual_size
cat /sys/class/graphics/fb0/bits_per_pixel

# Set permissions (if needed)
sudo usermod -a -G video $USER
```

## Environment Variables

Configure SDL2 behavior:

```bash
export SDL_VIDEODRIVER=KMSDRM    # Video driver
export SDL_FBDEV=/dev/fb0        # Framebuffer device
export SDL_NOMOUSE=1             # Disable mouse cursor
```

## Troubleshooting

### Permission Issues
```bash
sudo usermod -a -G video $USER
newgrp video
```

### SDL2 Import Errors
```bash
pip3 install --break-system-packages PySDL2
```

### Video Driver Issues
```bash
python3 sdl2/test-sdl2.py  # Check available drivers
```

## Next Steps

This repository is now ready for SDL2-based development. You can:

1. Create graphics applications using SDL2's powerful API
2. Implement hardware-accelerated rendering
3. Build cross-platform applications that work on embedded systems
4. Leverage SDL2's extensive ecosystem (image loading, audio, input, etc.)

## Migration Notes

This project has been cleaned up to focus exclusively on SDL2. Previous direct framebuffer implementations have been removed in favor of SDL2's more robust and performant approach.

SDL2 provides:
- Better hardware acceleration
- More reliable video driver support  
- Cross-platform compatibility
- Rich feature set (audio, input, networking, etc.)
- Active development and community support

## Song Detection Tool

The project includes a command-line tool for automatic song identification using AcoustID:

```bash
# Install Chromaprint for audio fingerprinting
sudo apt-get install libchromaprint-tools

# Detect currently playing song (10 second recording)
python3 detect_song.py --api-key YOUR_API_KEY

# Use longer recording for better accuracy
python3 detect_song.py --api-key YOUR_API_KEY --duration 15

# Specify ALSA device
python3 detect_song.py --api-key YOUR_API_KEY --device "hw:1,0"

# Continuous monitoring mode (check every 30 seconds)
python3 detect_song.py --api-key YOUR_API_KEY --continuous --interval 30
```

**Features:**
- Records audio from ALSA at 44.1kHz, 16-bit stereo
- Generates Chromaprint fingerprints
- Queries AcoustID API for song identification
- Displays artist, title, album, and MusicBrainz metadata
- Continuous monitoring mode for real-time detection
- Supports custom ALSA devices

**Get an API key:** Register your application at https://acoustid.org/new-application

See [ACOUSTID_README.md](ACOUSTID_README.md) for more information about the AcoustID API client.

## References

- [SDL2 Documentation](https://wiki.libsdl.org/)
- [PySDL2 Documentation](https://pysdl2.readthedocs.io/)
- [SDL2 Installation Guide](./sdl2/README.md)
- [AcoustID API Documentation](https://acoustid.org/webservice)
