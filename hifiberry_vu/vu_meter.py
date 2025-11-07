#!/usr/bin/env python3
"""
VU Meter Display Application using SDL2
Features:
- Displays simple-vu.png image on 720x720px screen
- Overlay needle display at configurable position
- Needle positioned at 50%x, 72%y with 50% height length
- Needle range: -30° to +30° (0° is vertical)
- Demo mode: Animates needle min to max in 1 second
- Display rotation support (0°, 90°, 180°, 270°) - currently 180°
- FPS monitoring via console output
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
import argparse
from pathlib import Path

# Import VU monitoring module
try:
    from .python_vu import VUMonitor
    VU_AVAILABLE = True
except ImportError:
    try:
        from python_vu import VUMonitor
        VU_AVAILABLE = True
    except ImportError:
        print("Warning: VU audio monitoring not available (missing python_vu module)")
        VU_AVAILABLE = False

def get_image_path(filename):
    """Get the full path to an image file in the img directory."""
    # Try to find img directory relative to this file
    current_dir = Path(__file__).parent
    img_dir = current_dir.parent / "img"
    
    if img_dir.exists():
        return str(img_dir / filename)
    
    # Fallback: look in current working directory
    if Path("img" / filename).exists():
        return str(Path("img") / filename)
    
    # Last resort: return filename as-is
    return filename

# Configuration constants
CONFIGS = {
    "simple": {
        # Image settings
        "image_path": get_image_path("simple-vu.png"),
        
        # Needle position and appearance
        "needle_center_x_percent": 0.50,    # 50% of screen width
        "needle_center_y_percent": 0.72,    # 72% of screen height
        "needle_length_percent": 0.50,      # 50% of screen height
        "needle_min_angle": -35,             # Minimum angle in degrees
        "needle_max_angle": 18,              # Maximum angle in degrees
        "needle_width": 3,                   # Needle thickness in pixels
        "needle_color": (255, 0, 0),         # Red color (R, G, B)
        
        # VU level mapping
        "min_db": -20,                       # Minimum dB level for needle display
        "max_db": 6,                         # Maximum dB level for needle display
    },
    "simple2": {
        # Image settings
        "image_path": get_image_path("simple-vu2.png"),
        
        # Needle position and appearance
        "needle_center_x_percent": 0.50,    # 50% of screen width
        "needle_center_y_percent": 0.72,    # 72% of screen height
        "needle_length_percent": 0.50,      # 50% of screen height
        "needle_min_angle": -35,             # Minimum angle in degrees
        "needle_max_angle": 18,              # Maximum angle in degrees
        "needle_width": 3,                   # Needle thickness in pixels
        "needle_color": (255, 0, 0),         # Red color (R, G, B)
        
        # VU level mapping
        "min_db": -20,                       # Minimum dB level for needle display
        "max_db": 6,                         # Maximum dB level for needle display
    }
}

# Default settings (will be overridden by command line arguments)
DEFAULT_VU_MODE = "alsa"           # "demo" or "alsa"
DEFAULT_CONFIG = "simple"          # Configuration name
DEFAULT_ROTATE_ANGLE = 180         # Rotation angle: 0, 90, 180, or 270 degrees
DEFAULT_VU_CHANNEL = "left"        # "left", "right", "max", or "stereo" (for alsa mode)
DEFAULT_VU_UPDATE_RATE = 30        # VU level updates per second (for alsa mode)
DEFAULT_AVERAGE_READINGS = 5       # Number of readings to average for smoother display
DEFAULT_FPS_ENABLE = True          # FPS display

# Demo mode settings
NEEDLE_DEFAULT_ANGLE = -30         # Default fixed position in degrees (when mode = "fixed")
DEMO_SWEEP_TIME = 1.0              # Time in seconds to go from min to max angle

# Global variables (will be set by parse_arguments)
VU_MODE = DEFAULT_VU_MODE
CURRENT_CONFIG = DEFAULT_CONFIG
ROTATE_ANGLE = DEFAULT_ROTATE_ANGLE
VU_CHANNEL = DEFAULT_VU_CHANNEL
VU_UPDATE_RATE = DEFAULT_VU_UPDATE_RATE
AVERAGE_READINGS = DEFAULT_AVERAGE_READINGS
FPS_ENABLE = DEFAULT_FPS_ENABLE
CONFIG = None  # Will be set after argument parsing

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SDL2 VU Meter Display with ALSA Audio Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available configurations: {}

Examples:
  %(prog)s --mode=demo --config=simple --rotate=180
  %(prog)s --mode=alsa --config=simple --rotate=0
  %(prog)s --mode=alsa --channel=right --fps
        """.format(", ".join(CONFIGS.keys()))
    )
    
    parser.add_argument(
        "--mode", 
        choices=["demo", "alsa"], 
        default=DEFAULT_VU_MODE,
        help="VU meter mode: 'demo' for animated needle, 'alsa' for real audio input (default: %(default)s)"
    )
    
    parser.add_argument(
        "--config", 
        choices=list(CONFIGS.keys()), 
        default=DEFAULT_CONFIG,
        help="Configuration to use (default: %(default)s)"
    )
    
    parser.add_argument(
        "--rotate", 
        type=int, 
        choices=[0, 90, 180, 270], 
        default=DEFAULT_ROTATE_ANGLE,
        help="Display rotation angle in degrees (default: %(default)s)"
    )
    
    parser.add_argument(
        "--channel", 
        choices=["left", "right", "max", "stereo"], 
        default=DEFAULT_VU_CHANNEL,
        help="Audio channel for ALSA mode: 'left', 'right', 'max' for maximum of both, or 'stereo' for average of both (default: %(default)s)"
    )
    
    parser.add_argument(
        "--fps", 
        action="store_true", 
        default=DEFAULT_FPS_ENABLE,
        help="Enable FPS display on console (default: %(default)s)"
    )
    
    parser.add_argument(
        "--no-fps", 
        action="store_true",
        help="Disable FPS display on console"
    )
    
    parser.add_argument(
        "--update-rate", 
        type=int, 
        default=DEFAULT_VU_UPDATE_RATE,
        help="VU level update rate in Hz for ALSA mode (default: %(default)s)"
    )
    
    parser.add_argument(
        "--average-readings", 
        type=int, 
        default=DEFAULT_AVERAGE_READINGS,
        help="Number of VU readings to average for smoother display (default: %(default)s)"
    )
    
    parser.add_argument(
        "--list-configs", 
        action="store_true",
        help="List available configurations and exit"
    )
    
    args = parser.parse_args()
    
    # Handle --no-fps override
    if args.no_fps:
        args.fps = False
    
    return args

def initialize_settings(args):
    """Initialize global settings from command line arguments."""
    global VU_MODE, CURRENT_CONFIG, ROTATE_ANGLE, VU_CHANNEL, VU_UPDATE_RATE, AVERAGE_READINGS, FPS_ENABLE, CONFIG
    global DEMO_ANGLE_RANGE, DEMO_UPDATES_PER_SECOND, DEMO_STEP_SIZE
    
    VU_MODE = args.mode
    CURRENT_CONFIG = args.config
    ROTATE_ANGLE = args.rotate
    VU_CHANNEL = args.channel
    VU_UPDATE_RATE = args.update_rate
    AVERAGE_READINGS = args.average_readings
    FPS_ENABLE = args.fps
    
    # Set the configuration
    CONFIG = CONFIGS[CURRENT_CONFIG]
    
    # Calculate demo timing automatically based on config and sweep time (for demo mode)
    if VU_MODE == "demo":
        DEMO_ANGLE_RANGE = CONFIG["needle_max_angle"] - CONFIG["needle_min_angle"]
        DEMO_UPDATES_PER_SECOND = 60       # Smooth 60 FPS animation
        DEMO_STEP_SIZE = DEMO_ANGLE_RANGE / (DEMO_SWEEP_TIME * DEMO_UPDATES_PER_SECOND)
    else:
        DEMO_ANGLE_RANGE = 0
        DEMO_UPDATES_PER_SECOND = 60
        DEMO_STEP_SIZE = 0

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
        
        # VU audio monitoring
        self.vu_monitor = None
        if VU_MODE == "alsa" and VU_AVAILABLE:
            self.vu_monitor = VUMonitor(update_rate=VU_UPDATE_RATE)
        
        # VU reading averaging for smooth display
        from collections import deque
        self.vu_readings_buffer = deque(maxlen=AVERAGE_READINGS)
        
        # FPS tracking
        self.frame_count = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        self.fps_update_interval = 1.0  # Update FPS console output every second
    
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
    
    def update_needle_angle(self):
        """Update needle angle based on current VU mode."""
        if VU_MODE == "demo":
            return self._update_demo_needle()
        elif VU_MODE == "alsa":
            return self._update_audio_needle()
        else:
            return NEEDLE_DEFAULT_ANGLE
    
    def _update_demo_needle(self):
        """Update the demo needle position for animation."""
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
    
    def _update_audio_needle(self):
        """Update needle position based on audio VU levels."""
        if not self.vu_monitor or not self.vu_monitor.is_running():
            return NEEDLE_DEFAULT_ANGLE
        
        # Get VU levels from audio monitor
        left_db, right_db = self.vu_monitor.get_vu_levels()
        
        # Select channel based on VU_CHANNEL setting
        if VU_CHANNEL == "left":
            vu_db = left_db
        elif VU_CHANNEL == "right":
            vu_db = right_db
        elif VU_CHANNEL == "max":
            vu_db = max(left_db, right_db)
        elif VU_CHANNEL == "stereo":
            # Average the left and right channels (in linear space, then convert back to dB)
            # Convert dB to linear, average, then back to dB
            min_db_threshold = CONFIG["min_db"]
            left_linear = 10**(left_db / 20.0) if left_db > min_db_threshold else 0
            right_linear = 10**(right_db / 20.0) if right_db > min_db_threshold else 0
            avg_linear = (left_linear + right_linear) / 2.0
            vu_db = 20.0 * math.log10(avg_linear) if avg_linear > 0 else min_db_threshold
        else:
            vu_db = left_db  # Default to left
        
        # Add current reading to buffer for averaging
        self.vu_readings_buffer.append(vu_db)
        
        # Calculate average of recent readings
        if len(self.vu_readings_buffer) > 0:
            avg_vu_db = sum(self.vu_readings_buffer) / len(self.vu_readings_buffer)
        else:
            avg_vu_db = vu_db
        
        # Convert averaged VU dB level to needle angle using configurable dB range
        # VU range: min_db to max_db (from configuration)
        # Needle range: needle_min_angle to needle_max_angle
        min_db = CONFIG["min_db"]
        max_db = CONFIG["max_db"]
        vu_range = max_db - min_db  # Total VU range in dB
        vu_normalized = (avg_vu_db - min_db) / vu_range  # Normalize to 0.0-1.0
        vu_normalized = max(0.0, min(1.0, vu_normalized))  # Clamp
        
        # Map to needle angle range
        angle_range = CONFIG["needle_max_angle"] - CONFIG["needle_min_angle"]
        needle_angle = CONFIG["needle_min_angle"] + (vu_normalized * angle_range)
        
        return needle_angle
    
    def update_fps(self):
        """Update FPS calculation and print to console if enabled."""
        if not FPS_ENABLE:
            return
            
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= self.fps_update_interval:
            self.current_fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_start_time = current_time
            # Print FPS to console
            print(f"FPS: {self.current_fps:.1f}")
    

    
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
            
            # Update and draw needle (based on VU mode)
            needle_angle = self.update_needle_angle()
            self.draw_needle(needle_angle)
        else:
            # Draw placeholder VU meter
            self.draw_vu_placeholder()
            
            # Update and draw needle (based on VU mode)
            needle_angle = self.update_needle_angle()
            self.draw_needle(needle_angle)
    
    def handle_events(self):
        """Handle SDL2 events."""
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
            # Removed 'q' key exit - only Ctrl+C supported
    
    def cleanup(self):
        """Clean up SDL2 and VU monitor resources."""
        # Stop VU monitor
        if self.vu_monitor:
            self.vu_monitor.stop()
            self.vu_monitor = None
        
        # Clean up SDL2 resources
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
        
        # Start VU audio monitoring if enabled
        if self.vu_monitor:
            if self.vu_monitor.start():
                print(f"VU audio monitoring started - {VU_CHANNEL} channel")
            else:
                print("Failed to start VU audio monitoring - falling back to demo mode")
                self.vu_monitor = None
        
        print("VU Meter Display Started")
        print(f"VU Mode: {VU_MODE}")
        if VU_MODE == "demo":
            print("Demo needle animation enabled")
        elif VU_MODE == "alsa":
            if self.vu_monitor:
                print(f"ALSA VU monitoring enabled - {VU_CHANNEL} channel")
            else:
                print("ALSA VU monitoring failed - using fixed position")
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
                
                # Update FPS tracking
                self.update_fps()
                
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
    # Parse command line arguments
    args = parse_arguments()
    
    # Handle --list-configs
    if args.list_configs:
        print("Available configurations:")
        for config_name, config_data in CONFIGS.items():
            print(f"  {config_name}:")
            print(f"    Image: {config_data['image_path']}")
            print(f"    Needle: {config_data['needle_min_angle']}° to {config_data['needle_max_angle']}°")
            print(f"    Position: {config_data['needle_center_x_percent']*100:.0f}%x, {config_data['needle_center_y_percent']*100:.0f}%y")
            print()
        return 0
    
    # Initialize settings from arguments
    initialize_settings(args)
    
    print("SDL2 VU Meter Display")
    print("====================")
    print(f"Configuration: {CURRENT_CONFIG}")
    print(f"Looking for image: {CONFIG['image_path']}")
    print(f"VU Mode: {VU_MODE}")
    if VU_MODE == "demo":
        print(f"Demo: {CONFIG['needle_min_angle']}° to {CONFIG['needle_max_angle']}° in {DEMO_SWEEP_TIME}s ({DEMO_STEP_SIZE:.3f}°/step)")
    elif VU_MODE == "alsa":
        if VU_AVAILABLE:
            print(f"ALSA VU: {VU_CHANNEL} channel, {VU_UPDATE_RATE} updates/sec")
        else:
            print("ALSA VU: NOT AVAILABLE (missing dependencies) - falling back to demo mode")
    if FPS_ENABLE:
        print("FPS display enabled (console output)")
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