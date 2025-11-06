#!/usr/bin/env python3
"""
Lightweight vinyl record animation - minimal but smooth.
"""

import struct
import mmap
import os
import sys
import math
import time

def rgb_to_rgb565(r, g, b):
    return ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)

def create_simple_vinyl_frames():
    """Create a set of simple vinyl frames for rotation."""
    fb_size = 720 * 720 * 2  # 720x720, 2 bytes per pixel
    num_frames = 36  # 36 frames = 10-degree increments
    
    frames = []
    center = 360
    record_radius = 300
    
    # Colors
    black = rgb_to_rgb565(0, 0, 0)
    vinyl = rgb_to_rgb565(25, 25, 25)
    groove = rgb_to_rgb565(45, 45, 45)
    label = rgb_to_rgb565(140, 30, 30)
    
    print(f"Creating {num_frames} simple vinyl frames...")
    
    for frame_num in range(num_frames):
        frame_data = bytearray(fb_size)
        rotation = (frame_num / num_frames) * 2 * math.pi
        
        # Draw vinyl record
        for y in range(720):
            row_offset = y * 720 * 2
            for x in range(720):
                dx, dy = x - center, y - center
                distance = int(math.sqrt(dx*dx + dy*dy))
                
                pixel_offset = row_offset + x * 2
                
                if distance <= 8:  # Spindle
                    color = black
                elif distance <= 50:  # Label
                    color = label
                elif distance <= record_radius:  # Vinyl surface
                    # Simple groove pattern with rotation
                    angle = math.atan2(dy, dx) + rotation
                    groove_pattern = int((distance - 50) / 6) + int(angle * 3)
                    if groove_pattern % 4 == 0:
                        color = groove
                    else:
                        color = vinyl
                else:  # Background
                    color = black
                
                frame_data[pixel_offset:pixel_offset+2] = struct.pack('H', color)
        
        frames.append(bytes(frame_data))
    
    return frames

def animate_simple_vinyl():
    """Simple vinyl animation with pre-calculated frames."""
    
    print("Framebuffer: 720x720, 16 bpp")
    
    # Pre-calculate frames
    frames = create_simple_vinyl_frames()
    
    print("Starting simple vinyl animation at 33.3 RPM...")
    print("Press Ctrl+C to stop")
    
    try:
        with open('/dev/fb0', 'r+b') as fb:
            fb_map = mmap.mmap(fb.fileno(), 720 * 720 * 2)
            
            start_time = time.time()
            frame_count = 0
            
            # 33.3 RPM = 1 rotation per 1.8 seconds
            # 36 frames per rotation = 1.8/36 = 0.05 seconds per frame
            frame_duration = 1.8 / 36
            
            try:
                while True:
                    frame_start = time.time()
                    
                    # Calculate frame index
                    elapsed_time = time.time() - start_time
                    frame_index = int(elapsed_time / frame_duration) % 36
                    
                    # Display frame
                    fb_map[:] = frames[frame_index]
                    fb_map.flush()
                    
                    frame_count += 1
                    
                    # Stats every 5 seconds
                    if frame_count % 100 == 0:
                        actual_fps = frame_count / elapsed_time
                        rotations = elapsed_time / 1.8
                        rpm = rotations * 60 / elapsed_time if elapsed_time > 0 else 0
                        print(f"FPS: {actual_fps:.1f}, RPM: {rpm:.1f}")
                    
                    # Maintain 20 FPS (good enough for smooth rotation)
                    frame_time = time.time() - frame_start
                    sleep_time = (1.0 / 20) - frame_time
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                        
            except KeyboardInterrupt:
                print(f"\nStopped after {frame_count} frames")
                fb_map[:] = b'\x00' * len(fb_map)
                fb_map.flush()
            
            fb_map.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    print("Simple Vinyl Record Animation")
    print("============================")
    sys.exit(animate_simple_vinyl())