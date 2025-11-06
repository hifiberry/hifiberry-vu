# round

SDL2-based graphics application for embedded displays and framebuffer rendering.

## Overview

This project provides a foundation for creating graphics applications using SDL2 on embedded systems, particularly for direct framebuffer rendering without X11. The focus is on high-performance graphics using hardware acceleration where available.

## Features

- **SDL2 Integration**: Modern graphics library with hardware acceleration
- **Framebuffer Support**: Direct rendering to `/dev/fb0` without X11
- **Cross-Platform**: Works on embedded systems, Raspberry Pi, and desktop Linux
- **Clean Architecture**: Fresh start with modern SDL2 best practices

## Installation

### Automated Installation (Recommended)

```bash
cd sdl2
sudo ./install-sdl2
```

This will install:
- SDL2 core libraries and extensions
- PySDL2 Python bindings  
- Development tools and headers

### Manual Installation

```bash
# System packages
sudo apt update
sudo apt install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# Python bindings
pip3 install --break-system-packages PySDL2
```

### Verification

Test the installation:

```bash
cd sdl2
python3 test-sdl2.py
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

## References

- [SDL2 Documentation](https://wiki.libsdl.org/)
- [PySDL2 Documentation](https://pysdl2.readthedocs.io/)
- [SDL2 Installation Guide](./sdl2/README.md)
