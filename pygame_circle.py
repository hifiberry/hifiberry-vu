#!/usr/bin/env python3
"""
Pygame version that draws a blue circle (600px diameter) centered on a 720x720px display.
Uses framebuffer directly without X11.
"""

import pygame
import os
import sys

def main():
    # Set environment variables for framebuffer
    os.environ['SDL_VIDEODRIVER'] = 'fbcon'
    os.environ['SDL_FBDEV'] = '/dev/fb0'
    os.environ['SDL_NOMOUSE'] = '1'
    
    print("Initializing Pygame with framebuffer...")
    print(f"SDL_VIDEODRIVER: {os.environ.get('SDL_VIDEODRIVER')}")
    print(f"SDL_FBDEV: {os.environ.get('SDL_FBDEV')}")
    
    try:
        # Initialize pygame
        pygame.init()
        
        # Set up the display - 720x720 pixels
        screen = pygame.display.set_mode((720, 720))
        pygame.display.set_caption("Blue Circle - Framebuffer")
        
        # Colors
        BLACK = (0, 0, 0)      # Background
        BLUE = (0, 0, 255)     # Circle color
        
        # Circle parameters
        screen_width, screen_height = 720, 720
        circle_diameter = 600
        circle_radius = circle_diameter // 2
        circle_center = (screen_width // 2, screen_height // 2)
        
        print(f"Screen size: {screen_width}x{screen_height}")
        print(f"Circle center: {circle_center}, radius: {circle_radius}")
        print("Drawing blue circle... Press Ctrl+C to exit")
        
        # Main loop
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                        running = False
            
            # Clear screen with black background
            screen.fill(BLACK)
            
            # Draw the blue circle
            pygame.draw.circle(screen, BLUE, circle_center, circle_radius)
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            clock.tick(60)
    
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have access to /dev/fb0 or run with appropriate permissions")
        return 1
    finally:
        pygame.quit()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())