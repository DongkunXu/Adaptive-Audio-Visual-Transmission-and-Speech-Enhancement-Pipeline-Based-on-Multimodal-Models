#!/usr/bin/env python3
import os
import sys
import re
import subprocess

def check_directory_permissions(directory_path, log_function=None):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            if log_function:
                log_function(f"Created directory: {directory_path}")
        except Exception as e:
            if log_function:
                log_function(f"ERROR creating directory: {str(e)}")
            return False
    
    if os.access(directory_path, os.W_OK):
        return True
    else:
        if log_function:
            log_function(f"Directory {directory_path} is not writable")
        try:
            os.chmod(directory_path, 0o755)
            if log_function:
                log_function("Fixed directory permissions")
            return True
        except Exception as e:
            if log_function:
                log_function(f"Failed to fix permissions: {str(e)}")
            return False

def measure_latency(target_ip, log_function=None):
    try:
        ping_cmd = ['ping', '-n', '1', '-w', '1000'] if sys.platform.startswith('win') else ['ping', '-c', '1', '-W', '1']
        ping_cmd.append(target_ip)
        result = subprocess.run(ping_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            match = re.search(r'time[=<](\d+)ms' if sys.platform.startswith('win') else r'time=([\d.]+) ms', result.stdout)
            if match:
                return float(match.group(1))
        return 999
    except Exception as e:
        if log_function:
            log_function(f"Latency measurement error: {str(e)}")
        return 999

def check_ffmpeg_installation(log_function=None):
    try:
        result = subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            version = result.stdout.splitlines()[0] if result.stdout else "Unknown version"
            if log_function:
                log_function(f"FFmpeg found: {version}")
            return True, version
        return False, None
    except Exception as e:
        if log_function:
            log_function(f"FFmpeg check error: {str(e)}")
        return False, None