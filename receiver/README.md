# Receiver Module 📡 🎧

This module runs on Windows and handles receiving audio-visual streams, monitoring quality metrics, and applying adaptive speech enhancement models.

## Components

### Stream Reception and Monitoring 📊
- `stream_monitor_ui.py`: Main GUI application for monitoring and controlling stream reception
- `stream_receiver.py`: Core functionality for receiving and processing UDP streams
- `stream_monitor_utils.py`: Utility functions for system operations

### Audio Enhancement 🔊
- `audio_enhancer.py`: Implements deep learning-based audio enhancement using pretrained models

## System Requirements

- Windows 10/11
- 8GB+ RAM (16GB recommended)
- NVIDIA GPU with CUDA support (recommended for ML model acceleration)
- Ethernet connection (recommended for stable reception)

## Dependencies

The receiver module requires the following dependencies:
- Python 3.8+
- PyTorch and torchaudio
- numpy
- matplotlib
- FFmpeg (added to system PATH)
- tkinter
- sounddevice
- psutil

## Audio Enhancement Models

The system uses deep learning models for speech enhancement:
- DNS-48: Lightweight denoising model
- DNS-64: Enhanced denoising model
- Custom AVSE models: For audio-visual speech enhancement

Model selection is performed automatically based on decision data received from the sender module.

## Usage Notes

The system must be on the same network as the sender to receive UDP multicast streams. Windows firewall settings may need adjustment to allow multicast traffic.

The receiver monitors stream quality metrics and can record short segments for enhanced processing. The "Enhance Audio" feature applies the current processing mode to the most recently recorded audio.

**Important**: This code is proprietary and not for distribution. Usage requires explicit permission from the authors.

---

**Note**: For optimal performance, ensure the audio output device is properly configured and CUDA is set up for PyTorch if a compatible GPU is available.
