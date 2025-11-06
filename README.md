# round

A Python application featuring an animated rotating vinyl record (33.3 RPM) on a 720x720px display using direct framebuffer access (no X11 required).

## Features

- **Rotating vinyl record animation** at authentic 33.3 RPM
- Direct framebuffer rendering (no X11/desktop environment needed)
- Fixed display size: 720x720 pixels
- Optimized for smooth 30 FPS performance
- Works on embedded systems and headless setups
- **No external dependencies** - uses only Python standard library

## Performance

The vinyl record animation achieves:
- **30 FPS** with ultra-optimized version
- **Exactly 33.3 RPM** rotation speed (authentic vinyl speed)
- Smooth animation using pre-calculated frame data
- Efficient memory usage with mmap framebuffer access

## Quick Start

**Recommended:** Run the ultra-optimized vinyl animation:
```bash
cd /home/matuschd/round
python3 vinyl_ultra_fast.py
```

Or use the menu script:
```bash
./run_circle.sh
```

For quick vinyl-only launcher:
```bash
./run_vinyl.sh
```

## Installation

No external dependencies needed! Just clone and run:

```bash
git clone <repo-url> round
cd round
python3 vinyl_ultra_fast.py
```

## Available Programs

### 🎵 Vinyl Record Animations

1. **`vinyl_ultra_fast.py`** - ⭐ **Recommended**
   - 30 FPS, perfect 33.3 RPM
   - Pre-calculated patterns for maximum performance
   - Detailed grooves, center label, and rotation marks

2. **`vinyl_simple.py`** - Lightweight alternative
   - 20 FPS, good performance
   - Simpler graphics, lower CPU usage

### 🔵 Other Options

3. **`direct_fb_circle.py`** - Static blue circle
   - Original simple blue circle (600px diameter)
   - No animation, instant display

4. **`fps_benchmark.py`** - Performance testing
   - Measure framebuffer access speed
   - Compare different rendering methods

## File Structure

```
round/
├── vinyl_ultra_fast.py     # ⭐ Ultra-optimized vinyl (30 FPS)
├── vinyl_simple.py         # Lightweight vinyl (20 FPS)
├── direct_fb_circle.py     # Static blue circle
├── fps_benchmark.py        # Performance testing
├── run_circle.sh           # Interactive menu launcher
├── run_vinyl.sh            # Quick vinyl launcher
├── requirements.txt        # (Empty - no dependencies)
├── README.md               # This documentation
└── .gitignore             # Git ignore rules
```

## Technical Details

### Ultra-Fast Implementation
- **Pre-calculation**: All 60 rotation frames calculated at startup
- **Memory efficiency**: Uses mmap for direct framebuffer access
- **Timing accuracy**: Frame timing ensures exactly 33.3 RPM
- **Color format**: Optimized RGB565 (16-bit) encoding
- **No dependencies**: Pure Python standard library

### Vinyl Record Design
- **Diameter**: 600px (300px radius) 
- **Center label**: 60px radius with red color
- **Grooves**: Concentric circles every 8 pixels
- **Rotation marks**: Radial lines every 30 degrees
- **Spindle hole**: 8px radius center hole

### Performance Benchmarks

| Operation | Performance | Implementation |
|-----------|-------------|----------------|
| Simple fill | 1000+ FPS | Memory operations |
| Pattern fill | 2500+ FPS | Pre-calculated data |
| Ultra-fast vinyl | **30 FPS** | Pre-calculated frames |
| Simple vinyl | **20 FPS** | Optimized rendering |

## Requirements

- Python 3.7+
- Access to `/dev/fb0` (framebuffer device)
- User in `video` group or appropriate permissions
- **No external packages required**

## Troubleshooting

### Permission Issues
```bash
# Add user to video group
sudo usermod -a -G video $USER
# Log out and back in, or:
newgrp video
```

### Performance Check
```bash
# Test actual performance
python3 fps_benchmark.py
```

### Framebuffer Access
```bash
# Verify framebuffer exists
ls -la /dev/fb*
cat /sys/class/graphics/fb0/virtual_size
```
