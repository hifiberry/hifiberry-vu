#!/usr/bin/env python3
"""
PNG-based vinyl record animation player.
Loads pre-generated PNG frames and displays them at 33.3 RPM.
"""

import struct
import mmap
import os
import sys
import time
import glob

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

def load_png_frame(filename):
    """Load a PNG frame and convert to RGB565 framebuffer data."""
    try:
        from PIL import Image
    except ImportError:
        print("Error: PIL (Pillow) is required")
        print("Install with: pip install Pillow")
        return None
    
    # Load PNG
    img = Image.open(filename)
    img = img.convert('RGB')
    
    # Ensure correct size
    if img.size != (720, 720):
        img = img.resize((720, 720), Image.Resampling.LANCZOS)
    
    # Convert to RGB565 framebuffer data
    fb_data = bytearray(720 * 720 * 2)  # 2 bytes per pixel
    
    pixels = img.load()
    for y in range(720):
        for x in range(720):
            r, g, b = pixels[x, y]
            
            # Convert to RGB565
            rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            
            # Write to framebuffer data
            pixel_offset = (y * 720 + x) * 2
            fb_data[pixel_offset:pixel_offset+2] = struct.pack('H', rgb565)
    
    return bytes(fb_data)

def load_all_frames():
    """Load all PNG frames into memory."""
    frames_dir = "vinyl_frames"
    
    if not os.path.exists(frames_dir):
        print(f"Error: {frames_dir} directory not found")
        print("Run 'python3 generate_vinyl_frames.py' first")
        return None
    
    # Find all frame files
    frame_files = sorted(glob.glob(f"{frames_dir}/vinyl_frame_*.png"))
    
    if not frame_files:
        print(f"Error: No PNG frames found in {frames_dir}")
        print("Run 'python3 generate_vinyl_frames.py' first")
        return None
    
    print(f"Loading {len(frame_files)} PNG frames...")
    
    frames = []
    for i, filename in enumerate(frame_files):
        print(f"Loading frame {i+1}/{len(frame_files)}", end='\r')
        
        frame_data = load_png_frame(filename)
        if frame_data is None:
            return None
        
        frames.append(frame_data)
    
    print(f"\nLoaded {len(frames)} frames successfully!")
    return frames

def animate_png_vinyl():
    """Animate vinyl record using PNG frames."""
    
    fb_width, fb_height, bytes_per_pixel, bpp = get_framebuffer_info()
    print(f"Framebuffer: {fb_width}x{fb_height}, {bpp} bpp")
    
    # Load all frames
    frames = load_all_frames()
    if frames is None:
        return 1
    
    num_frames = len(frames)
    
    print(f"Starting PNG-based vinyl animation...")
    print(f"Frames: {num_frames}, 33.3 RPM")
    print("Press Ctrl+C to stop")
    
    # 33.3 RPM = one rotation every 1.8 seconds
    # With N frames, each frame represents 1.8/N seconds
    frame_duration = 1.8 / num_frames
    
    try:
        with open('/dev/fb0', 'r+b') as fb:
            fb_size = fb_width * fb_height * bytes_per_pixel
            fb_map = mmap.mmap(fb.fileno(), fb_size)
            
            start_time = time.time()
            frame_count = 0
            
            try:
                while True:
                    frame_start = time.time()
                    
                    # Calculate which frame to show
                    elapsed_time = time.time() - start_time
                    frame_index = int(elapsed_time / frame_duration) % num_frames
                    
                    # Display frame
                    fb_map[:] = frames[frame_index]
                    fb_map.flush()
                    
                    frame_count += 1
                    
                    # Performance stats
                    if frame_count % 150 == 0:  # Every ~5 seconds
                        actual_fps = frame_count / elapsed_time
                        rotations = elapsed_time / 1.8
                        current_rpm = rotations * 60 / elapsed_time if elapsed_time > 0 else 0
                        print(f"Performance: {actual_fps:.1f} FPS, {current_rpm:.1f} RPM (PNG-based)")
                    
                    # Frame rate control - target 30 FPS for smooth display
                    frame_end = time.time()
                    frame_time = frame_end - frame_start
                    target_fps = 30
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

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        from PIL import Image
        return True
    except ImportError:
        print("Error: PIL (Pillow) is required for PNG support")
        print("Install with:")
        print("  pip install Pillow")
        print("")
        print("Or if using system packages:")
        print("  sudo apt install python3-pil")
        return False

if __name__ == '__main__':
    print("PNG-Based Vinyl Record Animation")
    print("===============================")
    
    if not check_dependencies():
        sys.exit(1)
    
    sys.exit(animate_png_vinyl())