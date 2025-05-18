#!/usr/bin/env python3
import os
import sys
import json
import glob
import torch
import torchaudio
import datetime
import logging
import threading

# Configure logging for errors only
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='audio_enhancer_errors.log'
)
logger = logging.getLogger('audio_enhancer')

# Path to the denoiser project
DENOISER_PATH = "/home/gpi-16-ssd/Documents/denoiser"
OUTPUT_DIR = os.path.join(os.getcwd(), "after_process")

# Create a thread lock for PyTorch operations
torch_thread_lock = threading.Lock()

def setup_paths():
    """Add the denoiser path to the system path to import its modules"""
    if DENOISER_PATH not in sys.path:
        sys.path.append(DENOISER_PATH)
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Denoiser path: {DENOISER_PATH}")
    print(f"Output directory: {OUTPUT_DIR}")

def get_latest_recording(recording_dir):
    """Find the latest audio recording and its associated info file"""
    audio_files = glob.glob(os.path.join(recording_dir, "audio_*.wav"))
    if not audio_files:
        print("WARNING: No audio recordings found")
        return None, None
    
    # Sort files by timestamp (newest first)
    latest_audio = max(audio_files, key=os.path.getctime)
    basename = os.path.basename(latest_audio)
    timestamp = basename.replace("audio_", "").replace(".wav", "")
    
    # Look for the corresponding info file
    info_filename = os.path.join(recording_dir, f"info_{timestamp}.json")
    if not os.path.exists(info_filename):
        print(f"WARNING: No info file found for {latest_audio}")
        return latest_audio, None
    
    # Read the info file
    with open(info_filename, 'r') as f:
        info = json.load(f)
    
    return latest_audio, info

def load_denoiser_model():
    """Load the denoiser model"""
    try:
        # Import the denoiser modules
        from denoiser.pretrained import dns48
        
        # Load the model
        print("Loading DNS-48 model...")
        model = dns48()
        
        # Move to CPU (or GPU if available)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        model.eval()
        
        print(f"Model loaded successfully on {device}")
        return model, device
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        print(f"ERROR: Failed to load model: {str(e)}")
        raise

def enhance_audio(model, device, audio_path):
    """Enhance audio using the denoiser model"""
    try:
        print(f"Processing audio file: {audio_path}")
        
        # Load the audio file
        waveform, sample_rate = torchaudio.load(audio_path)
        
        # Ensure the audio is mono and at the correct sample rate
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        
        if sample_rate != model.sample_rate:
            print(f"Resampling from {sample_rate} to {model.sample_rate}")
            from denoiser.dsp import convert_audio
            waveform = convert_audio(waveform, sample_rate, model.sample_rate, 1)
        
        # Move to device
        waveform = waveform.to(device)
        
        # Process audio with thread lock protection to avoid PyTorch threading issues
        print("Enhancing audio...")
        with torch_thread_lock, torch.no_grad():
            enhanced = model(waveform)
        
        return enhanced.cpu()
    
    except Exception as e:
        logger.error(f"Error enhancing audio: {str(e)}")
        print(f"ERROR: Audio enhancement failed: {str(e)}")
        raise

def save_enhanced_audio(enhanced_waveform, original_path, info, sample_rate=16000):
    """Save the enhanced audio to the output directory"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        orig_name = os.path.basename(original_path).replace(".wav", "")
        
        # Create output filename with enhancement mode info
        mode_code = info['mode_code'] if info else -1
        output_filename = f"{orig_name}_enhanced_mode{mode_code}_{timestamp}.wav"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # Normalize audio if it prevents clipping
        enhanced_waveform = enhanced_waveform / max(enhanced_waveform.abs().max().item(), 1)
        
        # Save the enhanced audio
        torchaudio.save(output_path, enhanced_waveform, sample_rate)
        print(f"Enhanced audio saved to: {output_path}")
        
        # Also save enhancement info alongside the audio
        if info:
            info_filename = output_path.replace(".wav", "_info.json")
            with open(info_filename, 'w') as f:
                json.dump(info, f, indent=4)
            print(f"Enhancement info saved to: {info_filename}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error saving enhanced audio: {str(e)}")
        print(f"ERROR: Failed to save enhanced audio: {str(e)}")
        raise

def enhance_latest_recording(recording_dir):
    """Main function to enhance the latest recorded audio file"""
    try:
        setup_paths()
        
        # Find the latest recording
        audio_path, info = get_latest_recording(recording_dir)
        if not audio_path:
            print("WARNING: No recordings found to enhance")
            return None
        
        print(f"Found latest recording: {audio_path}")
        if info:
            print(f"Enhancement mode: {info['mode']} (code: {info['mode_code']})")
        
        # Load the model
        model, device = load_denoiser_model()
        
        # Enhance the audio
        enhanced_waveform = enhance_audio(model, device, audio_path)
        
        # Save the enhanced audio
        output_path = save_enhanced_audio(enhanced_waveform, audio_path, info, model.sample_rate)
        
        print(f"Audio enhancement completed successfully!")
        return output_path, info
    
    except Exception as e:
        logger.exception(f"Error in enhance_latest_recording: {str(e)}")
        print(f"ERROR: Enhancement process failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Use a try/except block to catch and report any errors
    try:
        print("======= AUDIO ENHANCER =======")
        # If run as a script, look for recordings in the current directory
        recording_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), "recording")
        print(f"Looking for recordings in: {recording_dir}")
        
        # Set number of threads for PyTorch to prevent resource contention
        if hasattr(torch, 'set_num_threads'):
            torch.set_num_threads(1)
        
        result = enhance_latest_recording(recording_dir)
        
        if result:
            output_path, info = result
            print(f"Successfully enhanced audio: {output_path}")
            if info:
                print(f"Using enhancement mode: {info['mode']} (code: {info['mode_code']})")
            print("======= ENHANCEMENT COMPLETE =======")
        else:
            print("WARNING: No recordings were enhanced")
            print("======= ENHANCEMENT FAILED =======")
    
    except Exception as e:
        print(f"ERROR: An error occurred: {str(e)}")
        logger.exception("Detailed error information")
        print("======= ENHANCEMENT FAILED =======")
        sys.exit(1)