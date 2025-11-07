#!/usr/bin/env python3
"""
VU Meter Display Application using SDL2
Features:
- Displays vu.png image on 720x720px screen
- Overlay needle display at configurable position
- Needle positioned at 50%x, 72%y with 50% height length
- Needle range: -30° to +30° (0° is vertical)
- Demo mode: Animates needle min to max in 1 second
- Display rotation support (0°, 90°, 180°, 270°) - currently 180°
- FPS display at configurable position
- Configuration system with predefined settings (currently: "simple")
- Exit with Ctrl+C only
"""

import sdl2
import sdl2.ext
import os
import sys
import math
import time
import ctypes

# Configuration constants
CONFIGS = {
    "simple": {
        # Image settings
        "image_path": "vu.png",
        
        # Needle position and appearance
        "needle_center_x_percent": 0.50,    # 50% of screen width
        "needle_center_y_percent": 0.72,    # 72% of screen height
        "needle_length_percent": 0.50,      # 50% of screen height
        "needle_min_angle": -40,             # Minimum angle in degrees
        "needle_max_angle": 40,              # Maximum angle in degrees
        "needle_width": 3,                   # Needle thickness in pixels
        "needle_color": (255, 0, 0),         # Red color (R, G, B)
        
        # FPS display settings
        "fps_position_y_percent": 0.80,      # 80% of screen height
    }
}

# Demo mode settings (separate from config)
NEEDLE_DEFAULT_ANGLE = -30         # Default fixed position in degrees
DEMO_NEEDLE = True                 # Set to False to disable demo mode
DEMO_SWEEP_TIME = 1.0              # Time in seconds to go from min to max angle

# FPS display settings (global)
FPS_ENABLE = False                  # Set to False to disable FPS display

# Display rotation (global)
ROTATE_ANGLE = 180                 # Rotation angle: 0, 90, 180, or 270 degrees

# Select configuration
CURRENT_CONFIG = "simple"
CONFIG = CONFIGS[CURRENT_CONFIG]

# Calculate demo timing automatically based on config and sweep time
DEMO_ANGLE_RANGE = CONFIG["needle_max_angle"] - CONFIG["needle_min_angle"]
DEMO_UPDATES_PER_SECOND = 60       # Smooth 60 FPS animation
DEMO_STEP_SIZE = DEMO_ANGLE_RANGE / (DEMO_SWEEP_TIME * DEMO_UPDATES_PER_SECOND)

class VUMeter:
    def __init__(self, width=720, height=720):
        self.width = width
        self.height = height
        
        self.window = None
        self.renderer = None
        self.texture = None
        self.running = True
        
        # Demo needle state
        self.current_needle_angle = CONFIG["needle_min_angle"]
        self.needle_direction = 1  # 1 for increasing, -1 for decreasing
        self.last_needle_update = 0
        
        # FPS tracking
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        self.fps_update_interval = 1.0  # Update FPS display every second
    
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
            b"VU Meter",
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
    
    def load_image(self, image_path):
        """Load PNG image as texture."""
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return False
        
        try:
            # Try to initialize SDL_image
            import sdl2.sdlimage as sdlimage
            
            if sdlimage.IMG_Init(sdlimage.IMG_INIT_PNG) == 0:
                print(f"SDL_image PNG support initialization failed: {sdl2.SDL_GetError().decode()}")
                return False
            
            # Load surface
            surface = sdlimage.IMG_Load(image_path.encode('utf-8'))
            if not surface:
                print(f"Failed to load image: {image_path}")
                print(f"SDL Error: {sdl2.SDL_GetError().decode()}")
                sdlimage.IMG_Quit()
                return False
            
            # Create texture from surface
            self.texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, surface)
            sdl2.SDL_FreeSurface(surface)
            sdlimage.IMG_Quit()
            
            if not self.texture:
                print(f"Failed to create texture from image: {sdl2.SDL_GetError().decode()}")
                return False
            
            print(f"Successfully loaded: {image_path}")
            return True
            
        except ImportError:
            print("SDL_image not available. Install python3-sdl2 with image support or libsdl2-image")
            return False
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def draw_needle(self, angle_degrees):
        """Draw the VU meter needle at the specified angle.
        
        Args:
            angle_degrees: Angle in degrees (-20 to +20, where 0 is vertical)
        """
        # Clamp angle to valid range
        angle_degrees = max(CONFIG["needle_min_angle"], min(CONFIG["needle_max_angle"], angle_degrees))
        
        # Calculate needle center position
        needle_center_x = int(self.width * CONFIG["needle_center_x_percent"])
        needle_center_y = int(self.height * CONFIG["needle_center_y_percent"])
        
        # Calculate needle length
        needle_length = int(self.height * CONFIG["needle_length_percent"])
        
        # Convert angle to radians (0 degrees = vertical = -90 degrees in math coords)
        # Subtract 90 degrees to make 0 degrees point upward (vertical)
        angle_rad = math.radians(angle_degrees - 90)
        
        # Calculate needle end point
        end_x = int(needle_center_x + needle_length * math.cos(angle_rad))
        end_y = int(needle_center_y + needle_length * math.sin(angle_rad))
        
        # Apply rotation to coordinates
        needle_center_x, needle_center_y = self.rotate_coordinates(needle_center_x, needle_center_y)
        end_x, end_y = self.rotate_coordinates(end_x, end_y)
        
        # Set needle color
        r, g, b = CONFIG["needle_color"]
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        
        # Draw needle with specified thickness
        for offset in range(-CONFIG["needle_width"]//2, CONFIG["needle_width"]//2 + 1):
            # Draw multiple lines to create thickness
            sdl2.SDL_RenderDrawLine(
                self.renderer,
                needle_center_x + offset, needle_center_y,
                end_x + offset, end_y
            )
            sdl2.SDL_RenderDrawLine(
                self.renderer,
                needle_center_x, needle_center_y + offset,
                end_x, end_y + offset
            )
        
        # Draw center dot
        center_dot_size = 5
        for dx in range(-center_dot_size, center_dot_size + 1):
            for dy in range(-center_dot_size, center_dot_size + 1):
                if dx*dx + dy*dy <= center_dot_size*center_dot_size:
                    sdl2.SDL_RenderDrawPoint(self.renderer, 
                                           needle_center_x + dx, 
                                           needle_center_y + dy)
    
    def update_demo_needle(self):
        """Update the demo needle position for animation."""
        if not DEMO_NEEDLE:
            return NEEDLE_DEFAULT_ANGLE
        
        current_time = time.time()
        
        # Check if it's time to update (based on DEMO_UPDATES_PER_SECOND)
        update_interval = 1.0 / DEMO_UPDATES_PER_SECOND
        if current_time - self.last_needle_update >= update_interval:
            self.last_needle_update = current_time
            
            # Update needle position
            self.current_needle_angle += self.needle_direction * DEMO_STEP_SIZE
            
            # Check bounds and reverse direction if needed
            if self.current_needle_angle >= CONFIG["needle_max_angle"]:
                self.current_needle_angle = CONFIG["needle_max_angle"]
                self.needle_direction = -1  # Start going back
            elif self.current_needle_angle <= CONFIG["needle_min_angle"]:
                self.current_needle_angle = CONFIG["needle_min_angle"]
                self.needle_direction = 1   # Start going forward
        
        return self.current_needle_angle
    
    def update_fps(self):
        """Update FPS calculation."""
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= self.fps_update_interval:
            self.current_fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = current_time
    
    def draw_simple_digit(self, x, y, digit, color, size=3):
        """Draw a simple bitmap digit."""
        r, g, b = color
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, 255)
        
        # Simple 5x7 bitmap patterns for digits 0-9
        patterns = {
            '0': ["11111", "10001", "10001", "10001", "10001", "10001", "11111"],
            '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
            '2': ["11111", "00001", "00001", "11111", "10000", "10000", "11111"],
            '3': ["11111", "00001", "00001", "11111", "00001", "00001", "11111"],
            '4': ["10001", "10001", "10001", "11111", "00001", "00001", "00001"],
            '5': ["11111", "10000", "10000", "11111", "00001", "00001", "11111"],
            '6': ["11111", "10000", "10000", "11111", "10001", "10001", "11111"],
            '7': ["11111", "00001", "00001", "00001", "00001", "00001", "00001"],
            '8': ["11111", "10001", "10001", "11111", "10001", "10001", "11111"],
            '9': ["11111", "10001", "10001", "11111", "00001", "00001", "11111"],
            '.': ["00000", "00000", "00000", "00000", "00000", "00000", "01100"]
        }
        
        if digit not in patterns:
            return
        
        pattern = patterns[digit]
        
        for row, line in enumerate(pattern):
            for col, pixel in enumerate(line):
                if pixel == '1':
                    # Draw a size x size block for each pixel
                    for dx in range(size):
                        for dy in range(size):
                            px = x + col * size + dx
                            py = y + row * size + dy
                            # Apply rotation to text pixels based on ROTATE_ANGLE
                            if ROTATE_ANGLE == 0:
                                final_x, final_y = px, py
                            elif ROTATE_ANGLE == 90:
                                # Rotate 90° around the character center
                                char_center_x = x + 2.5 * size
                                char_center_y = y + 3.5 * size  
                                rel_x = px - char_center_x
                                rel_y = py - char_center_y
                                final_x = int(char_center_x - rel_y)
                                final_y = int(char_center_y + rel_x)
                            elif ROTATE_ANGLE == 180:
                                # Rotate 180° around the character center
                                char_center_x = x + 2.5 * size
                                char_center_y = y + 3.5 * size
                                rel_x = px - char_center_x
                                rel_y = py - char_center_y
                                final_x = int(char_center_x - rel_x)
                                final_y = int(char_center_y - rel_y)
                            elif ROTATE_ANGLE == 270:
                                # Rotate 270° around the character center
                                char_center_x = x + 2.5 * size
                                char_center_y = y + 3.5 * size
                                rel_x = px - char_center_x
                                rel_y = py - char_center_y
                                final_x = int(char_center_x + rel_y)
                                final_y = int(char_center_y - rel_x)
                            else:
                                final_x, final_y = px, py
                            
                            sdl2.SDL_RenderDrawPoint(self.renderer, final_x, final_y)
    
    def draw_text(self, x, y, text, color, size=3):
        """Draw simple text using bitmap digits."""
        char_width = 6 * size  # 5 pixels + 1 spacing
        current_x = x
        
        for char in text:
            self.draw_simple_digit(current_x, y, char, color, size)
            current_x += char_width
    
    def draw_fps_display(self):
        """Draw the FPS display if enabled."""
        if not FPS_ENABLE:
            return
        
        self.update_fps()
        fps_text = f"{self.current_fps:.1f}"
        
        # Calculate position based on rotation
        text_width = len(fps_text) * 6 * 3  # 6 pixels per char * size 3
        
        if ROTATE_ANGLE == 0:
            # Normal: bottom center
            text_x = self.width // 2 - text_width // 2
            text_y = int(self.height * CONFIG["fps_position_y_percent"])
        elif ROTATE_ANGLE == 90:
            # 90° rotation: right side, vertically centered
            text_x = int(self.width * CONFIG["fps_position_y_percent"])
            text_y = self.height // 2 - (len(fps_text) * 7 * 3) // 2  # Approximate text height
        elif ROTATE_ANGLE == 180:
            # 180° rotation: top center
            text_x = self.width // 2 - text_width // 2
            text_y = int(self.height * (1.0 - CONFIG["fps_position_y_percent"]))
        elif ROTATE_ANGLE == 270:
            # 270° rotation: left side, vertically centered
            text_x = int(self.width * (1.0 - CONFIG["fps_position_y_percent"]))
            text_y = self.height // 2 - (len(fps_text) * 7 * 3) // 2  # Approximate text height
        else:
            # Default to normal position
            text_x = self.width // 2 - text_width // 2
            text_y = int(self.height * CONFIG["fps_position_y_percent"])
        
        self.draw_text(text_x, text_y, fps_text, (0, 255, 0), size=3)  # Green text
    
    def rotate_coordinates(self, x, y):
        """Rotate coordinates based on ROTATE_ANGLE."""
        if ROTATE_ANGLE == 0:
            return x, y
        elif ROTATE_ANGLE == 90:
            return self.height - y, x
        elif ROTATE_ANGLE == 180:
            return self.width - x, self.height - y
        elif ROTATE_ANGLE == 270:
            return y, self.width - x
        else:
            # Invalid rotation angle, return original coordinates
            return x, y
    
    def draw_vu_placeholder(self):
        """Draw a simple VU meter placeholder."""
        # Clear background with black
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        sdl2.SDL_RenderClear(self.renderer)
        
        # Draw a simple VU meter representation
        center_x = self.width // 2
        center_y = self.height // 2
        
        # Draw outer circle (VU meter face)
        sdl2.SDL_SetRenderDrawColor(self.renderer, 100, 100, 100, 255)
        radius = 200
        for angle in range(0, 360, 2):
            rad = 3.14159 * angle / 180
            x = int(center_x + radius * math.cos(rad))
            y = int(center_y + radius * math.sin(rad))
            sdl2.SDL_RenderDrawPoint(self.renderer, x, y)
        
        # Draw scale marks
        sdl2.SDL_SetRenderDrawColor(self.renderer, 150, 150, 150, 255)
        for i in range(-90, 91, 15):  # -90 to +90 degrees, every 15 degrees
            angle_rad = 3.14159 * i / 180
            x1 = int(center_x + (radius - 20) * math.cos(angle_rad))
            y1 = int(center_y + (radius - 20) * math.sin(angle_rad))
            x2 = int(center_x + (radius - 10) * math.cos(angle_rad))
            y2 = int(center_y + (radius - 10) * math.sin(angle_rad))
            sdl2.SDL_RenderDrawLine(self.renderer, x1, y1, x2, y2)
        
        # Draw needle (pointing to -20 dB)
        needle_angle = -3.14159 * 45 / 180  # -45 degrees
        sdl2.SDL_SetRenderDrawColor(self.renderer, 255, 0, 0, 255)
        needle_x = int(center_x + (radius - 30) * math.cos(needle_angle))
        needle_y = int(center_y + (radius - 30) * math.sin(needle_angle))
        sdl2.SDL_RenderDrawLine(self.renderer, center_x, center_y, needle_x, needle_y)
        
        # Draw center dot
        for x in range(center_x - 3, center_x + 4):
            for y in range(center_y - 3, center_y + 4):
                sdl2.SDL_RenderDrawPoint(self.renderer, x, y)
        
        # Draw "VU METER" text using simple lines
        sdl2.SDL_SetRenderDrawColor(self.renderer, 255, 255, 255, 255)
        text_y = center_y + radius + 30
        
        # Simple text: "NO IMAGE - VU PLACEHOLDER"
        # Draw a simple rectangle with text indication
        rect_x = center_x - 100
        rect_y = text_y
        for x in range(rect_x, rect_x + 200):
            sdl2.SDL_RenderDrawPoint(self.renderer, x, rect_y)
            sdl2.SDL_RenderDrawPoint(self.renderer, x, rect_y + 20)
        for y in range(rect_y, rect_y + 21):
            sdl2.SDL_RenderDrawPoint(self.renderer, rect_x, y)
            sdl2.SDL_RenderDrawPoint(self.renderer, rect_x + 199, y)
    
    def draw_vu_meter(self):
        """Draw the VU meter image or placeholder."""
        if self.texture:
            # Clear background with black
            sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
            sdl2.SDL_RenderClear(self.renderer)
            
            # Get texture dimensions
            texture_format = ctypes.c_uint32()
            texture_access = ctypes.c_int()
            texture_width = ctypes.c_int()
            texture_height = ctypes.c_int()
            
            sdl2.SDL_QueryTexture(
                self.texture,
                ctypes.byref(texture_format),
                ctypes.byref(texture_access),
                ctypes.byref(texture_width),
                ctypes.byref(texture_height)
            )
            
            # Calculate position to center the image
            x = (self.width - texture_width.value) // 2
            y = (self.height - texture_height.value) // 2
            
            # Create destination rectangle
            dest_rect = sdl2.SDL_Rect(x, y, texture_width.value, texture_height.value)
            
            # Render texture with rotation
            center_point = sdl2.SDL_Point(texture_width.value // 2, texture_height.value // 2)
            sdl2.SDL_RenderCopyEx(
                self.renderer, 
                self.texture, 
                None, 
                dest_rect, 
                ROTATE_ANGLE,  # Rotation angle
                center_point,  # Center point for rotation
                sdl2.SDL_FLIP_NONE  # No flipping
            )
            
            # Update and draw needle (demo mode or fixed position)
            needle_angle = self.update_demo_needle()
            self.draw_needle(needle_angle)
            
            # Draw FPS display
            self.draw_fps_display()
        else:
            # Draw placeholder VU meter
            self.draw_vu_placeholder()
            
            # Update and draw needle (demo mode or fixed position)
            needle_angle = self.update_demo_needle()
            self.draw_needle(needle_angle)
            
            # Draw FPS display
            self.draw_fps_display()
    
    def handle_events(self):
        """Handle SDL2 events."""
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
            # Removed 'q' key exit - only Ctrl+C supported
    
    def cleanup(self):
        """Clean up SDL2 resources."""
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)
        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if self.window:
            sdl2.SDL_DestroyWindow(self.window)
        sdl2.ext.quit()
        sdl2.SDL_Quit()
    
    def run(self):
        """Main VU meter loop."""
        if not self.setup_sdl2():
            return 1
        
        # Try to load image, but continue even if it fails
        image_loaded = self.load_image(CONFIG["image_path"])
        if not image_loaded:
            print("Image loading failed - showing placeholder VU meter")
        
        print("VU Meter Display Started")
        if DEMO_NEEDLE:
            print("Demo needle animation enabled")
        print("Press Ctrl+C to exit")
        
        # Initialize demo needle timing
        self.last_needle_update = time.time()
        
        # Initialize FPS tracking
        self.fps_start_time = time.time()
        self.frame_count = 0
        
        try:
            while self.running:
                # Handle events
                self.handle_events()
                
                # Draw VU meter
                self.draw_vu_meter()
                
                # Present to screen
                sdl2.SDL_RenderPresent(self.renderer)
                
                # Small delay to prevent excessive CPU usage
                sdl2.SDL_Delay(16)  # ~60 FPS
                
        except KeyboardInterrupt:
            print("\nVU Meter stopped by user")
        
        finally:
            self.cleanup()
        
        return 0

def set_config(config_name):
    """Switch to a different configuration."""
    global CURRENT_CONFIG, CONFIG
    
    if config_name not in CONFIGS:
        print(f"Error: Configuration '{config_name}' not found.")
        print(f"Available configurations: {list(CONFIGS.keys())}")
        return False
    
    CURRENT_CONFIG = config_name
    CONFIG = CONFIGS[config_name]
    
    print(f"Switched to configuration: {config_name}")
    return True

def main():
    """Main entry point."""
    print("SDL2 VU Meter Display")
    print("====================")
    print(f"Configuration: {CURRENT_CONFIG}")
    print(f"Looking for image: {CONFIG['image_path']}")
    if DEMO_NEEDLE:
        print(f"Demo: {CONFIG['needle_min_angle']}° to {CONFIG['needle_max_angle']}° in {DEMO_SWEEP_TIME}s ({DEMO_STEP_SIZE:.3f}°/step)")
    if FPS_ENABLE:
        print(f"FPS display enabled at {CONFIG['fps_position_y_percent']*100}% height")
    print(f"Display rotation: {ROTATE_ANGLE}°")
    print("Exit: Press Ctrl+C")
    print()
    
    try:
        vu_meter = VUMeter()
        return vu_meter.run()
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())