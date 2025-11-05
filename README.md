# round

A Python application that draws a blue circle (600px diameter) centered on a 720x720px display using direct framebuffer access (no X11 required).

## Features

- Direct framebuffer rendering (no X11/desktop environment needed)
- Fixed display size: 720x720 pixels  
- Blue circle with 600px diameter perfectly centered
- Works on embedded systems and headless setups
- Multiple implementation options (direct framebuffer, Kivy, Pygame)

## Requirements

- Python 3.7+
- Access to `/dev/fb0` (framebuffer device)
- User must be in `video` group or run with appropriate permissions

## Quick Start

The easiest way to run the program:

```bash
./run_circle.sh
```

This script will automatically set up the virtual environment, install dependencies, and run the direct framebuffer version.

## Manual Installation and Setup

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Option 1: Direct Framebuffer (Recommended)
```bash
source venv/bin/activate
python3 direct_fb_circle.py
```

This version writes directly to `/dev/fb0` and works without any window system.

### Option 2: Pygame Version
```bash
source venv/bin/activate  
python3 pygame_circle.py
```

### Option 3: Kivy Version (for X11 systems)
```bash
source venv/bin/activate
python3 main.py
```

## Files

- `direct_fb_circle.py` - **Recommended**: Direct framebuffer implementation
- `pygame_circle.py` - Pygame-based framebuffer version  
- `main.py` - Kivy implementation (requires X11)
- `main_framebuffer.py` - Kivy with framebuffer configuration
- `run_circle.sh` - Automated setup and run script
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Technical Details

### Direct Framebuffer Version
- Reads framebuffer properties from `/sys/class/graphics/fb0/`
- Supports 16-bit (RGB565), 24-bit (RGB), and 32-bit (RGBA/BGRA) color formats
- Uses memory mapping for efficient pixel access
- Circle drawn using distance calculation from center point

### Display Configuration
- Target framebuffer: 720x720 pixels, 16-bit color depth
- Circle: 600px diameter (300px radius)
- Center position: (360, 360)
- Color: Pure blue (RGB565: 0x001F)

## Troubleshooting

### Permission Issues
If you get "Permission denied" accessing `/dev/fb0`:

```bash
# Add user to video group
sudo usermod -a -G video $USER
# Then log out and back in, or run:
newgrp video

# Or run with sudo (not recommended for regular use)
sudo python3 direct_fb_circle.py
```

### Framebuffer Not Available
Ensure your system has framebuffer support enabled and `/dev/fb0` exists:
```bash
ls -la /dev/fb*
```

### Display Issues
- Verify framebuffer resolution: `cat /sys/class/graphics/fb0/virtual_size`
- Check color depth: `cat /sys/class/graphics/fb0/bits_per_pixel`
