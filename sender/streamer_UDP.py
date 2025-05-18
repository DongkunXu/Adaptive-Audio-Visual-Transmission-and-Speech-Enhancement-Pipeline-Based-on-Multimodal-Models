#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Media Streaming and Processing Mode Decision Transmission Module (UDP Multicast)
"""

import subprocess
import threading
import time
import os
import signal
import sys
import datetime
import socket
import json
from s11_monitor import S11Monitor

class MediaStreamer:
    def __init__(self, bind_ip='192.168.1.1', video_port=5100, audio_port=5101, 
                 timestamp_port=5102, decision_port=5103):
        self.bind_ip = bind_ip
        self.video_multicast_addr = '239.0.0.1'  # 多播地址
        self.video_port = video_port
        self.audio_port = audio_port
        self.timestamp_port = timestamp_port
        self.decision_port = decision_port
        self.video_process = None
        self.audio_process = None
        self.timestamp_server = None
        self.decision_server = None
        self.s11_monitor = S11Monitor()
        self.running = False
        self.current_frame_id = 0
        self.frame_timestamps = {}
        
    def start_video_stream(self):
        """启动视频流（UDP 多播）"""
        cmd = [
            'libcamera-vid',
            '-t', '0',
            '--inline',
            '--width', '640',
            '--height', '480',
            '--framerate', '30',
            '--codec', 'h264',
            '--profile', 'baseline',
            '--intra', '5',
            '--bitrate', '1000000',
            '-o', f'udp://{self.video_multicast_addr}:{self.video_port}?ttl=1&localaddr={self.bind_ip}'
        ]
        
        self.video_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Video stream started, multicasting to: {self.video_multicast_addr}:{self.video_port}")
        
    def start_audio_stream(self):
        """启动音频流（UDP 多播）"""
        audio_device = self.detect_audio_device()
        
        cmd = [
            'ffmpeg',
            '-f', 'alsa',
            '-channels', '1',
            '-sample_rate', '16000',
            '-i', audio_device,
            '-acodec', 'aac',
            '-ab', '128k',
            '-ac', '1',
            '-f', 'mpegts',
            f'udp://{self.video_multicast_addr}:{self.audio_port}?ttl=1&localaddr={self.bind_ip}'
        ]
        
        self.audio_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Audio stream started, multicasting to: {self.video_multicast_addr}:{self.audio_port}")
    
    def start_timestamp_server(self):
        """启动时间戳UDP服务器（保持不变）"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server_socket.bind((self.bind_ip, self.timestamp_port))
            print(f"Timestamp service started, bound to: {self.bind_ip}:{self.timestamp_port}")
            
            while self.running:
                data, addr = server_socket.recvfrom(1024)
                
                if data == b'TIMESTAMP':
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                    server_socket.sendto(current_time.encode(), addr)
                elif data.startswith(b'GET_FRAME_'):
                    try:
                        frame_id = int(data.decode().split('_')[-1])
                        if frame_id in self.frame_timestamps:
                            response = json.dumps({
                                'frame_id': frame_id,
                                'timestamp': self.frame_timestamps[frame_id]
                            })
                            server_socket.sendto(response.encode(), addr)
                        else:
                            server_socket.sendto(b'FRAME_NOT_FOUND', addr)
                    except (ValueError, IndexError) as e:
                        print(f"Frame ID parsing error: {e}")
                        server_socket.sendto(b'INVALID_FRAME_ID', addr)
                elif data == b'LATEST_FRAME':
                    if self.frame_timestamps:
                        latest_frame_id = max(self.frame_timestamps.keys())
                        response = json.dumps({
                            'frame_id': latest_frame_id,
                            'timestamp': self.frame_timestamps[latest_frame_id]
                        })
                        server_socket.sendto(response.encode(), addr)
                    else:
                        server_socket.sendto(b'NO_FRAMES_AVAILABLE', addr)
                
        except Exception as e:
            print(f"Timestamp server error: {e}")
        finally:
            if 'server_socket' in locals():
                server_socket.close()
    
    def start_decision_server(self):
        """启动处理模式决策TCP服务器（保持不变）"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.bind_ip, self.decision_port))
            server_socket.listen(5)
            server_socket.settimeout(1.0)
            print(f"Decision service started, bound to: {self.bind_ip}:{self.decision_port}")
            
            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    print(f"Client connected from {addr}")
                    
                    client_thread = threading.Thread(
                        target=self.handle_decision_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    time.sleep(1)
                
        except Exception as e:
            print(f"Decision server error: {e}")
        finally:
            if 'server_socket' in locals():
                server_socket.close()
    
    def handle_decision_client(self, client_socket, addr):
        """处理决策客户端连接（保持不变）"""
        try:
            client_socket.settimeout(5.0)
            
            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    if data == b'GET_DECISION':
                        decision = self.s11_monitor.get_current_status()
                        response = json.dumps(decision)
                        client_socket.sendall(response.encode())
                        
                except socket.timeout:
                    try:
                        client_socket.sendall(b'')
                    except:
                        break
                except Exception as e:
                    print(f"Error handling client {addr}: {e}")
                    break
                
        except Exception as e:
            print(f"Client handler error: {e}")
        finally:
            client_socket.close()
            print(f"Client {addr} disconnected")
    
    def s11_decision_update(self):
        """定期更新S11和处理模式决策（保持不变）"""
        while self.running:
            decision = self.s11_monitor.get_current_status()
            time.sleep(5)
    
    def update_frame_counter(self):
        """更新帧计数器并记录时间戳（保持不变）"""
        while self.running:
            if len(self.frame_timestamps) > 100:
                oldest_frame = min(self.frame_timestamps.keys())
                del self.frame_timestamps[oldest_frame]
                
            self.current_frame_id += 1
            self.frame_timestamps[self.current_frame_id] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            time.sleep(1/30)
    
    def detect_audio_device(self):
        """检测音频录制设备（保持不变）"""
        try:
            result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            print("Available audio devices:")
            print(result.stdout)
            default_device = 'hw:1,0'
            if 'card 2' in result.stdout:
                return 'hw:2,0' 
            elif 'card 1' in result.stdout:
                return default_device
            elif 'card 0' in result.stdout:
                return 'hw:0,0'
            else:
                print("WARNING: No specific audio device detected, using default device")
                return default_device
        except Exception as e:
            print(f"Audio device detection failed: {e}")
            return 'hw:1,0'
    
    def sync_time(self):
        """确保系统时间同步（保持不变）"""
        try:
            print("Synchronizing system time with NTP server...")
            subprocess.run(['sudo', 'systemctl', 'stop', 'chronyd'], check=False)
            subprocess.run(['sudo', 'chronyd', '-q'], check=False)
            subprocess.run(['sudo', 'systemctl', 'start', 'chronyd'], check=False)
            print("Time synchronization completed")
        except Exception as e:
            print(f"Time synchronization failed: {e}")
    
    def start(self):
        """启动所有流服务（保持不变）"""
        self.running = True
        self.sync_time()
        
        video_thread = threading.Thread(target=self.start_video_stream)
        audio_thread = threading.Thread(target=self.start_audio_stream)
        timestamp_thread = threading.Thread(target=self.start_timestamp_server)
        decision_thread = threading.Thread(target=self.start_decision_server)
        s11_update_thread = threading.Thread(target=self.s11_decision_update)
        frame_counter_thread = threading.Thread(target=self.update_frame_counter)
        
        video_thread.daemon = True
        audio_thread.daemon = True
        timestamp_thread.daemon = True
        decision_thread.daemon = True
        s11_update_thread.daemon = True
        frame_counter_thread.daemon = True
        
        video_thread.start()
        time.sleep(2)
        
        audio_thread.start()
        timestamp_thread.start()
        decision_thread.start()
        s11_update_thread.start()
        frame_counter_thread.start()
        
        print("All media streaming services have been started")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止所有流服务（保持不变）"""
        self.running = False
        
        if self.video_process:
            print("Stopping video stream...")
            self.video_process.terminate()
            self.video_process.wait()
            
        if self.audio_process:
            print("Stopping audio stream...")
            self.audio_process.terminate()
            self.audio_process.wait()
            
        print("All streaming services stopped")

if __name__ == "__main__":
    def signal_handler(sig, frame):
        print("Shutting down service...")
        streamer.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    bind_ip = '192.168.1.1'
    if len(sys.argv) > 1:
        bind_ip = sys.argv[1]
    
    streamer = MediaStreamer(bind_ip=bind_ip, video_port=5100, audio_port=5101, 
                            timestamp_port=5102, decision_port=5103)
    print(f"Starting audio and video streaming service, binding to {bind_ip}...")
    streamer.start()