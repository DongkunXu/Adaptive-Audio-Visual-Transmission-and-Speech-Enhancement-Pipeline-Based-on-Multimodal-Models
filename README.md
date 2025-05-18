# AdaptiveAudioVisual Transmission and Speech Enhancement Pipeline 🎤 🎥 🔊

## Overview

This project implements an adaptive audio-visual transmission and speech enhancement system that dynamically selects appropriate enhancement models based on environmental conditions. By leveraging a Vector Network Analyzer (VNA) to assess user cognitive states, the system intelligently switches between audio-only and audio-visual speech enhancement models to optimize processing resources while maintaining high-quality output.

![System Architecture](docs/images/system_architecture.png)

## Key Components 🔧

### Sender Module (Raspberry Pi)
- Captures audio and video input streams
- Monitors cognitive load using S11 parameters from PocketVNA
- Broadcasts media streams via UDP multicast
- Transmits processing mode decisions based on real-time measurements
- Provides timestamp services for latency calculation

### Receiver Module (Windows)
- Receives and processes audio/video streams
- Implements real-time audio enhancement using deep learning models
- Dynamically adjusts processing based on received mode decisions
- Visualizes quality metrics and processing parameters
- Records and enhances audio segments on demand

## System Features ✨

- **Adaptive Processing**: Automatically selects between audio-only (AO) and audio-visual speech enhancement (AVSE) models based on environmental conditions
- **Real-time Monitoring**: Visualizes stream quality metrics and processing decisions
- **Low-latency Transmission**: Optimized for real-time applications with minimal delay
- **Cognitive State Integration**: Uses S11 parameters as a proxy for user cognitive state
- **Modular Architecture**: Separate sender and receiver components for flexible deployment

## Technology Stack 🔬

- **Signal Processing**: Vector Network Analysis, Speech Enhancement, Audio Processing
- **Machine Learning**: PyTorch-based Audio Enhancement Models
- **Networking**: UDP Multicast, TCP Control Channel, Custom Protocol
- **Visualization**: Real-time Metrics, Processing Mode Display
- **Hardware Integration**: PocketVNA, Camera and Microphone Systems

## Repository Structure 📁

```
.
├── sender/                 # Raspberry Pi sender module
│   ├── s11_monitor.py      # S11 parameter monitoring and decision making
│   ├── pocketvna_monitor.py # Standalone VNA monitoring with GUI
│   └── streamer_UDP.py     # Media streaming and transmission
│
├── receiver/               # Windows receiver module
│   ├── stream_monitor_ui.py  # Main UI for stream monitoring
│   ├── stream_receiver.py    # Stream receiver core functionality
│   ├── audio_enhancer.py     # Audio enhancement using ML models
│   └── stream_monitor_utils.py # Utility functions
│
├── docs/                   # Documentation
│   └── images/             # System diagrams and screenshots
│
├── LICENSE                 # Proprietary license
└── README.md               # This file
```

## License ⚖️

This is a proprietary project. All rights reserved. This code may not be used, modified, or distributed without explicit permission from the author.

## Contact 📧

For inquiries about this project, please contact the repository owner.

---

**Note**: This repository contains research code and is not intended for production use without proper testing and adaptation.
