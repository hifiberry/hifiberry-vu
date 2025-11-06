#!/usr/bin/env python3
"""
SDL2 Installation Test Script
Tests SDL2 functionality and lists available video drivers.
"""

import sys
import os

def test_sdl2_import():
    """Test if SDL2 can be imported."""
    try:
        import sdl2
        import sdl2.ext
        print("✅ SDL2 Python bindings imported successfully")
        
        # Try different ways to get version info
        try:
            print(f"   PySDL2 version: {sdl2.version.version}")
        except AttributeError:
            try:
                print(f"   PySDL2 version: {sdl2.__version__}")
            except AttributeError:
                print("   PySDL2 version: (version info not available)")
        
        try:
            sdl_version = sdl2.version.SDL_GetVersion()
            print(f"   SDL2 version: {sdl_version.major}.{sdl_version.minor}.{sdl_version.patch}")
        except Exception:
            print("   SDL2 version: (version info not available)")
            
        return True
    except ImportError as e:
        print(f"❌ Failed to import SDL2: {e}")
        return False

def test_sdl2_init():
    """Test SDL2 initialization."""
    try:
        import sdl2
        
        # Initialize SDL2
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
            print(f"❌ SDL2 initialization failed: {sdl2.SDL_GetError()}")
            return False
        
        print("✅ SDL2 initialized successfully")
        
        # Get number of video drivers
        num_drivers = sdl2.SDL_GetNumVideoDrivers()
        print(f"   Available video drivers: {num_drivers}")
        
        # List all video drivers
        for i in range(num_drivers):
            driver_name = sdl2.SDL_GetVideoDriver(i).decode('utf-8')
            print(f"   - {driver_name}")
        
        # Get current video driver
        current_driver = sdl2.SDL_GetCurrentVideoDriver()
        if current_driver:
            print(f"   Current driver: {current_driver.decode('utf-8')}")
        else:
            print("   No video driver currently active")
        
        # Cleanup
        sdl2.SDL_Quit()
        return True
        
    except Exception as e:
        print(f"❌ SDL2 initialization test failed: {e}")
        return False

def test_framebuffer_access():
    """Test if framebuffer is accessible."""
    fb_devices = ['/dev/fb0', '/dev/fb1']
    
    print("\nFramebuffer Device Check:")
    for fb_dev in fb_devices:
        if os.path.exists(fb_dev):
            try:
                with open(fb_dev, 'r+b') as fb:
                    print(f"✅ {fb_dev} is accessible")
                    
                    # Try to get framebuffer info
                    try:
                        with open(f'/sys/class/graphics/{os.path.basename(fb_dev)}/virtual_size', 'r') as f:
                            size = f.read().strip()
                            print(f"   Resolution: {size}")
                        
                        with open(f'/sys/class/graphics/{os.path.basename(fb_dev)}/bits_per_pixel', 'r') as f:
                            bpp = f.read().strip()
                            print(f"   Color depth: {bpp} bpp")
                            
                    except Exception as e:
                        print(f"   Could not read framebuffer info: {e}")
                        
            except PermissionError:
                print(f"⚠️  {fb_dev} exists but access denied (try: sudo usermod -a -G video $USER)")
            except Exception as e:
                print(f"❌ Error accessing {fb_dev}: {e}")
        else:
            print(f"❌ {fb_dev} not found")

def test_environment_variables():
    """Check relevant environment variables."""
    print("\nEnvironment Variables:")
    
    env_vars = [
        'SDL_VIDEODRIVER',
        'SDL_FBDEV', 
        'DISPLAY',
        'WAYLAND_DISPLAY'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        print(f"   {var}: {value}")

def main():
    """Run all SDL2 tests."""
    print("SDL2 Installation Test")
    print("=====================")
    print()
    
    # Test imports
    if not test_sdl2_import():
        print("\n❌ SDL2 not properly installed. Run: sudo ./install-sdl2")
        return 1
    
    print()
    
    # Test initialization
    if not test_sdl2_init():
        print("\n❌ SDL2 initialization failed")
        return 1
    
    # Test framebuffer
    test_framebuffer_access()
    
    # Check environment
    test_environment_variables()
    
    print("\n🎉 SDL2 installation test completed!")
    print("\nRecommended next steps:")
    print("1. For framebuffer rendering:")
    print("   export SDL_VIDEODRIVER=fbcon")
    print("   export SDL_FBDEV=/dev/fb0")
    print("2. Test vinyl record with SDL2:")
    print("   python3 ../vinyl_with_sdl2.py")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())