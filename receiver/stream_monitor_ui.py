#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import matplotlib.ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import sys
import os
import threading
import subprocess
from stream_receiver import StreamReceiver
from stream_monitor_utils import check_ffmpeg_installation

class StreamMonitorUI:
    def __init__(self, sender_ip=""):
        self.sender_ip = sender_ip
        self.root = tk.Tk()
        self.root.title("Audio/Video Stream Quality Monitor")
        self.root.geometry("1000x800")
        
        ffmpeg_available, _ = check_ffmpeg_installation()
        if not ffmpeg_available:
            print("WARNING: FFmpeg not found. Recording disabled.")
        
        self.receiver = StreamReceiver(sender_ip)
        self.receiver.set_callbacks(
            log_callback=self.update_log,
            metrics_callback=self.update_metrics,
            decision_callback=self.update_decision
        )
        self.setup_ui()
    
    def setup_ui(self):
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="Sender IP:").pack(side=tk.LEFT)
        self.ip_entry = ttk.Entry(control_frame, width=15)
        self.ip_entry.insert(0, self.sender_ip)
        self.ip_entry.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(control_frame, text="Start Receiving", command=self.start)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Receiving", command=self.stop)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.state(['disabled'])
        
        self.record_button = ttk.Button(control_frame, text="Record 3s", command=self.record)
        self.record_button.pack(side=tk.LEFT, padx=5)
        self.record_button.state(['disabled'])
        
        # Add enhance button
        self.enhance_button = ttk.Button(control_frame, text="Enhance Audio", command=self.enhance_latest_audio)
        self.enhance_button.pack(side=tk.LEFT, padx=5)
        
        metrics_frame = ttk.LabelFrame(self.root, text="Real-time Metrics", padding=10)
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        row = 0
        ttk.Label(metrics_frame, text="Video Bitrate:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.video_bitrate_label = ttk.Label(metrics_frame, text="0 kbps")
        self.video_bitrate_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(metrics_frame, text="Audio Bitrate:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
        self.audio_bitrate_label = ttk.Label(metrics_frame, text="0 kbps")
        self.audio_bitrate_label.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        ttk.Label(metrics_frame, text="Video FPS:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.video_fps_label = ttk.Label(metrics_frame, text="0 fps")
        self.video_fps_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(metrics_frame, text="Total Bandwidth:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
        self.total_bandwidth_label = ttk.Label(metrics_frame, text="0 kbps")
        self.total_bandwidth_label.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        ttk.Label(metrics_frame, text="Video Latency:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.video_latency_label = ttk.Label(metrics_frame, text="0 ms")
        self.video_latency_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(metrics_frame, text="Audio Latency:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
        self.audio_latency_label = ttk.Label(metrics_frame, text="0 ms")
        self.audio_latency_label.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        ttk.Label(metrics_frame, text="Packet Loss:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.packet_loss_label = ttk.Label(metrics_frame, text="0 %")
        self.packet_loss_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(metrics_frame, text="Connection Status:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
        self.connection_status_label = ttk.Label(metrics_frame, text="Not Connected")
        self.connection_status_label.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
        
        decision_frame = ttk.LabelFrame(self.root, text="Processing Mode Decision", padding=10)
        decision_frame.pack(fill=tk.X, padx=10, pady=5)
        
        row = 0
        ttk.Label(decision_frame, text="Current Mode:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.current_mode_label = ttk.Label(decision_frame, text="Unknown")
        self.current_mode_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(decision_frame, text="S11 Mean:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
        self.s11_mean_label = ttk.Label(decision_frame, text="0.00 dB")
        self.s11_mean_label.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        ttk.Label(decision_frame, text="Mode Code:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.mode_code_label = ttk.Label(decision_frame, text="-1")
        self.mode_code_label.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(decision_frame, text="Decision Value:").grid(row=row, column=2, sticky=tk.W, padx=5, pady=2)
        self.defuzzified_value_label = ttk.Label(decision_frame, text="0.00")
        self.defuzzified_value_label.grid(row=row, column=3, sticky=tk.W, padx=5, pady=2)
        
        row += 1
        ttk.Label(decision_frame, text="Mode Description:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.mode_description_label = ttk.Label(decision_frame, text="No processing mode active", wraplength=400)
        self.mode_description_label.grid(row=row, column=1, columnspan=3, sticky=tk.W, padx=5, pady=2)
        
        charts_frame = ttk.LabelFrame(self.root, text="Performance Monitoring Charts", padding=10)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.figure = Figure(figsize=(10, 6), dpi=100)
        
        self.bitrate_plot = self.figure.add_subplot(311)
        self.bitrate_plot.set_title('Real-time Bitrate')
        self.bitrate_plot.set_xlabel('Time (s)')
        self.bitrate_plot.set_ylabel('Bitrate (kbps)')
        self.bitrate_plot.grid(True)
        
        self.latency_plot = self.figure.add_subplot(312)
        self.latency_plot.set_title('Real-time Latency')
        self.latency_plot.set_xlabel('Time (s)')
        self.latency_plot.set_ylabel('Latency (ms)')
        self.latency_plot.grid(True)
        
        self.s11_plot = self.figure.add_subplot(313)
        self.s11_plot.set_title('S11 Parameter')
        self.s11_plot.set_xlabel('Time (s)')
        self.s11_plot.set_ylabel('S11 (dB)')
        self.s11_plot.grid(True)
        
        self.figure.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.figure, charts_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=5, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
    
    def update_log(self, message):
        # This method is called from the main thread or worker threads
        # Use after to schedule the UI update in the main thread
        try:
            self.root.after(0, lambda: self.log_text.insert(tk.END, f"{message}\n") or self.log_text.see(tk.END))
        except Exception as e:
            print(f"Error updating log: {str(e)}")
    
    def update_metrics(self, metrics):
        try:
            self.root.after(0, lambda: self._update_metrics_internal(metrics))
        except Exception as e:
            print(f"Error scheduling metrics update: {str(e)}")
    
    def _update_metrics_internal(self, metrics):
        try:
            self.video_bitrate_label.config(text=f"{metrics['video_bitrate']:.1f} kbps")
            self.audio_bitrate_label.config(text=f"{metrics['audio_bitrate']:.1f} kbps")
            self.total_bandwidth_label.config(text=f"{metrics['total_bitrate']:.1f} kbps")
            self.video_fps_label.config(text=f"{metrics['video_fps']} fps")
            self.video_latency_label.config(text=f"{metrics['video_latency']} ms")
            self.audio_latency_label.config(text=f"{metrics['audio_latency']} ms")
            self.packet_loss_label.config(text=f"{metrics['packet_loss']:.1f} %")
            
            self.connection_status_label.config(text="Connected" if metrics['connected'] else "Not Connected")
            self.record_button.state(['!disabled'] if metrics['connected'] else ['disabled'])
            
            self.update_charts(metrics)
        except Exception as e:
            print(f"Error updating metrics: {str(e)}")
    
    def update_decision(self, decision_data):
        try:
            self.root.after(0, lambda: self._update_decision_internal(decision_data))
        except Exception as e:
            print(f"Error scheduling decision update: {str(e)}")
    
    def _update_decision_internal(self, decision_data):
        try:
            mode = decision_data.get("mode", "Unknown")
            mode_code = decision_data.get("mode_code", -1)
            s11_mean = decision_data.get("s11_mean", 0)
            defuzzified_value = decision_data.get("defuzzified_value", 0)
            
            self.current_mode_label.config(text=mode)
            self.s11_mean_label.config(text=f"{s11_mean:.2f} dB")
            self.mode_code_label.config(text=f"{mode_code}")
            self.defuzzified_value_label.config(text=f"{defuzzified_value:.2f}")
            
            descriptions = {
                4: "Advanced AV Mode: High-quality processing for poor conditions",
                3: "Standard AV Mode: Suitable for moderate conditions",
                2: "Light AV Mode: For slightly degraded conditions",
                1: "Audio-Only Mode: Audio processing for good conditions",
                0: "No Enhancement: Excellent conditions",
                -1: "Unknown/Error"
            }
            self.mode_description_label.config(text=descriptions.get(mode_code, "Unknown mode"))
        except Exception as e:
            print(f"Error updating decision display: {str(e)}")
    
    def update_charts(self, metrics):
        try:
            timestamps = metrics.get('timestamps', [])
            bitrate_data = metrics.get('bitrate_history', [])
            latency_data = metrics.get('latency_history', [])
            s11_data = metrics.get('s11_history', [])
            
            for plot in [self.bitrate_plot, self.latency_plot, self.s11_plot]:
                plot.clear()
            
            self.bitrate_plot.set_title('Real-time Bitrate')
            self.bitrate_plot.set_ylabel('Bitrate (kbps)')
            self.bitrate_plot.grid(True)
            
            self.latency_plot.set_title('Real-time Latency')
            self.latency_plot.set_ylabel('Latency (ms)')
            self.latency_plot.grid(True)
            
            self.s11_plot.set_title('S11 Parameter')
            self.s11_plot.set_xlabel('Time (s)')
            self.s11_plot.set_ylabel('S11 (dB)')
            self.s11_plot.grid(True)
            
            window_size = 30
            if timestamps:
                current_time = timestamps[-1]
                x_min = max(0, current_time - window_size)
                x_max = current_time
                
                if bitrate_data:
                    self.bitrate_plot.plot(timestamps, bitrate_data, 'b-')
                    self.bitrate_plot.set_xlim(x_min, x_max)
                    self.bitrate_plot.set_ylim(0, max(max(bitrate_data), 1) * 1.2)
                
                if latency_data:
                    self.latency_plot.plot(timestamps, latency_data, 'r-')
                    self.latency_plot.set_xlim(x_min, x_max)
                    self.latency_plot.set_ylim(0, max(max(latency_data), 1) * 1.2)
                
                if s11_data:
                    self.s11_plot.plot(timestamps[-len(s11_data):], s11_data, 'g-')
                    self.s11_plot.set_xlim(x_min, x_max)
                    min_s11, max_s11 = min(s11_data, default=-85), max(s11_data, default=-25)
                    padding = abs(max_s11 - min_s11) * 0.1 if min_s11 != max_s11 else 5
                    self.s11_plot.set_ylim(min_s11 - padding, max_s11 + padding)
            else:
                for plot in [self.bitrate_plot, self.latency_plot, self.s11_plot]:
                    plot.set_xlim(0, window_size)
                self.bitrate_plot.set_ylim(0, 100)
                self.latency_plot.set_ylim(0, 100)
                self.s11_plot.set_ylim(-85, -25)
            
            self.figure.tight_layout()
            self.canvas.draw()
        except Exception as e:
            self.update_log(f"Chart update error: {str(e)}")
    
    def start(self):
        new_ip = self.ip_entry.get()
        if not new_ip:
            self.update_log("Error: Please enter sender IP")
            return
        
        self.receiver.sender_ip = new_ip
        self.start_button.state(['disabled'])
        self.stop_button.state(['!disabled'])
        self.update_log(f"Receiving from {self.receiver.sender_ip}")
        self.receiver.start()
    
    def stop(self):
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        self.record_button.state(['disabled'])
        self.receiver.stop()
    
    def record(self):
        if not self.receiver.running:
            self.update_log("Error: Start receiving first")
            return False
        
        self.record_button.state(['disabled'])
        success = self.receiver.record(3)
        if success:
            self.root.after(4000, lambda: self.record_button.state(['!disabled']))
            self.root.after(3500, lambda: self.update_log("Recording completed"))
        else:
            self.record_button.state(['!disabled'])
        return success
    
    def enhance_latest_audio(self):
        """Enhance the latest recorded audio file using the Denoiser model"""
        self.update_log("Starting audio enhancement process...")
        
        # Disable the enhance button to prevent multiple clicks
        self.enhance_button.state(['disabled'])
        
        # Create and start enhancement thread
        enhance_thread = threading.Thread(
            target=self._run_enhancer_process,
            daemon=True
        )
        enhance_thread.start()
    
    def _run_enhancer_process(self):
        """Run the enhancer process in a separate thread"""
        print(f"Run the enhancer process")
        try:
            # Get the current directory
            current_dir = os.getcwd()
            enhancer_script = os.path.join(current_dir, "audio_enhancer.py")
            recording_dir = self.receiver.recording_dir
            
            # Run the enhancer script as a subprocess
            process = subprocess.Popen(
                [sys.executable, enhancer_script, recording_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Read stdout in real-time and schedule UI updates in the main thread
            for line in process.stdout:
                try:
                    line_text = line.strip()
                    self.root.after(0, lambda msg=line_text: self.update_log(msg))
                except Exception as e:
                    print(f"Error scheduling log update: {str(e)}")
            
            # Check for errors
            stderr = process.stderr.read()
            if stderr:
                self.root.after(0, lambda: self.update_log(f"Error: {stderr}"))
            
            process.wait()
            if process.returncode != 0:
                self.root.after(0, lambda: self.update_log(f"Enhancement process failed with code {process.returncode}"))
            
            # Re-enable the enhance button
            self.root.after(0, lambda: self.enhance_button.state(['!disabled']))
        except Exception as e:
            print(f"Enhancement thread error: {str(e)}")
            self.root.after(0, lambda: self.update_log(f"Error: {str(e)}"))
            self.root.after(0, lambda: self.enhance_button.state(['!disabled']))
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        if self.receiver.running:
            self.stop()
        self.root.destroy()

if __name__ == "__main__":
    sender_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.1"
    try:
        monitor = StreamMonitorUI(sender_ip)
        monitor.run()
    except ImportError as e:
        print(f"Error: {e}\nInstall dependencies: pip install matplotlib numpy psutil")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")