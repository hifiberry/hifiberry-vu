#!/usr/bin/env python3
"""
Basic SDL2 example for framebuffer rendering.
Demonstrates SDL2 setup and basic graphics operations.
"""

import sdl2
import sdl2.ext
import os
import sys
import time
import ctypes

def setup_framebuffer_rendering():
    """Configure SDL2 for framebuffer rendering."""
    # Set environment variables for framebuffer
    os.environ['SDL_VIDEODRIVER'] = 'KMSDRM'  # Kernel Mode Setting DRM
    os.environ['SDL_FBDEV'] = '/dev/fb0'
    os.environ['SDL_NOMOUSE'] = '1'
    
    print("SDL2 Framebuffer Configuration:")
    print(f"  Video Driver: {os.environ.get('SDL_VIDEODRIVER')}")
    print(f"  Framebuffer Device: {os.environ.get('SDL_FBDEV')}")

def create_sdl2_window(width=720, height=720):
    """Create SDL2 window and renderer."""
    
    # Initialize SDL2
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
        print(f"SDL2 initialization failed: {sdl2.SDL_GetError().decode()}")
        return None, None
    
    # Create window
    window = sdl2.SDL_CreateWindow(
        b"SDL2 Round Application",
        sdl2.SDL_WINDOWPOS_UNDEFINED,
        sdl2.SDL_WINDOWPOS_UNDEFINED,
        width, height,
        sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_FULLSCREEN
    )
    
    if not window:
        print(f"Window creation failed: {sdl2.SDL_GetError().decode()}")
        sdl2.SDL_Quit()
        return None, None
    
    # Create renderer
    renderer = sdl2.SDL_CreateRenderer(
        window, -1,
        sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC
    )
    
    if not renderer:
        print(f"Renderer creation failed: {sdl2.SDL_GetError().decode()}")
        sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()
        return None, None
    
    return window, renderer

def draw_test_pattern(renderer, width, height):
    """Draw a simple test pattern."""
    
    # Clear screen with black
    sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
    sdl2.SDL_RenderClear(renderer)
    
    # Draw colored rectangles
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green  
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
    ]
    
    rect_width = width // 3
    rect_height = height // 2
    
    for i, (r, g, b) in enumerate(colors):
        x = (i % 3) * rect_width
        y = (i // 3) * rect_height
        
        rect = sdl2.SDL_Rect(x, y, rect_width, rect_height)
        sdl2.SDL_SetRenderDrawColor(renderer, r, g, b, 255)
        sdl2.SDL_RenderFillRect(renderer, rect)
    
    # Draw white border
    sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
    border = sdl2.SDL_Rect(0, 0, width, height)
    sdl2.SDL_RenderDrawRect(renderer, border)

def main():
    """Main application."""
    
    print("SDL2 Basic Example")
    print("==================")
    
    # Setup framebuffer
    setup_framebuffer_rendering()
    
    # Create window and renderer
    window, renderer = create_sdl2_window()
    if not window or not renderer:
        return 1
    
    print("SDL2 window and renderer created successfully")
    print("Displaying test pattern for 5 seconds...")
    
    try:
        # Main loop
        start_time = time.time()
        running = True
        
        while running and (time.time() - start_time) < 5.0:
            # Handle events
            event = sdl2.SDL_Event()
            while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE:
                        running = False
            
            # Draw test pattern
            draw_test_pattern(renderer, 720, 720)
            
            # Present to screen
            sdl2.SDL_RenderPresent(renderer)
            
            # Small delay
            sdl2.SDL_Delay(16)  # ~60 FPS
        
        print("Test completed successfully!")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        if renderer:
            sdl2.SDL_DestroyRenderer(renderer)
        if window:
            sdl2.SDL_DestroyWindow(window)
        sdl2.SDL_Quit()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())