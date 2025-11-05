#!/usr/bin/env python3
"""
Kivy program that draws a blue circle (600px diameter) centered on a 720x720px display.
Configured specifically for framebuffer/embedded display without X11.
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.config import Config
import os

# Environment variables for framebuffer rendering
os.environ['KIVY_WINDOW'] = 'sdl2'
os.environ['KIVY_GL_BACKEND'] = 'gl'
os.environ['SDL_VIDEODRIVER'] = 'fbcon'  # Use framebuffer console
os.environ['SDL_FBDEV'] = '/dev/fb0'     # Default framebuffer device

# Disable mouse cursor for embedded systems
os.environ['SDL_NOMOUSE'] = '1'

# Kivy configuration for framebuffer
Config.set('graphics', 'width', '720')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'borderless', '1')
Config.set('graphics', 'fullscreen', 'fake')
Config.set('graphics', 'show_cursor', '0')

# Input configuration
Config.set('input', 'mouse', 'mouse,disable_multitouch')


class CircleWidget(Widget):
    """Widget that draws a blue circle in the center."""
    
    def __init__(self, **kwargs):
        super(CircleWidget, self).__init__(**kwargs)
        
        # Bind to size changes to redraw when widget is resized
        self.bind(size=self.draw_circle, pos=self.draw_circle)
    
    def draw_circle(self, *args):
        """Draw a blue circle centered in the widget."""
        self.canvas.clear()
        
        with self.canvas:
            # Set color to blue (RGB values between 0 and 1)
            Color(0, 0, 1, 1)  # Blue color (red=0, green=0, blue=1, alpha=1)
            
            # Calculate center position for the circle
            # Circle diameter is 600px, so radius is 300px
            circle_diameter = 600
            circle_radius = circle_diameter / 2
            
            # Center the circle in the widget
            center_x = self.center_x - circle_radius
            center_y = self.center_y - circle_radius
            
            # Draw the circle (Ellipse with equal width and height)
            Ellipse(pos=(center_x, center_y), size=(circle_diameter, circle_diameter))


class CircleApp(App):
    """Main Kivy application."""
    
    def build(self):
        """Build and return the root widget."""
        self.title = "Blue Circle - 600px on 720x720px (Framebuffer)"
        return CircleWidget()


if __name__ == '__main__':
    # Print debug info
    print("Starting Kivy framebuffer application...")
    print(f"SDL_VIDEODRIVER: {os.environ.get('SDL_VIDEODRIVER', 'not set')}")
    print(f"SDL_FBDEV: {os.environ.get('SDL_FBDEV', 'not set')}")
    
    try:
        CircleApp().run()
    except Exception as e:
        print(f"Error running application: {e}")
        print("Make sure you have access to /dev/fb0 or run with appropriate permissions")