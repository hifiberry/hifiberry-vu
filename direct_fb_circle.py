#!/usr/bin/env python3
"""
Direct framebuffer access to draw a blue circle (600px diameter) on a 720x720px display.
This bypasses SDL and writes directly to /dev/fb0.
"""

import struct
import mmap
import os
import sys
import math

def get_framebuffer_info():
    """Get framebuffer information using fbset or reading /sys."""
    try:
        # Try to get info from /sys/class/graphics/fb0/
        with open('/sys/class/graphics/fb0/virtual_size', 'r') as f:
            w, h = map(int, f.read().strip().split(','))
        
        with open('/sys/class/graphics/fb0/bits_per_pixel', 'r') as f:
            bpp = int(f.read().strip())
            
        # Calculate bytes per pixel
        bytes_per_pixel = bpp // 8
        
        return w, h, bytes_per_pixel, bpp
    except:
        # Default fallback
        print("Could not read framebuffer info, using defaults")
        return 720, 720, 4, 32  # Assume 720x720, 32-bit

def draw_circle_direct_fb():
    """Draw a blue circle directly to framebuffer."""
    
    # Get framebuffer info
    fb_width, fb_height, bytes_per_pixel, bpp = get_framebuffer_info()
    
    print(f"Framebuffer: {fb_width}x{fb_height}, {bpp} bpp, {bytes_per_pixel} bytes/pixel")
    
    # Circle parameters
    circle_radius = 300  # 600px diameter = 300px radius
    center_x = fb_width // 2
    center_y = fb_height // 2
    
    print(f"Drawing blue circle: center=({center_x}, {center_y}), radius={circle_radius}")
    
    try:
        # Open framebuffer device
        with open('/dev/fb0', 'r+b') as fb:
            # Memory map the framebuffer
            fb_size = fb_width * fb_height * bytes_per_pixel
            fb_map = mmap.mmap(fb.fileno(), fb_size)
            
            # Clear screen (black background)
            fb_map[:] = b'\x00' * fb_size
            
            # Draw circle
            for y in range(fb_height):
                for x in range(fb_width):
                    # Calculate distance from center
                    dx = x - center_x
                    dy = y - center_y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Check if point is inside circle
                    if distance <= circle_radius:
                        # Calculate pixel position in framebuffer
                        pixel_offset = (y * fb_width + x) * bytes_per_pixel
                        
                        # Set pixel to blue color
                        if bytes_per_pixel == 4:  # 32-bit RGBA or BGRA
                            # Blue color: depends on format (RGBA vs BGRA)
                            # Try BGRA first (common on ARM)
                            fb_map[pixel_offset:pixel_offset+4] = struct.pack('BBBB', 255, 0, 0, 255)  # BGRA
                        elif bytes_per_pixel == 3:  # 24-bit RGB
                            fb_map[pixel_offset:pixel_offset+3] = struct.pack('BBB', 0, 0, 255)  # RGB
                        elif bytes_per_pixel == 2:  # 16-bit RGB565
                            # Convert to RGB565 format (5-bit red, 6-bit green, 5-bit blue)
                            blue_565 = 0x001F  # Pure blue in RGB565
                            fb_map[pixel_offset:pixel_offset+2] = struct.pack('H', blue_565)
            
            # Sync changes
            fb_map.flush()
            print("Blue circle drawn to framebuffer!")
            print("The circle should now be visible on your display.")
            
            # Keep the image displayed for a while
            input("Press Enter to clear the screen and exit...")
            
            # Clear screen before exit
            fb_map[:] = b'\x00' * fb_size
            fb_map.flush()
            
            fb_map.close()
            
    except PermissionError:
        print("Permission denied accessing /dev/fb0")
        print("Try running with sudo or ensure user is in video group:")
        print("  sudo usermod -a -G video $USER")
        return 1
    except Exception as e:
        print(f"Error accessing framebuffer: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    print("Direct framebuffer circle drawing")
    print("This will draw a blue circle directly to /dev/fb0")
    sys.exit(draw_circle_direct_fb())