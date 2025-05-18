# Sender Module 📡 🎬

This module runs on Raspberry Pi and handles media capture, S11 parameter measurement, and transmission of audio-visual data streams along with processing mode decisions.

## Components

### S11 Monitoring System 📊
- `s11_monitor.py`: Core module for S11 parameter monitoring and processing mode decision making
- `pocketvna_monitor.py`: Standalone GUI application for S11 parameter visualization and testing

### Media Streaming 🎤 🎥
- `streamer_UDP.py`: UDP multicast streaming service for audio and video transmission

## Hardware Requirements

- Raspberry Pi (4 recommended)
- PocketVNA device
- USB Camera compatible with libcamera
- USB Microphone or Audio HAT
- Ethernet connection (recommended for stable streaming)

## Dependencies

The sender module requires the following dependencies:
- Python 3.7+
- numpy
- matplotlib
- scikit-fuzzy
- PocketVNA Python API
- FFmpeg
- libcamera-tools

## Network Configuration

The system uses the following default ports:
- Video Stream: UDP 239.0.0.1:5100
- Audio Stream: UDP 239.0.0.1:5101
- Timestamp Service: UDP Port 5102
- Decision Service: TCP Port 5103

## Usage Notes

This module is designed to run on Raspberry Pi OS. Proper permissions are required for accessing the PocketVNA device through USB.

**Important**: This code is proprietary and not for distribution. Usage requires explicit permission from the authors.

---

**Caution**: The S11 monitoring system requires specific hardware setup. Incorrect connections to the VNA device may provide inaccurate measurements.
