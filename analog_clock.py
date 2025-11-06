#!/usr/bin/env python3
"""
Analog Clock Application using SDL2
Features:
- 700px diameter analog clock on 720x720px screen
- Hour, minute, and second hands
- Smooth second hand movement (updates continuously)
- Exit with Ctrl+C or 'q' key
"""

import sdl2
import sdl2.ext
import os
import sys
import time
import math
import ctypes
from datetime import datetime

class AnalogClock:
    def __init__(self, width=720, height=720, clock_diameter=700):
        self.width = width
        self.height = height
        self.clock_diameter = clock_diameter
        self.clock_radius = clock_diameter // 2
        self.center_x = width // 2
        self.center_y = height // 2
        
        self.window = None
        self.renderer = None
        self.running = True
        
        # Clock colors (RGB)
        self.bg_color = (0, 0, 0)           # Black background
        self.face_color = (255, 255, 255)   # White clock face
        self.border_color = (50, 50, 50)    # Dark border
        self.hour_marks_color = (0, 0, 0)   # Black hour marks
        self.minute_marks_color = (100, 100, 100)  # Gray minute marks
        self.hour_hand_color = (0, 0, 0)    # Black hour hand
        self.minute_hand_color = (0, 0, 0)  # Black minute hand
        self.second_hand_color = (255, 0, 0) # Red second hand
        self.center_dot_color = (0, 0, 0)   # Black center dot
        
        # Hand dimensions
        self.hour_hand_length = self.clock_radius * 0.5
        self.minute_hand_length = self.clock_radius * 0.7
        self.second_hand_length = self.clock_radius * 0.8
        self.hour_hand_width = 6
        self.minute_hand_width = 4
        self.second_hand_width = 2
        self.center_dot_radius = 8
        
    def setup_sdl2(self):
        """Initialize SDL2 for framebuffer rendering."""
        # Configure for framebuffer
        os.environ['SDL_VIDEODRIVER'] = 'KMSDRM'
        os.environ['SDL_FBDEV'] = '/dev/fb0'
        os.environ['SDL_NOMOUSE'] = '1'
        
        # Initialize SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            print(f"SDL2 initialization failed: {sdl2.SDL_GetError().decode()}")
            return False
        
        # Create window
        self.window = sdl2.SDL_CreateWindow(
            b"Analog Clock",
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            self.width, self.height,
            sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN
        )
        
        if not self.window:
            print(f"Window creation failed: {sdl2.SDL_GetError().decode()}")
            sdl2.SDL_Quit()
            return False
        
        # Create renderer
        self.renderer = sdl2.SDL_CreateRenderer(
            self.window, -1,
            sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
        )
        
        if not self.renderer:
            print(f"Renderer creation failed: {sdl2.SDL_GetError().decode()}")
            sdl2.SDL_DestroyWindow(self.window)
            sdl2.SDL_Quit()
            return False
        
        return True
    
    def draw_circle_outline(self, x, y, radius, color):
        """Draw a circle outline using SDL2's built-in line drawing."""
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        
        # Use SDL2's line drawing for much better performance
        points = []
        for angle in range(0, 360, 2):  # Draw every 2 degrees for smooth circle
            rad = math.radians(angle)
            px = int(x + radius * math.cos(rad))
            py = int(y + radius * math.sin(rad))
            points.append((px, py))
        
        # Draw lines between consecutive points
        for i in range(len(points)):
            x1, y1 = points[i]
            x2, y2 = points[(i + 1) % len(points)]
            sdl2.SDL_RenderDrawLine(self.renderer, x1, y1, x2, y2)
    
    def draw_filled_circle_fast(self, x, y, radius, color):
        """Draw a filled circle using horizontal lines - much faster."""
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        
        # Draw horizontal lines to fill the circle
        for dy in range(-radius, radius + 1):
            dx = int(math.sqrt(max(0, radius * radius - dy * dy)))
            if dx > 0:
                sdl2.SDL_RenderDrawLine(self.renderer, x - dx, y + dy, x + dx, y + dy)
    
    def draw_line_simple(self, x1, y1, x2, y2, color):
        """Draw a simple line using SDL2."""
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderDrawLine(self.renderer, int(x1), int(y1), int(x2), int(y2))
    
    def draw_clock_face(self):
        """Draw the clock face with hour and minute marks - optimized version."""
        # Draw outer border with simple circle outline
        self.draw_circle_outline(self.center_x, self.center_y, self.clock_radius + 2, self.border_color)
        
        # Draw white clock face outline
        self.draw_circle_outline(self.center_x, self.center_y, self.clock_radius, self.face_color)
        
        # Draw hour marks (simple lines)
        for hour in range(12):
            angle = hour * math.pi / 6 - math.pi / 2  # 12 o'clock is at top
            
            # Outer point
            outer_x = self.center_x + (self.clock_radius - 20) * math.cos(angle)
            outer_y = self.center_y + (self.clock_radius - 20) * math.sin(angle)
            
            # Inner point  
            inner_x = self.center_x + (self.clock_radius - 50) * math.cos(angle)
            inner_y = self.center_y + (self.clock_radius - 50) * math.sin(angle)
            
            # Draw 3 lines for thickness (much faster than thick line function)
            for offset in range(-1, 2):
                self.draw_line_simple(outer_x + offset, outer_y, inner_x + offset, inner_y, self.hour_marks_color)
        
        # Draw minute marks (simple thin lines) - reduced frequency for performance
        for minute in range(0, 60, 5):  # Only every 5 minutes instead of all 60
            if minute % 15 != 0:  # Skip quarter hours to avoid overlapping with hour marks
                angle = minute * math.pi / 30 - math.pi / 2
                
                # Outer point
                outer_x = self.center_x + (self.clock_radius - 10) * math.cos(angle)
                outer_y = self.center_y + (self.clock_radius - 10) * math.sin(angle)
                
                # Inner point
                inner_x = self.center_x + (self.clock_radius - 25) * math.cos(angle)
                inner_y = self.center_y + (self.clock_radius - 25) * math.sin(angle)
                
                self.draw_line_simple(outer_x, outer_y, inner_x, inner_y, self.minute_marks_color)
    
    def draw_hand(self, angle, length, width, color):
        """Draw a clock hand at given angle - optimized version."""
        end_x = self.center_x + length * math.cos(angle)
        end_y = self.center_y + length * math.sin(angle)
        
        # Draw multiple lines for thickness (faster than thick line function)
        half_width = width // 2
        for offset in range(-half_width, half_width + 1):
            self.draw_line_simple(
                self.center_x + offset, self.center_y,
                end_x + offset, end_y, 
                color
            )
    
    def get_current_time_angles(self):
        """Calculate angles for clock hands based on current time."""
        now = datetime.now()
        
        # Get time components with microsecond precision for smooth second hand
        hours = now.hour % 12
        minutes = now.minute
        seconds = now.second + now.microsecond / 1000000.0
        
        # Calculate angles (12 o'clock is at -π/2, clockwise is positive)
        hour_angle = (hours + minutes/60 + seconds/3600) * math.pi / 6 - math.pi / 2
        minute_angle = (minutes + seconds/60) * math.pi / 30 - math.pi / 2
        second_angle = seconds * math.pi / 30 - math.pi / 2
        
        return hour_angle, minute_angle, second_angle
    
    def draw_clock(self):
        """Draw the complete analog clock."""
        # Clear background
        r, g, b = self.bg_color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        sdl2.SDL_RenderClear(self.renderer)
        
        # Draw clock face
        self.draw_clock_face()
        
        # Get current time angles
        hour_angle, minute_angle, second_angle = self.get_current_time_angles()
        
        # Draw hands (back to front: hour, minute, second)
        self.draw_hand(hour_angle, self.hour_hand_length, self.hour_hand_width, self.hour_hand_color)
        self.draw_hand(minute_angle, self.minute_hand_length, self.minute_hand_width, self.minute_hand_color)
        self.draw_hand(second_angle, self.second_hand_length, self.second_hand_width, self.second_hand_color)
        
        # Draw center dot
        self.draw_filled_circle_fast(self.center_x, self.center_y, self.center_dot_radius, self.center_dot_color)
    
    def handle_events(self):
        """Handle SDL2 events."""
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_ESCAPE or event.key.keysym.sym == sdl2.SDLK_q:
                    self.running = False
    
    def run(self):
        """Main clock loop."""
        if not self.setup_sdl2():
            return 1
        
        print("Analog Clock Started")
        print("Press 'q' or Ctrl+C to exit")
        
        try:
            while self.running:
                # Handle events
                self.handle_events()
                
                # Draw clock
                self.draw_clock()
                
                # Present to screen
                sdl2.SDL_RenderPresent(self.renderer)
                
                # Small delay for smooth animation (~60 FPS)
                sdl2.SDL_Delay(16)
                
        except KeyboardInterrupt:
            print("\nClock stopped by user")
        
        finally:
            self.cleanup()
        
        return 0
    
    def cleanup(self):
        """Clean up SDL2 resources."""
        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if self.window:
            sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

def main():
    """Main function."""
    print("SDL2 Analog Clock")
    print("=================")
    print("Clock: 700px diameter on 720x720px screen")
    print("Features: Smooth second hand, hour/minute marks")
    print("Exit: Press 'q' or Ctrl+C")
    print()
    
    clock = AnalogClock(width=720, height=720, clock_diameter=700)
    return clock.run()

if __name__ == '__main__':
    sys.exit(main())