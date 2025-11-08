#!/usr/bin/env python3
"""
Quick test script for the song detection tool.

This script provides a simple way to test if all components are working:
- PyAudio for audio recording
- Chromaprint (fpcalc) for fingerprinting
- AcoustID API for song identification

Usage:
    python3 test_song_detection.py
"""

import sys
import subprocess

def check_pyaudio():
    """Check if PyAudio is installed."""
    try:
        import pyaudio
        print("✓ PyAudio is installed")
        
        # Test opening PyAudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"✓ Found {device_count} audio devices")
        
        # List audio input devices
        print("\nAvailable input devices:")
        for i in range(device_count):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  [{i}] {info['name']}")
                print(f"      Max Channels: {info['maxInputChannels']}")
                print(f"      Sample Rate: {info['defaultSampleRate']} Hz")
        
        p.terminate()
        return True
        
    except ImportError:
        print("✗ PyAudio is not installed")
        print("  Install with: pip install pyaudio")
        return False
    except Exception as e:
        print(f"✗ PyAudio error: {e}")
        return False


def check_numpy():
    """Check if NumPy is installed."""
    try:
        import numpy
        print(f"✓ NumPy is installed (version {numpy.__version__})")
        return True
    except ImportError:
        print("✗ NumPy is not installed")
        print("  Install with: pip install numpy")
        return False


def check_requests():
    """Check if requests is installed."""
    try:
        import requests
        print(f"✓ requests is installed (version {requests.__version__})")
        return True
    except ImportError:
        print("✗ requests is not installed")
        print("  Install with: pip install requests")
        return False


def check_fpcalc():
    """Check if fpcalc (Chromaprint) is installed."""
    try:
        result = subprocess.run(
            ['fpcalc', '-version'],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print(f"✓ fpcalc is installed ({version})")
        return True
        
    except FileNotFoundError:
        print("✗ fpcalc (Chromaprint) is not installed")
        print("  Install with: sudo apt-get install libchromaprint-tools")
        return False
    except Exception as e:
        print(f"✗ fpcalc error: {e}")
        return False


def check_acoustid_module():
    """Check if the AcoustID module is available."""
    try:
        from hifiberry_vu.acoustid import AcoustIDClient
        print("✓ AcoustID module is available")
        return True
    except ImportError:
        try:
            from acoustid import AcoustIDClient
            print("✓ AcoustID module is available")
            return True
        except ImportError:
            print("✗ AcoustID module not found")
            print("  Make sure acoustid.py is in hifiberry_vu/")
            return False


def test_api_key():
    """Prompt for API key."""
    print("\n" + "="*60)
    print("API Key Check")
    print("="*60)
    print("\nTo use the song detection tool, you need an AcoustID API key.")
    print("Get one at: https://acoustid.org/new-application")
    print("\nOnce you have your API key, run the detection tool like this:")
    print("  python3 detect_song.py --api-key YOUR_API_KEY")
    print("\nFor continuous monitoring:")
    print("  python3 detect_song.py --api-key YOUR_API_KEY --continuous")


def main():
    """Run all checks."""
    print("="*60)
    print("Song Detection Tool - System Check")
    print("="*60)
    print()
    
    all_ok = True
    
    # Check Python packages
    print("Checking Python packages...")
    all_ok &= check_pyaudio()
    all_ok &= check_numpy()
    all_ok &= check_requests()
    all_ok &= check_acoustid_module()
    
    print()
    
    # Check system tools
    print("Checking system tools...")
    all_ok &= check_fpcalc()
    
    print()
    print("="*60)
    
    if all_ok:
        print("✓ All components are installed!")
        test_api_key()
    else:
        print("✗ Some components are missing. Please install them.")
        print("\nQuick installation:")
        print("  sudo apt-get install libchromaprint-tools")
        print("  pip install pyaudio numpy requests")
    
    print("="*60)


if __name__ == '__main__':
    main()
