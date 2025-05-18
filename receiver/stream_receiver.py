#!/usr/bin/env python3
import subprocess
import threading
import time
import datetime
import socket
import psutil
import json
import os
import queue
import re
from collections import deque
from stream_monitor_utils import measure_latency, check_directory_permissions

# 全局调试设置 - 设置为True启用详细日志，False禁用大多数日志
DEBUG = False

class ThreadSafeLogger:
    """Thread-safe logging mechanism to safely send logs from worker threads to Tkinter UI"""
    def __init__(self, log_callback=None, file_path=None):
        self.log_queue = queue.Queue()
        self.log_callback = log_callback
        self.log_file = open(file_path, "a") if file_path else None
        self.running = True
        self.processor_thread = None
    
    def start(self):
        """Start the log processing thread"""
        self.running = True
        self.processor_thread = threading.Thread(target=self._process_logs, daemon=True)
        self.processor_thread.start()
    
    def stop(self):
        """Stop the log processing thread"""
        self.running = False
        if self.processor_thread:
            self.processor_thread.join(timeout=1)
        if self.log_file:
            self.log_file.close()
    
    def log(self, message, force=False):
        """Add a log message to the queue
        Args:
            message: The message to log
            force: If True, log even when DEBUG is False
        """
        if not DEBUG and not force:
            # 如果不是调试模式且未强制，只写入文件，不输出到UI
            if self.log_file:
                current_time = datetime.datetime.now().strftime("%H:%M:%S")
                log_message = f"[{current_time}] {message}"
                self.log_file.write(log_message + "\n")
                self.log_file.flush()
            return
            
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        log_message = f"[{current_time}] {message}"
        self.log_queue.put(log_message)
        
        # Also print to console directly for debugging
        print(log_message)
        
        # Write to file immediately to ensure it's captured even if processing thread fails
        if self.log_file:
            self.log_file.write(log_message + "\n")
            self.log_file.flush()
    
    def _process_logs(self):
        """Process log messages from the queue"""
        while self.running:
            try:
                # Use timeout to allow the thread to check running flag
                message = self.log_queue.get(timeout=0.1)
                if self.log_callback:
                    try:
                        self.log_callback(message)
                    except Exception as e:
                        print(f"Error in log callback: {str(e)}")
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Log processing error: {str(e)}")

class StreamReceiver:
    def __init__(self, sender_ip, multicast_addr='239.0.0.1', video_port=5100, audio_port=5101, timestamp_port=5102, decision_port=5103):
        self.sender_ip = sender_ip
        self.multicast_addr = multicast_addr
        self.video_port = video_port
        self.audio_port = audio_port
        self.timestamp_port = timestamp_port
        self.decision_port = decision_port
        
        self.video_process = None
        self.audio_process = None
        self.monitor_process = None
        self.decision_socket = None
        self.decision_thread = None
        self.record_process_video = None
        self.record_process_audio = None
        
        # Callbacks
        self.log_callback = None
        self.metrics_callback = None
        self.decision_callback = None
        
        # Initialize thread-safe logger
        self.thread_safe_logger = ThreadSafeLogger(file_path="stream_monitor.log")
        
        # Recording
        self.recording = False
        self.recording_dir = os.path.join(os.getcwd(), "recording")
        os.makedirs(self.recording_dir, exist_ok=True)
        
        # Metrics
        self.video_bitrate = 0
        self.audio_bitrate = 0
        self.video_fps = 0
        self.video_latency = 0
        self.audio_latency = 0
        self.packet_loss = 0
        
        # Decision data
        self.processing_mode = "Unknown"
        self.mode_code = -1
        self.s11_mean = 0
        self.defuzzified_value = 0
        self.last_decision_time = 0
        
        # History
        self.window_size = 30
        self.bitrate_history = deque(maxlen=self.window_size)
        self.latency_history = deque(maxlen=self.window_size)
        self.s11_history = deque(maxlen=self.window_size)
        self.timestamps = deque(maxlen=self.window_size)
        
        self.start_timestamp = time.time()
        self.frame_times = []
        self.timestamp_socket = None
        self.running = False
    
    def set_callbacks(self, log_callback=None, metrics_callback=None, decision_callback=None):
        self.log_callback = log_callback
        self.metrics_callback = metrics_callback
        self.decision_callback = decision_callback
        
        # Set the thread-safe logger callback and start it
        self.thread_safe_logger.log_callback = log_callback
        self.thread_safe_logger.start()
    
    def log(self, message, force=False):
        # Use thread-safe logger to log messages
        self.thread_safe_logger.log(message, force)
    
    def start_video_receiver(self):
        cmd = [
            'ffplay',
            '-fflags', 'nobuffer',
            '-flags', 'low_delay',
            '-framedrop',
            '-sync', 'ext',
            '-autoexit',
            '-window_title', f"Video from {self.sender_ip}",
            '-loglevel', 'warning',  # 将日志级别从verbose改为warning，减少输出
            f'udp://{self.multicast_addr}:{self.video_port}?timeout=5000000&buffer_size=65536'
        ]
        self.log(f"Starting video receiver with command: {' '.join(cmd)}", force=True)
        self.video_process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=self.log_process_errors, args=(self.video_process, "Video Receiver"), daemon=True).start()
        self.log(f"Video receiver started on {self.multicast_addr}:{self.video_port}", force=True)
    
    def start_audio_receiver(self):
        cmd = [
            'ffplay',
            '-fflags', 'nobuffer',
            '-flags', 'low_delay',
            '-framedrop',
            '-sync', 'ext',
            '-nodisp',
            '-autoexit',
            '-loglevel', 'warning',  # 将日志级别从verbose改为warning，减少输出
            f'udp://{self.multicast_addr}:{self.audio_port}?timeout=5000000&buffer_size=65536'
        ]
        self.log(f"Starting audio receiver with command: {' '.join(cmd)}", force=True)
        self.audio_process = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=self.log_process_errors, args=(self.audio_process, "Audio Receiver"), daemon=True).start()
        self.log(f"Audio receiver started on {self.multicast_addr}:{self.audio_port}", force=True)
    
    def log_process_errors(self, process, name):
        """
        处理进程的stderr输出，并过滤掉不必要的FFmpeg状态更新信息
        """
        for line in process.stderr:
            # 过滤掉FFmpeg频繁的状态更新信息
            line_text = line.strip()
            
            # 忽略这些模式的输出
            skip_patterns = [
                # 音频接收器状态更新
                r'M-A:\s+\d+\.\d+ fd=',
                # 视频接收器状态更新
                r'M-V:\s+\w+ fd=',
                # 一般的队列状态更新
                r'aq=\s+\d+KB vq=\s+\d+KB sq=',
                # FFmpeg统计信息
                r'fps=\s+\d+ q=',
                # 非单调DTS消息
                r'Non-monotonous DTS'
            ]
            
            # 检查是否应该跳过这一行
            skip_line = False
            for pattern in skip_patterns:
                if re.search(pattern, line_text):
                    skip_line = True
                    break
            
            # 如果不应该跳过，则记录这一行（这通常是错误或重要警告）
            if not skip_line:
                self.log(f"{name} output: {line_text}", force=True)  # 强制记录错误
    
    def measure_timestamp_latency(self):
        """测量时间戳延迟，抑制频繁日志"""
        try:
            if not self.timestamp_socket:
                self.timestamp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.timestamp_socket.settimeout(2.0)
                # 加入组播组
                self.timestamp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.timestamp_socket.bind(('', self.timestamp_port))
                mreq = socket.inet_aton(self.multicast_addr) + socket.inet_aton('0.0.0.0')
                self.timestamp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                self.log("Timestamp socket initialized", force=True)
            
            # 不记录每次请求的日志
            local_request_time = time.time()
            self.timestamp_socket.sendto(b'LATEST_FRAME', (self.sender_ip, self.timestamp_port))
            data, _ = self.timestamp_socket.recvfrom(1024)
            local_response_time = time.time()
            
            if data == b'NO_FRAMES_AVAILABLE':
                return 0
            
            # 不记录原始时间戳数据
            frame_data = json.loads(data.decode())
            frame_timestamp = datetime.datetime.strptime(frame_data['timestamp'], "%Y-%m-%d %H:%M:%S.%f").timestamp()
            latency = (local_response_time - frame_timestamp) * 1000
            
            # 只有在延迟变化明显时才记录
            if hasattr(self, 'last_reported_latency'):
                if abs(latency - self.last_reported_latency) > 50:  # 延迟变化超过50ms时才记录
                    self.log(f"Latency changed: {latency:.2f} ms", force=True)
                    self.last_reported_latency = latency
            else:
                self.last_reported_latency = latency
                self.log(f"Initial latency: {latency:.2f} ms", force=True)
                
            return latency if 0 <= latency <= 5000 else 0
        except socket.timeout:
            return 0
        except Exception as e:
            self.log(f"Timestamp latency error: {str(e)}", force=True)
            return 0
    
    def start_decision_receiver(self):
        def decision_receiver_thread():
            while self.running:
                try:
                    if not self.decision_socket:
                        self.decision_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.decision_socket.settimeout(5)
                        self.log(f"Attempting to connect to decision service at {self.sender_ip}:{self.decision_port}", force=True)
                        self.decision_socket.connect((self.sender_ip, self.decision_port))
                        self.log(f"Connected to decision service at {self.sender_ip}:{self.decision_port}", force=True)
                    
                    self.decision_socket.sendall(b'GET_DECISION')
                    response = self.decision_socket.recv(1024)
                    if response:
                        decision_data = json.loads(response.decode())
                        old_mode = self.processing_mode
                        old_code = self.mode_code
                        
                        self.processing_mode = decision_data.get("mode", "Unknown")
                        self.mode_code = decision_data.get("mode_code", -1)
                        self.s11_mean = decision_data.get("s11_mean", 0)
                        self.defuzzified_value = decision_data.get("defuzzified_value", 0)
                        self.last_decision_time = time.time()
                        self.s11_history.append(self.s11_mean)
                        
                        # 只在模式发生变化时记录日志
                        if old_mode != self.processing_mode or old_code != self.mode_code:
                            self.log(f"Decision changed: {self.processing_mode} (S11: {self.s11_mean:.2f} dB)", force=True)
                        
                        if self.decision_callback:
                            # Use a try block to safely call the callback
                            try:
                                self.decision_callback(decision_data)
                            except Exception as e:
                                print(f"Error in decision callback: {str(e)}")
                    else:
                        self.log("No decision data received", force=True)
                        self.decision_socket.close()
                        self.decision_socket = None
                except Exception as e:
                    self.log(f"Decision receiver error: {str(e)}", force=True)
                    if self.decision_socket:
                        self.decision_socket.close()
                        self.decision_socket = None
                    time.sleep(5)
                time.sleep(2)
        
        self.decision_thread = threading.Thread(target=decision_receiver_thread, daemon=True)
        self.decision_thread.start()
    
    def get_stream_info(self):
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-probesize', '1000000',
                '-analyzeduration', '2000000',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=r_frame_rate,avg_frame_rate',
                '-of', 'json',
                f'udp://{self.multicast_addr}:{self.video_port}?timeout=5000000'
            ]
            self.log(f"Running ffprobe: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if 'streams' in data and data['streams']:
                    r_frame_rate = data['streams'][0].get('r_frame_rate', '0/1')
                    num, den = map(int, r_frame_rate.split('/'))
                    if den != 0:
                        self.video_fps = int(num / den)
                        self.log(f"Detected framerate: {self.video_fps} fps", force=True)
                else:
                    self.log("No stream info available", force=True)
            else:
                self.log(f"ffprobe failed: {result.stderr}", force=True)
        except subprocess.TimeoutExpired:
            self.log("ffprobe timed out", force=True)
        except Exception as e:
            self.log(f"Stream info error: {str(e)}", force=True)
    
    def start_frame_counter(self):
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-probesize', '1000000',
            '-analyzeduration', '2000000',
            '-show_entries', 'frame=pkt_size,pkt_pts_time',
            '-of', 'csv',
            f'udp://{self.multicast_addr}:{self.video_port}?timeout=5000000'
        ]
        self.log(f"Starting frame counter with: {' '.join(cmd)}")
        self.monitor_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        threading.Thread(target=self.read_frame_data, args=(self.monitor_process.stdout,), daemon=True).start()
        threading.Thread(target=self.log_process_errors, args=(self.monitor_process, "Frame Counter"), daemon=True).start()
    
    def read_frame_data(self, stdout):
        """读取帧数据，只在重大变化时记录日志"""
        last_fps = 0
        frame_log_interval = 60  # 每60秒只记录一次帧率
        last_frame_log = 0
        
        while self.running and self.monitor_process and self.monitor_process.poll() is None:
            try:
                line = stdout.readline().strip()
                if line:
                    current_time = time.time()
                    self.frame_times.append(current_time)
                    self.frame_times = [t for t in self.frame_times if current_time - t <= 1.0]
                    self.video_fps = len(self.frame_times)
                    
                    # 只在帧率有重大变化(超过5帧)或者经过了日志间隔时间时才记录
                    fps_changed = abs(self.video_fps - last_fps) > 5
                    time_to_log = current_time - last_frame_log >= frame_log_interval
                    
                    if fps_changed or time_to_log:
                        self.log(f"Frame rate update: {self.video_fps} FPS", force=True)
                        last_fps = self.video_fps
                        last_frame_log = current_time
            except Exception as e:
                self.log(f"Frame data error: {str(e)}", force=True)
                time.sleep(0.1)
    
    def start_quality_monitor(self):
        self.get_stream_info()
        self.start_frame_counter()
        threading.Thread(target=self.start_network_monitor, daemon=True).start()
    
    def start_network_monitor(self):
        net_io_counters_start = psutil.net_io_counters()
        start_time = time.time()
        last_timestamp_check = 0
        log_interval = 60  # 降低网络日志记录间隔到60秒
        last_network_log = 0
        
        while self.running:
            time.sleep(1)
            current_time = time.time()
            elapsed = current_time - start_time
            elapsed_since_start = current_time - self.start_timestamp
            
            net_io_counters = psutil.net_io_counters()
            bytes_recv = net_io_counters.bytes_recv - net_io_counters_start.bytes_recv
            recv_rate = (bytes_recv * 8) / (1024 * elapsed)
            self.video_bitrate = int(recv_rate * 0.9)
            self.audio_bitrate = int(recv_rate * 0.1)
            net_io_counters_start = net_io_counters
            start_time = current_time
            
            # 降低网络状态日志输出频率
            if current_time - last_network_log >= log_interval:
                self.log(f"Network stats - Video bitrate: {self.video_bitrate} kbps, Audio bitrate: {self.audio_bitrate} kbps", force=True)
                last_network_log = current_time
            
            if current_time - last_timestamp_check >= 2:
                timestamp_latency = self.measure_timestamp_latency()
                if timestamp_latency > 0:
                    self.video_latency = timestamp_latency
                    self.audio_latency = timestamp_latency
                else:
                    ping_latency = measure_latency(self.sender_ip, None)  # 不记录ping日志
                    if ping_latency > 0:
                        self.video_latency = ping_latency
                        self.audio_latency = ping_latency
                    self.packet_loss = 0 if ping_latency < 999 else 100
                last_timestamp_check = current_time
            
            self.timestamps.append(elapsed_since_start)
            self.bitrate_history.append(self.video_bitrate + self.audio_bitrate)
            self.latency_history.append(self.video_latency)
            
            if self.metrics_callback:
                metrics = {
                    'video_bitrate': self.video_bitrate,
                    'audio_bitrate': self.audio_bitrate,
                    'total_bitrate': self.video_bitrate + self.audio_bitrate,
                    'video_fps': self.video_fps,
                    'video_latency': self.video_latency,
                    'audio_latency': self.audio_latency,
                    'packet_loss': self.packet_loss,
                    'connected': self.video_process and self.video_process.poll() is None,
                    'timestamps': list(self.timestamps),
                    'bitrate_history': list(self.bitrate_history),
                    'latency_history': list(self.latency_history),
                    's11_history': list(self.s11_history)
                }
                try:
                    self.metrics_callback(metrics)
                except Exception as e:
                    print(f"Error in metrics callback: {str(e)}")
    
    def record(self, duration=3):
        if self.recording:
            self.log("Already recording", force=True)
            return False
        
        if not self.running:
            self.log("Receiver not running", force=True)
            return False
        
        self.recording = True
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = os.path.join(self.recording_dir, f"video_{timestamp}.mp4")
        audio_filename = os.path.join(self.recording_dir, f"audio_{timestamp}.wav")
        info_filename = os.path.join(self.recording_dir, f"info_{timestamp}.json")
        
        self.log(f"Starting recording to {video_filename} and {audio_filename}", force=True)
        
        # Save the current enhancement mode information
        enhancement_info = {
            "timestamp": timestamp,
            "mode": self.processing_mode,
            "mode_code": self.mode_code, 
            "s11_mean": self.s11_mean,
            "defuzzified_value": self.defuzzified_value
        }
        
        try:
            with open(info_filename, 'w') as f:
                json.dump(enhancement_info, f, indent=4)
            self.log(f"Saved enhancement info to {info_filename}", force=True)
        except Exception as e:
            self.log(f"Error saving enhancement info: {str(e)}", force=True)
        
        video_thread = threading.Thread(
            target=self.record_video_stream,
            args=(video_filename, duration, self.multicast_addr, self.video_port),
            daemon=True
        )
        audio_thread = threading.Thread(
            target=self.record_audio_stream,
            args=(audio_filename, duration, self.multicast_addr, self.audio_port),
            daemon=True
        )
        video_thread.start()
        audio_thread.start()
        
        # Wait for recording to complete
        time.sleep(duration + 1)
        self.recording = False
        return True
    
    def record_video_stream(self, output_file, duration, multicast_addr, video_port):
        if not check_directory_permissions(os.path.dirname(output_file), None):  # 不记录检查日志
            self.log("Video recording aborted: directory not writable", force=True)
            self.recording = False
            return
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', f'udp://{multicast_addr}:{video_port}?timeout=5000000&buffer_size=65536',
            '-t', str(duration),
            '-c:v', 'copy',
            '-an',
            '-fflags', '+genpts',
            '-avoid_negative_ts', 'make_zero',
            '-loglevel', 'warning',  # 降低日志级别
            output_file
        ]
        self.log(f"Starting video recording with command: {' '.join(cmd)}", force=True)
        self.record_process_video = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=self.log_process_errors, args=(self.record_process_video, "Video Recording"), daemon=True).start()
        self.log(f"Started video recording to {output_file}", force=True)
        self.record_process_video.wait()
        if self.record_process_video.returncode == 0:
            self.log(f"Video recording completed: {output_file}", force=True)
        else:
            self.log(f"Video recording failed with exit code {self.record_process_video.returncode}", force=True)
        self.recording = False
    
    def record_audio_stream(self, output_file, duration, multicast_addr, audio_port):
        if not check_directory_permissions(os.path.dirname(output_file), None):  # 不记录检查日志
            self.log("Audio recording aborted: directory not writable", force=True)
            self.recording = False
            return
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', f'udp://{multicast_addr}:{audio_port}?timeout=5000000&buffer_size=65536',
            '-t', str(duration),
            '-vn',
            '-ar', '16000',
            '-ac', '1',
            '-acodec', 'pcm_s16le',
            '-fflags', '+genpts',
            '-loglevel', 'warning',  # 降低日志级别
            output_file
        ]
        self.log(f"Starting audio recording with command: {' '.join(cmd)}", force=True)
        self.record_process_audio = subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True)
        threading.Thread(target=self.log_process_errors, args=(self.record_process_audio, "Audio Recording"), daemon=True).start()
        self.log(f"Started audio recording to {output_file}", force=True)
        self.record_process_audio.wait()
        if self.record_process_audio.returncode == 0:
            self.log(f"Audio recording completed: {output_file}", force=True)
        else:
            self.log(f"Audio recording failed with exit code {self.record_process_audio.returncode}", force=True)
    
    def start(self):
        self.running = True
        self.start_timestamp = time.time()
        self.log("Starting StreamReceiver", force=True)
        threading.Thread(target=self.start_video_receiver, daemon=True).start()
        time.sleep(1)
        threading.Thread(target=self.start_audio_receiver, daemon=True).start()
        time.sleep(1)
        self.start_decision_receiver()
        self.start_quality_monitor()
    
    def stop(self):
        self.running = False
        self.log("Stopping receiver", force=True)
        
        # Stop the thread-safe logger
        self.thread_safe_logger.stop()
        
        if self.timestamp_socket:
            self.timestamp_socket.close()
        
        for process in [self.video_process, self.audio_process, self.monitor_process, self.record_process_video, self.record_process_audio]:
            if process and process.poll() is None:
                self.log(f"Terminating process {process.pid}", force=True)
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    self.log(f"Process {process.pid} killed after timeout", force=True)
        
        if self.decision_socket:
            self.decision_socket.close()