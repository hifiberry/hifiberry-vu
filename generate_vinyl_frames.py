#!/usr/bin/env python3
"""
Generate PNG frames for vinyl record animation.
Creates 36 frames (10-degree increments) for smooth rotation.
"""

import os
import sys
import math
from PIL import Image, ImageDraw

def create_vinyl_frame(frame_num, total_frames=36):
    """Create a single vinyl record frame."""
    
    # Image settings
    size = 720
    center = size // 2
    record_radius = 300
    label_radius = 60
    
    # Create image with black background
    img = Image.new('RGB', (size, size), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Calculate rotation angle
    rotation_angle = (frame_num / total_frames) * 2 * math.pi
    
    # Colors
    vinyl_color = (25, 25, 25)      # Dark gray for vinyl
    groove_light = (45, 45, 45)     # Lighter groove
    groove_dark = (15, 15, 15)      # Darker groove
    label_color = (150, 30, 30)     # Red center label
    label_border = (200, 200, 200)  # White label border
    
    # Draw main vinyl disc
    draw.ellipse([center - record_radius, center - record_radius,
                  center + record_radius, center + record_radius], 
                 fill=vinyl_color)
    
    # Draw concentric grooves
    for radius in range(label_radius + 10, record_radius - 10, 8):
        groove_color = groove_dark if (radius // 8) % 2 == 0 else groove_light
        draw.ellipse([center - radius, center - radius,
                      center + radius, center + radius], 
                     outline=groove_color, width=2)
    
    # Draw rotation marks (radial lines)
    for mark_angle in range(0, 360, 30):  # Every 30 degrees
        angle_rad = math.radians(mark_angle) + rotation_angle
        
        # Draw line from label edge to near record edge
        start_radius = label_radius + 5
        end_radius = record_radius - 20
        
        start_x = center + start_radius * math.cos(angle_rad)
        start_y = center + start_radius * math.sin(angle_rad)
        end_x = center + end_radius * math.cos(angle_rad)
        end_y = center + end_radius * math.sin(angle_rad)
        
        draw.line([(start_x, start_y), (end_x, end_y)], 
                  fill=(60, 60, 60), width=2)
    
    # Draw center label
    draw.ellipse([center - label_radius, center - label_radius,
                  center + label_radius, center + label_radius], 
                 fill=label_color)
    
    # Draw label border
    draw.ellipse([center - label_radius + 5, center - label_radius + 5,
                  center + label_radius - 5, center + label_radius - 5], 
                 outline=label_border, width=3)
    
    # Draw center spindle hole
    spindle_radius = 8
    draw.ellipse([center - spindle_radius, center - spindle_radius,
                  center + spindle_radius, center + spindle_radius], 
                 fill=(0, 0, 0))
    
    return img

def generate_vinyl_frames():
    """Generate all PNG frames for vinyl animation."""
    
    # Check if PIL is available
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Error: PIL (Pillow) is required for PNG generation")
        print("Install with: pip install Pillow")
        return False
    
    # Create frames directory
    frames_dir = "vinyl_frames"
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
        print(f"Created directory: {frames_dir}")
    
    total_frames = 36
    print(f"Generating {total_frames} vinyl record frames...")
    
    for frame_num in range(total_frames):
        print(f"Generating frame {frame_num + 1}/{total_frames}", end='\r')
        
        # Create frame
        img = create_vinyl_frame(frame_num, total_frames)
        
        # Save frame
        filename = f"{frames_dir}/vinyl_frame_{frame_num:02d}.png"
        img.save(filename, "PNG")
    
    print(f"\nCompleted! Generated {total_frames} frames in {frames_dir}/")
    
    # Calculate file sizes
    total_size = 0
    for frame_num in range(total_frames):
        filename = f"{frames_dir}/vinyl_frame_{frame_num:02d}.png"
        size = os.path.getsize(filename)
        total_size += size
    
    print(f"Total size: {total_size / (1024*1024):.1f} MB")
    print(f"Average per frame: {total_size / total_frames / 1024:.1f} KB")
    
    return True

if __name__ == '__main__':
    print("Vinyl Record PNG Frame Generator")
    print("===============================")
    
    success = generate_vinyl_frames()
    
    if success:
        print("\nNext step: Run the PNG-based animation with:")
        print("python3 vinyl_png_player.py")
    else:
        print("\nInstall Pillow first:")
        print("pip install Pillow")