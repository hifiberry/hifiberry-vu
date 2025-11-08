#!/usr/bin/env python3
"""
AcoustID Song Detection Tool

Records audio from ALSA and uses AcoustID to identify the currently playing song.
Requires Chromaprint (fpcalc) to generate audio fingerprints.

Usage:
    python detect_song.py --api-key YOUR_API_KEY
    python detect_song.py --api-key YOUR_API_KEY --duration 10 --device "hw:1,0"
    python detect_song.py --api-key YOUR_API_KEY --continuous

Installation:
    # Install Chromaprint
    sudo apt-get install libchromaprint-tools
    
    # Install Python dependencies
    pip install pyaudio numpy requests

Features:
    - Records audio from ALSA at 44.1kHz, 16-bit stereo
    - Generates Chromaprint fingerprints
    - Queries AcoustID API for song identification
    - Displays artist, title, and album information
    - Supports continuous monitoring mode
"""

import argparse
import sys
import os
import tempfile
import subprocess
import json
import time
import wave
import struct
from pathlib import Path

try:
    import pyaudio
    import numpy as np
except ImportError:
    print("Error: Required packages not found.")
    print("Install with: pip install pyaudio numpy")
    sys.exit(1)

try:
    from hifiberry_vu.acoustid import AcoustIDClient, AcoustIDError
except ImportError:
    try:
        from acoustid import AcoustIDClient, AcoustIDError
    except ImportError:
        print("Error: AcoustID module not found.")
        print("Make sure acoustid.py is in the hifiberry_vu directory.")
        sys.exit(1)


class AudioRecorder:
    """Records audio from ALSA device."""
    
    def __init__(self, 
                 device_name=None,
                 sample_rate=44100,
                 channels=2,
                 sample_width=2):  # 16-bit = 2 bytes
        """
        Initialize audio recorder.
        
        Args:
            device_name: ALSA device name (e.g., "hw:1,0") or None for default
            sample_rate: Sample rate in Hz (default: 44100)
            channels: Number of channels (default: 2 for stereo)
            sample_width: Bytes per sample (default: 2 for 16-bit)
        """
        self.device_name = device_name
        self.sample_rate = sample_rate
        self.channels = channels
        self.sample_width = sample_width
        self.format = pyaudio.paInt16  # 16-bit
        
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
    
    def find_device_index(self):
        """Find the index of the specified ALSA device."""
        if not self.device_name:
            return None  # Use default device
        
        for i in range(self.pyaudio.get_device_count()):
            info = self.pyaudio.get_device_info_by_index(i)
            if self.device_name in info['name']:
                return i
        
        return None
    
    def record(self, duration_seconds, verbose=False):
        """
        Record audio for specified duration.
        
        Args:
            duration_seconds: How long to record in seconds
            verbose: Print recording progress
            
        Returns:
            numpy array of audio samples (interleaved stereo)
        """
        chunk_size = 1024
        device_index = self.find_device_index()
        
        if verbose:
            if device_index is not None:
                print(f"Recording from device: {self.device_name} (index {device_index})")
            else:
                print("Recording from default device")
            print(f"Duration: {duration_seconds}s, Sample Rate: {self.sample_rate}Hz")
            print("Recording", end="", flush=True)
        
        try:
            self.stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=chunk_size
            )
            
            frames = []
            num_chunks = int(self.sample_rate / chunk_size * duration_seconds)
            
            for i in range(num_chunks):
                data = self.stream.read(chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                if verbose and i % 10 == 0:
                    print(".", end="", flush=True)
            
            if verbose:
                print(" Done!")
            
            # Convert to numpy array
            audio_data = b''.join(frames)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            return audio_array
            
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
    
    def save_wav(self, audio_data, filename):
        """
        Save audio data to WAV file.
        
        Args:
            audio_data: numpy array of audio samples
            filename: Output filename
        """
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(self.sample_width)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data.tobytes())
    
    def close(self):
        """Clean up PyAudio resources."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.pyaudio.terminate()


class FingerprintGenerator:
    """Generates Chromaprint fingerprints using fpcalc."""
    
    @staticmethod
    def check_fpcalc():
        """Check if fpcalc is installed."""
        try:
            subprocess.run(['fpcalc', '-version'], 
                         capture_output=True, 
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    @staticmethod
    def generate(audio_file):
        """
        Generate fingerprint from audio file.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Tuple of (duration, fingerprint) or (None, None) on error
        """
        try:
            result = subprocess.run(
                ['fpcalc', '-json', str(audio_file)],
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            return data.get('duration'), data.get('fingerprint')
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            print(f"Error generating fingerprint: {e}")
            return None, None


class SongDetector:
    """Main song detection application."""
    
    def __init__(self, api_key, device_name=None):
        """
        Initialize song detector.
        
        Args:
            api_key: AcoustID API key
            device_name: Optional ALSA device name
        """
        self.api_key = api_key
        self.device_name = device_name
        self.recorder = AudioRecorder(device_name=device_name)
        self.acoustid = AcoustIDClient(api_key=api_key)
    
    def detect_song(self, duration=10, verbose=True):
        """
        Record audio and detect the song.
        
        Args:
            duration: Recording duration in seconds
            verbose: Print detailed information
            
        Returns:
            Dictionary with detection results or None
        """
        if verbose:
            print("\n" + "="*60)
            print("AcoustID Song Detection")
            print("="*60)
        
        # Record audio
        try:
            audio_data = self.recorder.record(duration, verbose=verbose)
        except Exception as e:
            print(f"Error recording audio: {e}")
            return None
        
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            if verbose:
                print("Saving audio to temporary file...")
            self.recorder.save_wav(audio_data, tmp_filename)
            
            # Generate fingerprint
            if verbose:
                print("Generating audio fingerprint...")
            duration_sec, fingerprint = FingerprintGenerator.generate(tmp_filename)
            
            if not fingerprint:
                print("Failed to generate fingerprint")
                return None
            
            if verbose:
                print(f"Fingerprint generated (duration: {duration_sec}s)")
                print("Querying AcoustID API...")
            
            # Query AcoustID
            try:
                result = self.acoustid.lookup_fingerprint(
                    duration=duration_sec,
                    fingerprint=fingerprint,
                    meta=['recordings', 'releasegroups', 'compress']
                )
                
                if result['status'] == 'ok' and result.get('results'):
                    return self._format_results(result, verbose)
                else:
                    if verbose:
                        print("No matches found")
                    return None
                    
            except AcoustIDError as e:
                print(f"AcoustID API error: {e}")
                return None
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_filename)
            except:
                pass
    
    def _format_results(self, result, verbose=True):
        """Format and display detection results."""
        matches = result.get('results', [])
        
        if not matches:
            return None
        
        # Get the best match (highest score)
        best_match = matches[0]
        score = best_match.get('score', 0)
        
        if verbose:
            print("\n" + "-"*60)
            print(f"Match found! (Confidence: {score*100:.1f}%)")
            print("-"*60)
        
        song_info = {
            'acoustid': best_match.get('id'),
            'score': score,
            'title': None,
            'artists': [],
            'album': None,
            'album_type': None,
            'duration': None,
            'musicbrainz_id': None
        }
        
        # Extract recording information
        recordings = best_match.get('recordings', [])
        if recordings:
            recording = recordings[0]  # Use first recording
            
            song_info['title'] = recording.get('title', 'Unknown')
            song_info['duration'] = recording.get('duration')
            song_info['musicbrainz_id'] = recording.get('id')
            
            # Extract artists
            if 'artists' in recording:
                song_info['artists'] = [a['name'] for a in recording['artists']]
            
            # Extract album info
            if 'releasegroups' in recording:
                release_groups = recording['releasegroups']
                if release_groups:
                    rg = release_groups[0]
                    song_info['album'] = rg.get('title')
                    song_info['album_type'] = rg.get('type')
        
        # Display results
        if verbose:
            print(f"\nTitle:  {song_info['title'] or 'Unknown'}")
            
            if song_info['artists']:
                artists_str = ', '.join(song_info['artists'])
                print(f"Artist: {artists_str}")
            
            if song_info['album']:
                album_str = song_info['album']
                if song_info['album_type']:
                    album_str += f" ({song_info['album_type']})"
                print(f"Album:  {album_str}")
            
            if song_info['duration']:
                minutes = song_info['duration'] // 60
                seconds = song_info['duration'] % 60
                print(f"Length: {minutes}:{seconds:02d}")
            
            print(f"\nAcoustID: {song_info['acoustid']}")
            if song_info['musicbrainz_id']:
                print(f"MusicBrainz ID: {song_info['musicbrainz_id']}")
            print("-"*60)
        
        return song_info
    
    def continuous_monitoring(self, duration=10, interval=30, verbose=True):
        """
        Continuously monitor and detect songs.
        
        Args:
            duration: Recording duration for each detection
            interval: Seconds between detections
            verbose: Print detailed information
        """
        print("\n" + "="*60)
        print("Continuous Song Monitoring")
        print("="*60)
        print(f"Recording {duration}s every {interval}s")
        print("Press Ctrl+C to stop")
        print("="*60)
        
        last_song = None
        
        try:
            while True:
                song_info = self.detect_song(duration=duration, verbose=verbose)
                
                # Check if it's a different song
                if song_info:
                    current_song = (song_info.get('title'), 
                                  tuple(song_info.get('artists', [])))
                    
                    if current_song != last_song:
                        print("\n🎵 NEW SONG DETECTED!")
                        last_song = current_song
                    else:
                        print("\n♫ Same song still playing")
                
                # Wait before next detection
                if verbose:
                    print(f"\nWaiting {interval}s before next check...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nStopping monitoring...")
    
    def close(self):
        """Clean up resources."""
        self.recorder.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Detect songs using AcoustID',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --api-key YOUR_API_KEY
  %(prog)s --api-key YOUR_API_KEY --duration 15
  %(prog)s --api-key YOUR_API_KEY --device "hw:1,0"
  %(prog)s --api-key YOUR_API_KEY --continuous --interval 60

Requirements:
  - fpcalc (Chromaprint): sudo apt-get install libchromaprint-tools
  - Python packages: pip install pyaudio numpy requests
        """
    )
    
    parser.add_argument(
        '--api-key',
        required=True,
        help='AcoustID API key (get one at https://acoustid.org/new-application)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=10,
        help='Recording duration in seconds (default: 10)'
    )
    
    parser.add_argument(
        '--device',
        default=None,
        help='ALSA device name (e.g., "hw:1,0") or None for default'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Continuous monitoring mode'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Seconds between detections in continuous mode (default: 30)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output (only show results)'
    )
    
    args = parser.parse_args()
    
    # Check for fpcalc
    if not FingerprintGenerator.check_fpcalc():
        print("Error: fpcalc (Chromaprint) not found!")
        print("Install with: sudo apt-get install libchromaprint-tools")
        sys.exit(1)
    
    # Create detector
    detector = SongDetector(
        api_key=args.api_key,
        device_name=args.device
    )
    
    try:
        if args.continuous:
            detector.continuous_monitoring(
                duration=args.duration,
                interval=args.interval,
                verbose=not args.quiet
            )
        else:
            result = detector.detect_song(
                duration=args.duration,
                verbose=not args.quiet
            )
            
            if not result:
                sys.exit(1)
    
    finally:
        detector.close()


if __name__ == '__main__':
    main()
