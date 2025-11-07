#!/usr/bin/env python3
"""
VU Meter Mode Switcher
======================

Simple script to test different VU meter modes and settings.
"""

import os
import sys
import subprocess
import time

def modify_vu_mode(mode, channel="left"):
    """Modify the VU_MODE setting in vu_meter.py"""
    
    # Read the file
    with open("vu_meter.py", "r") as f:
        content = f.read()
    
    # Replace VU_MODE setting
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('VU_MODE = '):
            lines[i] = f'VU_MODE = "{mode}"                  # "demo", "audio", or "fixed"'
        elif line.startswith('VU_CHANNEL = '):
            lines[i] = f'VU_CHANNEL = "{channel}"                # "left", "right", or "max" (for audio mode)'
    
    # Write back
    with open("vu_meter.py", "w") as f:
        f.write('\n'.join(lines))
    
    print(f"✓ Set VU_MODE to '{mode}' with channel '{channel}'")

def run_vu_meter(duration=10):
    """Run the VU meter for a specified duration"""
    try:
        print(f"Starting VU meter for {duration} seconds...")
        result = subprocess.run([
            "timeout", str(duration), "python3", "vu_meter.py"
        ], capture_output=False, text=True, timeout=duration + 2)
        print("VU meter stopped")
        return True
    except subprocess.TimeoutExpired:
        print("VU meter timed out")
        return True
    except KeyboardInterrupt:
        print("VU meter interrupted by user")
        return True
    except Exception as e:
        print(f"Error running VU meter: {e}")
        return False

def main():
    """Main test menu"""
    print("VU Meter Mode Test Script")
    print("=" * 30)
    
    while True:
        print("\nSelect VU Meter Mode:")
        print("1. Demo Mode (animated sweep)")
        print("2. Audio Mode - Left Channel")
        print("3. Audio Mode - Right Channel") 
        print("4. Audio Mode - Max (L/R)")
        print("5. Fixed Position")
        print("6. Exit")
        
        try:
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == "1":
                modify_vu_mode("demo")
                run_vu_meter(10)
            
            elif choice == "2":
                modify_vu_mode("audio", "left")
                run_vu_meter(15)
            
            elif choice == "3":
                modify_vu_mode("audio", "right")
                run_vu_meter(15)
            
            elif choice == "4":
                modify_vu_mode("audio", "max")
                run_vu_meter(15)
            
            elif choice == "5":
                modify_vu_mode("fixed")
                run_vu_meter(10)
            
            elif choice == "6":
                print("Exiting...")
                break
            
            else:
                print("Invalid choice. Please select 1-6.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("vu_meter.py"):
        print("Error: vu_meter.py not found in current directory")
        print("Please run this script from the same directory as vu_meter.py")
        sys.exit(1)
    
    main()