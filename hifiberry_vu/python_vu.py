#!/usr/bin/env python3
"""
Python VU Module - ALSA Audio Recording and VU Level Calculation
================================================================

This module records audio from ALSA and calculates VU (Volume Unit) levels
for left and right channels at configurable intervals.

Features:
- ALSA audio recording using pyaudio
- Real-time VU level calculation (RMS-based)
- Configurable sample rate and update frequency
- Thread-safe operation
- Left/right channel separation
- VU levels in dB scale (-60 to +6 dB range)

Dependencies:
- pyaudio (pip install pyaudio)
- numpy (pip install numpy)

Usage:
    vu_monitor = VUMonitor()
    vu_monitor.start()
    
    # Get current VU levels
    left_db, right_db = vu_monitor.get_vu_levels()
    
    vu_monitor.stop()
"""

import pyaudio
import numpy as np
import threading
import time
import math
from collections import deque


class VUMonitor:
    """
    ALSA Audio VU Level Monitor
    
    Records audio from the default ALSA input device and calculates
    VU levels for left and right channels in real-time.
    """
    
    def __init__(self, 
                 sample_rate=44100,
                 chunk_size=1024,
                 channels=2,
                 update_rate=10,
                 device_index=None):
        """
        Initialize VU Monitor
        
        Args:
            sample_rate (int): Audio sample rate in Hz (default: 44100)
            chunk_size (int): Audio buffer size in samples (default: 1024)
            channels (int): Number of audio channels (default: 2 for stereo)
            update_rate (int): VU level updates per second (default: 10)
            device_index (int): ALSA device index (None for default)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.update_rate = update_rate
        self.device_index = device_index
        
        # Audio stream objects
        self.audio = None
        self.stream = None
        
        # Threading
        self.recording_thread = None
        self.running = False
        self.lock = threading.Lock()
        
        # VU level storage
        self.left_vu_db = -60.0   # Start at minimum level
        self.right_vu_db = -60.0  # Start at minimum level
        
        # Audio buffer for VU calculation
        self.audio_buffer = deque(maxlen=int(sample_rate * 0.3))  # 300ms buffer
        
        # VU calculation timing
        self.last_vu_update = 0
        self.vu_update_interval = 1.0 / update_rate
        
        # VU constants
        self.VU_MIN_DB = -60.0    # Minimum VU level in dB
        self.VU_MAX_DB = 6.0      # Maximum VU level in dB
        self.VU_REFERENCE = 0.707  # 0 dB VU reference level (RMS)
    
    def list_audio_devices(self):
        """List available ALSA audio input devices."""
        if not self.audio:
            self.audio = pyaudio.PyAudio()
        
        print("Available ALSA Audio Input Devices:")
        print("=" * 40)
        
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:  # Only input devices
                print(f"Device {i}: {info['name']}")
                print(f"  Channels: {info['maxInputChannels']}")
                print(f"  Sample Rate: {info['defaultSampleRate']}")
                print(f"  Host API: {self.audio.get_host_api_info_by_index(info['hostApi'])['name']}")
                print()
    
    def start(self):
        """Start audio recording and VU monitoring."""
        if self.running:
            print("VU Monitor already running")
            return False
        
        try:
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Find default input device if not specified
            if self.device_index is None:
                self.device_index = self.audio.get_default_input_device_info()['index']
            
            # Get device info
            device_info = self.audio.get_device_info_by_index(self.device_index)
            print(f"Using audio device: {device_info['name']}")
            
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            # Start recording
            self.running = True
            self.stream.start_stream()
            
            # Start VU calculation thread
            self.recording_thread = threading.Thread(target=self._vu_calculation_loop)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            print(f"VU Monitor started - {self.update_rate} updates/sec")
            return True
            
        except Exception as e:
            print(f"Error starting VU Monitor: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop audio recording and VU monitoring."""
        self.running = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
        
        if self.recording_thread:
            self.recording_thread.join(timeout=1.0)
            self.recording_thread = None
        
        print("VU Monitor stopped")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for incoming audio data."""
        if status:
            print(f"Audio callback status: {status}")
        
        # Convert audio data to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        
        # Add to buffer for VU calculation
        with self.lock:
            self.audio_buffer.extend(audio_data)
        
        return (None, pyaudio.paContinue)
    
    def _vu_calculation_loop(self):
        """Background thread for VU level calculation."""
        while self.running:
            current_time = time.time()
            
            # Check if it's time for VU update
            if current_time - self.last_vu_update >= self.vu_update_interval:
                self._calculate_vu_levels()
                self.last_vu_update = current_time
            
            # Small sleep to prevent excessive CPU usage
            time.sleep(0.01)
    
    def _calculate_vu_levels(self):
        """Calculate VU levels for left and right channels."""
        with self.lock:
            if len(self.audio_buffer) < self.chunk_size:
                return  # Not enough data
            
            # Convert buffer to numpy array
            audio_data = np.array(list(self.audio_buffer))
            
            # Clear processed data (keep some overlap)
            overlap_samples = self.chunk_size // 4
            self.audio_buffer = deque(list(self.audio_buffer)[-overlap_samples:], 
                                    maxlen=self.audio_buffer.maxlen)
        
        if self.channels == 2:
            # Separate left and right channels
            left_channel = audio_data[0::2]   # Even indices
            right_channel = audio_data[1::2]  # Odd indices
        else:
            # Mono - use same data for both channels
            left_channel = audio_data
            right_channel = audio_data
        
        # Calculate RMS values
        left_rms = np.sqrt(np.mean(left_channel**2)) if len(left_channel) > 0 else 0
        right_rms = np.sqrt(np.mean(right_channel**2)) if len(right_channel) > 0 else 0
        
        # Convert to dB (VU scale)
        self.left_vu_db = self._rms_to_db(left_rms)
        self.right_vu_db = self._rms_to_db(right_rms)
    
    def _rms_to_db(self, rms_value):
        """Convert RMS value to dB scale."""
        if rms_value <= 0:
            return self.VU_MIN_DB
        
        # Calculate dB relative to VU reference level
        db_value = 20 * math.log10(rms_value / self.VU_REFERENCE)
        
        # Clamp to VU range
        return max(self.VU_MIN_DB, min(self.VU_MAX_DB, db_value))
    
    def get_vu_levels(self):
        """
        Get current VU levels for left and right channels.
        
        Returns:
            tuple: (left_db, right_db) - VU levels in dB (-60 to +6 dB range)
        """
        with self.lock:
            return self.left_vu_db, self.right_vu_db
    
    def get_vu_levels_normalized(self):
        """
        Get current VU levels normalized to 0.0-1.0 range.
        
        Returns:
            tuple: (left_normalized, right_normalized) - Values from 0.0 to 1.0
        """
        left_db, right_db = self.get_vu_levels()
        
        # Normalize from dB range to 0.0-1.0
        left_norm = (left_db - self.VU_MIN_DB) / (self.VU_MAX_DB - self.VU_MIN_DB)
        right_norm = (right_db - self.VU_MIN_DB) / (self.VU_MAX_DB - self.VU_MIN_DB)
        
        # Clamp to valid range
        left_norm = max(0.0, min(1.0, left_norm))
        right_norm = max(0.0, min(1.0, right_norm))
        
        return left_norm, right_norm
    
    def is_running(self):
        """Check if VU monitor is currently running."""
        return self.running and self.stream and self.stream.is_active()


def main():
    """Test the VU Monitor functionality."""
    print("Python VU Monitor Test")
    print("=" * 30)
    
    # Create VU monitor
    vu_monitor = VUMonitor(update_rate=10)
    
    # List available devices
    vu_monitor.list_audio_devices()
    
    try:
        # Start monitoring
        if vu_monitor.start():
            print("\nMonitoring VU levels... Press Ctrl+C to stop")
            print("Format: Left: XXX dB | Right: XXX dB")
            print("-" * 40)
            
            while True:
                left_db, right_db = vu_monitor.get_vu_levels()
                left_norm, right_norm = vu_monitor.get_vu_levels_normalized()
                
                # Create simple bar display
                left_bar = "█" * int(left_norm * 20)
                right_bar = "█" * int(right_norm * 20)
                
                print(f"\rL: {left_db:5.1f}dB [{left_bar:<20}] | R: {right_db:5.1f}dB [{right_bar:<20}]", 
                      end="", flush=True)
                
                time.sleep(0.1)  # 10 Hz display update
        
        else:
            print("Failed to start VU Monitor")
    
    except KeyboardInterrupt:
        print("\n\nStopping VU Monitor...")
    
    finally:
        vu_monitor.stop()
        print("VU Monitor test completed")


if __name__ == "__main__":
    main()