# SDL2 Installation and Setup

This directory contains scripts and documentation for installing SDL2 with Python bindings on Debian/Ubuntu systems.

## Overview

SDL2 (Simple DirectMedia Layer) is a cross-platform development library designed to provide low-level access to audio, keyboard, mouse, joystick, and graphics hardware via OpenGL and Direct3D. For framebuffer applications, SDL2 can provide better hardware acceleration and more reliable video driver support than direct framebuffer access.

## Files

- **`install-sdl2`** - Installation script for SDL2 and Python bindings
- **`test-sdl2.py`** - Test script to verify SDL2 installation and capabilities
- **`README.md`** - This documentation

## Installation

### Automatic Installation (Recommended)

Run the installation script with sudo privileges:

```bash
cd /home/matuschd/round/sdl2
sudo ./install-sdl2
```

This script will:
1. Update package lists
2. Install SDL2 core libraries and development headers
3. Install SDL2 extension libraries (image, mixer, ttf, gfx)
4. Install Python development packages
5. Install PySDL2 Python bindings
6. Verify the installation

### Manual Installation

If you prefer to install manually:

```bash
# Core SDL2 libraries
sudo apt update
sudo apt install -y libsdl2-dev libsdl2-2.0-0

# SDL2 extensions
sudo apt install -y libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libsdl2-gfx-dev

# Python bindings - try system package first
sudo apt install -y python3-dev python3-pip python3-sdl2

# If system package has issues, use pip with --break-system-packages
pip3 install --break-system-packages PySDL2
```

## Testing Installation

After installation, test SDL2 functionality:

```bash
cd /home/matuschd/round/sdl2
python3 test-sdl2.py
```

The test script will:
- Verify PySDL2 imports correctly
- Initialize SDL2 and list available video drivers
- Check framebuffer device access
- Display relevant environment variables

## Configuration for Framebuffer

To use SDL2 with framebuffer rendering (no X11):

```bash
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0
export SDL_NOMOUSE=1
```

Add these to your shell profile for persistent configuration:

```bash
echo 'export SDL_VIDEODRIVER=fbcon' >> ~/.bashrc
echo 'export SDL_FBDEV=/dev/fb0' >> ~/.bashrc
echo 'export SDL_NOMOUSE=1' >> ~/.bashrc
```

## Troubleshooting

### Permission Issues

If you get framebuffer access denied:

```bash
# Add user to video group
sudo usermod -a -G video $USER
# Then log out and back in, or:
newgrp video
```

### SDL2 Import Errors

If `import sdl2` fails:

```bash
# Try installing via pip with --break-system-packages
pip3 install --break-system-packages PySDL2

# Or system package (if available)
sudo apt install python3-sdl2
```

Note: Debian/Ubuntu may require `--break-system-packages` flag for pip installations due to PEP 668.

### Video Driver Issues

Check available drivers:

```bash
python3 test-sdl2.py
```

Common video drivers:
- `fbcon` - Framebuffer console (for headless systems)
- `x11` - X11 windowing system
- `wayland` - Wayland compositor
- `dummy` - Dummy driver (no output)

### Framebuffer Not Found

Ensure framebuffer support is enabled:

```bash
# Check if framebuffer devices exist
ls -la /dev/fb*

# Check framebuffer info
cat /sys/class/graphics/fb0/virtual_size
cat /sys/class/graphics/fb0/bits_per_pixel
```

## Performance Comparison

SDL2 vs Direct Framebuffer Access:

| Method | Pros | Cons |
|--------|------|------|
| **SDL2** | - Hardware acceleration<br>- Cross-platform<br>- Robust video drivers<br>- Better performance | - Additional dependency<br>- More complex setup |
| **Direct FB** | - No dependencies<br>- Simple implementation<br>- Direct control | - No hardware acceleration<br>- Platform-specific<br>- Driver issues |

## Integration with Vinyl Record Animation

After SDL2 installation, you can use it for improved vinyl record animation:

```bash
# Set framebuffer mode
export SDL_VIDEODRIVER=fbcon
export SDL_FBDEV=/dev/fb0

# Run SDL2-based vinyl animation (if implemented)
cd /home/matuschd/round
python3 vinyl_with_sdl2.py
```

## Package Details

### Core SDL2 Packages
- `libsdl2-2.0-0` - SDL2 runtime library
- `libsdl2-dev` - SDL2 development headers

### Extension Packages
- `libsdl2-image-2.0-0` / `libsdl2-image-dev` - Image loading (PNG, JPEG, etc.)
- `libsdl2-mixer-2.0-0` / `libsdl2-mixer-dev` - Audio mixing
- `libsdl2-ttf-2.0-0` / `libsdl2-ttf-dev` - TrueType font rendering
- `libsdl2-gfx-1.0-0` / `libsdl2-gfx-dev` - Graphics primitives

### Python Packages
- `python3-sdl2` - System package (if available)
- `PySDL2` - pip package

## References

- [SDL2 Official Documentation](https://wiki.libsdl.org/)
- [PySDL2 Documentation](https://pysdl2.readthedocs.io/)
- [SDL2 Framebuffer Guide](https://wiki.libsdl.org/SDL2/README/linux)