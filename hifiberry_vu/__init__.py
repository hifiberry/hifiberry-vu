"""
HiFiBerry VU Meter Package
=========================

A SDL2-based VU meter display application with real-time audio monitoring.

Features:
- Real-time ALSA audio monitoring with configurable VU levels
- Customizable needle display with rotation support
- Multiple display modes: demo, ALSA audio, fixed position
- Configurable VU meter images and needle parameters
- Smooth needle movement with configurable averaging
- Console FPS monitoring
"""

__version__ = "1.0.0"
__author__ = "HiFiBerry"
__description__ = "SDL2-based VU meter display with real-time audio monitoring"

from .vu_meter import VUMeter, main
from .python_vu import VUMonitor

__all__ = ['VUMeter', 'VUMonitor', 'main']