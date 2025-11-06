#!/usr/bin/env python3
"""
FPS benchmark and performance test for framebuffer access.
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

def test_raw_framebuffer_speed():
    """Test raw framebuffer write speed."""
    fb_width, fb_height, bytes_per_pixel, bpp = get_framebuffer_info()
    
    print(f"Testing raw framebuffer performance...")
    print(f"Resolution: {fb_width}x{fb_height}, {bpp} bpp")
    
    try:
        with open('/dev/fb0', 'r+b') as fb:
            fb_size = fb_width * fb_height * bytes_per_pixel
            fb_map = mmap.mmap(fb.fileno(), fb_size)
            
            # Test 1: Simple fill
            print("\nTest 1: Simple black fill")
            start_time = time.time()
            test_frames = 100
            
            for frame in range(test_frames):
                fb_map[:] = b'\x00' * fb_size
                fb_map.flush()
            
            duration = time.time() - start_time
            fps = test_frames / duration
            print(f"Simple fill: {fps:.1f} FPS ({duration:.2f}s for {test_frames} frames)")
            
            # Test 2: Pattern fill
            print("\nTest 2: Simple pattern fill")
            blue_565 = rgb_to_rgb565(0, 0, 255)
            pattern = struct.pack('H', blue_565) * (fb_width * fb_height)
            
            start_time = time.time()
            for frame in range(test_frames):
                fb_map[:] = pattern
                fb_map.flush()
            
            duration = time.time() - start_time
            fps = test_frames / duration
            print(f"Pattern fill: {fps:.1f} FPS ({duration:.2f}s for {test_frames} frames)")
            
            # Test 3: Pixel-by-pixel writing
            print("\nTest 3: Pixel-by-pixel circle drawing")
            test_frames = 10  # Fewer frames for pixel-by-pixel test
            
            start_time = time.time()
            for frame in range(test_frames):
                # Clear
                fb_map[:] = b'\x00' * fb_size
                
                # Draw circle pixel by pixel
                center_x, center_y = fb_width // 2, fb_height // 2
                radius = 100
                
                for y in range(center_y - radius, center_y + radius):
                    for x in range(center_x - radius, center_x + radius):
                        if 0 <= x < fb_width and 0 <= y < fb_height:
                            dx, dy = x - center_x, y - center_y
                            if dx*dx + dy*dy <= radius*radius:
                                pixel_offset = (y * fb_width + x) * 2
                                fb_map[pixel_offset:pixel_offset+2] = struct.pack('H', blue_565)
                
                fb_map.flush()
            
            duration = time.time() - start_time
            fps = test_frames / duration
            print(f"Pixel-by-pixel: {fps:.1f} FPS ({duration:.2f}s for {test_frames} frames)")
            
            # Test 4: Optimized circle using bytearray
            print("\nTest 4: Optimized circle using bytearray")
            test_frames = 50
            
            start_time = time.time()
            for frame in range(test_frames):
                # Create frame in memory first
                frame_data = bytearray(fb_size)
                
                # Draw circle
                for y in range(center_y - radius, center_y + radius):
                    for x in range(center_x - radius, center_x + radius):
                        if 0 <= x < fb_width and 0 <= y < fb_height:
                            dx, dy = x - center_x, y - center_y
                            if dx*dx + dy*dy <= radius*radius:
                                pixel_offset = (y * fb_width + x) * 2
                                frame_data[pixel_offset:pixel_offset+2] = struct.pack('H', blue_565)
                
                # Write entire frame at once
                fb_map[:] = frame_data
                fb_map.flush()
            
            duration = time.time() - start_time
            fps = test_frames / duration
            print(f"Optimized circle: {fps:.1f} FPS ({duration:.2f}s for {test_frames} frames)")
            
            # Clear screen
            fb_map[:] = b'\x00' * fb_size
            fb_map.flush()
            fb_map.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

def test_vinyl_performance():
    """Test actual vinyl record animation performance."""
    fb_width, fb_height, bytes_per_pixel, bpp = get_framebuffer_info()
    
    print(f"\nTesting vinyl record animation performance...")
    
    # Simplified vinyl drawing for performance test
    def draw_simple_vinyl(frame_data, rotation_angle):
        center_x, center_y = fb_width // 2, fb_height // 2
        record_radius = 300
        
        vinyl_color = rgb_to_rgb565(30, 30, 30)
        groove_color = rgb_to_rgb565(50, 50, 50)
        
        for y in range(fb_height):
            for x in range(fb_width):
                dx, dy = x - center_x, y - center_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= record_radius:
                    # Simple groove pattern
                    groove_num = int(distance) % 10
                    if groove_num < 2:
                        color = groove_color
                    else:
                        color = vinyl_color
                    
                    pixel_offset = (y * fb_width + x) * 2
                    frame_data[pixel_offset:pixel_offset+2] = struct.pack('H', color)
    
    try:
        with open('/dev/fb0', 'r+b') as fb:
            fb_size = fb_width * fb_height * bytes_per_pixel
            fb_map = mmap.mmap(fb.fileno(), fb_size)
            
            test_frames = 30
            start_time = time.time()
            
            for frame in range(test_frames):
                frame_data = bytearray(fb_size)
                rotation_angle = (frame * 0.1) % (2 * math.pi)
                
                draw_simple_vinyl(frame_data, rotation_angle)
                
                fb_map[:] = frame_data
                fb_map.flush()
            
            duration = time.time() - start_time
            fps = test_frames / duration
            print(f"Vinyl animation: {fps:.1f} FPS ({duration:.2f}s for {test_frames} frames)")
            
            # Calculate theoretical maximum FPS for smooth animation
            print(f"\nFor smooth 33.3 RPM rotation:")
            print(f"- Need at least 10-15 FPS for visible rotation")
            print(f"- Recommended: 20-30 FPS for smooth animation")
            print(f"- Current performance: {fps:.1f} FPS")
            
            if fps < 10:
                print("⚠️  Performance too low for smooth animation")
            elif fps < 20:
                print("⚠️  Performance adequate but may appear choppy")
            else:
                print("✅ Performance sufficient for smooth animation")
            
            # Clear screen
            fb_map[:] = b'\x00' * fb_size
            fb_map.flush()
            fb_map.close()
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    print("Framebuffer Performance Benchmark")
    print("=================================")
    
    test_raw_framebuffer_speed()
    test_vinyl_performance()
    
    print("\nBenchmark complete!")
    print("\nOptimization tips:")
    print("- Use bytearray for frame preparation")
    print("- Minimize flush() calls")
    print("- Pre-calculate patterns when possible")
    print("- Consider reducing frame rate if performance is low")