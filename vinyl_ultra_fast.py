#!/usr/bin/env python3
"""
Ultra-optimized vinyl record animation using pre-calculated rotation frames.
"""

import struct
import mmap
import os
import sys
import math
import time

def get_framebuffer_info():
    """Get framebuffer information."""
    try:
        with open('/sys/class/graphics/fb0/virtual_size', 'r') as f:
            w, h = map(int, f.read().strip().split(','))
        with open('/sys/class/graphics/fb0/bits_per_pixel', 'r') as f:
            bpp = int(f.read().strip())
        bytes_per_pixel = bpp // 8
        return w, h, bytes_per_pixel, bpp
    except:
        return 720, 720, 2, 16

def rgb_to_rgb565(r, g, b):
    """Convert RGB to RGB565."""
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

def create_vinyl_base_pattern(fb_width, fb_height):
    """Create the base vinyl pattern (static elements)."""
    center_x, center_y = fb_width // 2, fb_height // 2
    record_radius = 300
    label_radius = 60
    
    # Colors
    black = rgb_to_rgb565(0, 0, 0)
    vinyl_dark = rgb_to_rgb565(20, 20, 20)
    vinyl_light = rgb_to_rgb565(35, 35, 35)
    groove_dark = rgb_to_rgb565(10, 10, 10)
    label_red = rgb_to_rgb565(150, 30, 30)
    label_white = rgb_to_rgb565(200, 200, 200)
    
    # Pre-calculate pixel data
    base_pattern = bytearray(fb_width * fb_height * 2)  # 2 bytes per pixel for RGB565
    
    print("Pre-calculating vinyl base pattern...")
    
    for y in range(fb_height):
        for x in range(fb_width):
            dx, dy = x - center_x, y - center_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            pixel_offset = (y * fb_width + x) * 2
            
            if distance <= 8:  # Center spindle hole
                color = black
            elif distance <= label_radius - 10:  # Center label
                color = label_red
            elif distance <= label_radius:  # Label border
                color = label_white
            elif distance <= record_radius:  # Vinyl surface
                # Create groove pattern
                groove_distance = (distance - label_radius) % 8
                if groove_distance < 1:
                    color = groove_dark
                elif groove_distance < 2:
                    color = vinyl_light
                else:
                    color = vinyl_dark
            else:  # Background
                color = black
            
            base_pattern[pixel_offset:pixel_offset+2] = struct.pack('H', color)
    
    return base_pattern

def create_rotation_marks(fb_width, fb_height, num_frames=60):
    """Create rotation marks for different frame positions."""
    center_x, center_y = fb_width // 2, fb_height // 2
    record_radius = 300
    label_radius = 60
    
    rotation_marks = []
    
    print(f"Pre-calculating {num_frames} rotation frames...")
    
    for frame in range(num_frames):
        marks = []
        rotation_angle = (frame / num_frames) * 2 * math.pi
        
        # Add radial marks every 30 degrees
        for mark_angle in range(0, 360, 30):
            angle_rad = math.radians(mark_angle) + rotation_angle
            
            # Draw line from label edge to near record edge
            for radius in range(label_radius + 5, record_radius - 20, 3):
                mark_x = int(center_x + radius * math.cos(angle_rad))
                mark_y = int(center_y + radius * math.sin(angle_rad))
                
                if 0 <= mark_x < fb_width and 0 <= mark_y < fb_height:
                    marks.append((mark_x, mark_y))
        
        rotation_marks.append(marks)
    
    return rotation_marks

def draw_optimized_vinyl(fb_map, base_pattern, rotation_marks, frame_index):
    """Draw vinyl record with rotation using pre-calculated data."""
    # Start with base pattern
    fb_map[:] = base_pattern
    
    # Add rotation marks
    mark_color = rgb_to_rgb565(60, 60, 60)  # Slightly lighter for marks
    mark_data = struct.pack('H', mark_color)
    
    marks = rotation_marks[frame_index % len(rotation_marks)]
    for x, y in marks:
        pixel_offset = (y * 720 + x) * 2  # Assuming 720x720
        fb_map[pixel_offset:pixel_offset+2] = mark_data

def animate_vinyl_ultra_optimized():
    """Ultra-optimized vinyl animation."""
    
    fb_width, fb_height, bytes_per_pixel, bpp = get_framebuffer_info()
    print(f"Framebuffer: {fb_width}x{fb_height}, {bpp} bpp")
    
    # Pre-calculate all patterns
    base_pattern = create_vinyl_base_pattern(fb_width, fb_height)
    rotation_marks = create_rotation_marks(fb_width, fb_height, 60)  # 60 pre-calculated frames
    
    print("Starting ultra-optimized vinyl animation...")
    print("Press Ctrl+C to stop")
    
    # 33.3 RPM = one rotation every 1.8 seconds
    # With 60 pre-calculated frames, each frame represents 1.8/60 = 0.03 seconds
    frame_duration = 1.8 / 60  # Time per frame for 33.3 RPM
    
    try:
        with open('/dev/fb0', 'r+b') as fb:
            fb_size = fb_width * fb_height * bytes_per_pixel
            fb_map = mmap.mmap(fb.fileno(), fb_size)
            
            start_time = time.time()
            frame_count = 0
            
            try:
                while True:
                    frame_start = time.time()
                    
                    # Calculate which pre-calculated frame to show
                    elapsed_time = time.time() - start_time
                    frame_index = int(elapsed_time / frame_duration) % 60
                    
                    # Draw frame
                    draw_optimized_vinyl(fb_map, base_pattern, rotation_marks, frame_index)
                    fb_map.flush()
                    
                    frame_count += 1
                    
                    # Performance stats
                    if frame_count % 150 == 0:  # Every ~5 seconds
                        actual_fps = frame_count / elapsed_time
                        rotations = elapsed_time / 1.8  # Number of complete rotations
                        current_rpm = rotations * 60 / elapsed_time if elapsed_time > 0 else 0
                        print(f"Performance: {actual_fps:.1f} FPS, {current_rpm:.1f} RPM (target: 33.3)")
                    
                    # Frame rate control - try to maintain smooth playback
                    frame_end = time.time()
                    frame_time = frame_end - frame_start
                    target_fps = 30  # Target 30 FPS for smooth animation
                    sleep_time = (1.0 / target_fps) - frame_time
                    
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        
            except KeyboardInterrupt:
                print(f"\nStopped after {frame_count} frames")
                fb_map[:] = b'\x00' * fb_size
                fb_map.flush()
            
            fb_map.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    print("Ultra-Optimized Vinyl Record Animation")
    print("=====================================")
    sys.exit(animate_vinyl_ultra_optimized())