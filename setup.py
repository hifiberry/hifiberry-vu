#!/usr/bin/env python3
"""
Setup script for HiFiBerry VU Meter package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read version from package
version = {}
with open("hifiberry_vu/__init__.py") as fp:
    exec(fp.read(), version, version)

setup(
    name="hifiberry-vu",
    version=version['__version__'],
    description="SDL2-based VU meter display with real-time audio monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="HiFiBerry",
    author_email="support@hifiberry.com",
    url="https://github.com/hifiberry/hifiberry-vu",
    license="MIT",
    
    packages=find_packages(),
    package_data={
        "": ["../img/*.png"],  # Include image files
    },
    include_package_data=True,
    
    install_requires=[
        "pysdl2",
        "pyaudio",
        "numpy",
    ],
    
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ]
    },
    
    entry_points={
        "console_scripts": [
            "hifiberry-vu=hifiberry_vu.vu_meter:main",
            "vu-meter=hifiberry_vu.vu_meter:main",
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: System :: Hardware",
        "Operating System :: POSIX :: Linux",
    ],
    
    python_requires=">=3.8",
    
    keywords="audio vu-meter sdl2 alsa raspberry-pi hifiberry",
    
    project_urls={
        "Bug Reports": "https://github.com/hifiberry/hifiberry-vu/issues",
        "Source": "https://github.com/hifiberry/hifiberry-vu",
        "Documentation": "https://github.com/hifiberry/hifiberry-vu/blob/main/README.md",
    },
)