#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time PocketVNA S11 Monitoring and Processing Mode Selection Script
修复版 - 使用可用的接口类型
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'pocketvna_api'))
import pocketvna

import numpy as np
import math
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Set matplotlib to display text
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'WenQuanYi Micro Hei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False    # To display negative sign correctly

class PocketVNAMonitor:
    def __init__(self):
        # Initialize parameters
        self.start_freq = 1.5e9  # 1.5 GHz
        self.end_freq = 3e9      # 3 GHz
        self.num_of_points = 100  # Number of frequency points
        
        # Initialize S11 values
        self.s11_min = 0
        self.s11_max = 0
        self.s11_mean = 0
        self.mode = "Unknown"
        
        # Initialize fuzzy logic system parameters
        self.x_CL = np.arange(-85, -25, 0.1)
        self.y_SE = np.arange(0, 46, 1)
        
        # 添加调试信息 - 显示当前工作目录和PocketVNA API版本信息
        print(f"当前工作目录: {os.getcwd()}")
        print(f"PocketVNA API版本: {getattr(pocketvna, 'version', '未知')}")
        print(f"Python版本: {sys.version}")
        
        # 查找并打印可用的接口类型
        self.available_interfaces = [item for item in dir(pocketvna.ConnectionInterfaceCode) if not item.startswith('_')]
        print(f"可用的接口类型: {', '.join(self.available_interfaces)}")
        
        # Create fuzzy membership functions
        self.init_fuzzy_sets()
        
        # Create GUI interface
        self.init_figure()
        
    def init_fuzzy_sets(self):
        """Initialize fuzzy sets"""
        # CL (Channel Loss) membership functions
        self.CL_low = fuzz.trapmf(self.x_CL, [-85, -75, -65, -60])
        self.CL_mid = fuzz.trapmf(self.x_CL, [-55, -50, -45, -40])
        self.CL_high = fuzz.trapmf(self.x_CL, [-35, -30, -25, -20])
        
        # SE (Speech Enhancement) membership functions
        self.SE_not = fuzz.trapmf(self.y_SE, [0, 0, 5, 10])
        self.SE_little = fuzz.trapmf(self.y_SE, [5, 10, 15, 20])
        self.SE_mid = fuzz.trapmf(self.y_SE, [15, 20, 25, 30])
        self.SE_high = fuzz.trapmf(self.y_SE, [25, 30, 35, 40])
        self.SE_veryHigh = fuzz.trapmf(self.y_SE, [35, 40, 45, 50])

    def init_figure(self):
        """Initialize GUI interface"""
        self.fig, self.axs = plt.subplots(2, 1, figsize=(10, 8))
        
        # S11 real-time value display
        self.axs[0].set_title('S11 Measurement')
        self.axs[0].set_xlabel('Time (seconds)')
        self.axs[0].set_ylabel('S11 (dB)')
        self.axs[0].set_ylim(-80, -20)
        self.axs[0].grid(True)
        
        # Fuzzy logic and processing mode display
        self.axs[1].set_title('Fuzzy Logic Output')
        self.axs[1].set_xlabel('Speech Enhancement Value')
        self.axs[1].set_ylim(0, 1.1)
        self.axs[1].grid(True)
        
        # Data storage
        self.times = []
        self.s11_values = []
        self.line, = self.axs[0].plot([], [], 'b-')
        self.mode_text = self.axs[0].text(0.02, 0.9, '', transform=self.axs[0].transAxes)
        
        plt.tight_layout()

    def try_connect_with_interface(self, driver, interface_code, interface_name):
        """尝试使用特定接口连接设备"""
        print(f"尝试使用 {interface_name} 接口连接...")
        try:
            if driver.connect_to_first(interface_code):
                print(f"成功通过 {interface_name} 接口连接！")
                return True
            else:
                print(f"{interface_name} 连接失败")
                return False
        except Exception as e:
            print(f"使用 {interface_name} 接口连接时出错: {e}")
            return False

    def measure_s11(self):
        """Measure S11 value"""
        try:
            # Create driver instance
            driver = pocketvna.Driver()
            
            # Check device connection
            device_count = driver.count()
            print(f"检测到 {device_count} 个设备")
            if device_count < 1:
                print('未检测到设备。请检查USB连接或udev规则。')
                
                # 添加调试信息 - 检查USB设备
                os.system("echo '检查USB设备列表:'")
                os.system("lsusb | grep -i vna")
                os.system("echo '检查hidraw设备:'")
                os.system("ls -la /dev/hidraw*")
                return False
            
            # 尝试可用接口连接设备
            connected = False
            
            # 尝试HID接口
            if "CIface_HID" in self.available_interfaces:
                if self.try_connect_with_interface(driver, pocketvna.ConnectionInterfaceCode.CIface_HID, "HID"):
                    connected = True
            
            # 尝试VCI接口
            if not connected and "CIface_VCI" in self.available_interfaces:
                if self.try_connect_with_interface(driver, pocketvna.ConnectionInterfaceCode.CIface_VCI, "VCI"):
                    connected = True
            
            # 如果有其他接口，也尝试使用
            for iface in self.available_interfaces:
                if not connected and iface not in ["CIface_HID", "CIface_VCI"]:
                    try:
                        interface_code = getattr(pocketvna.ConnectionInterfaceCode, iface)
                        if self.try_connect_with_interface(driver, interface_code, iface):
                            connected = True
                            break
                    except Exception as e:
                        print(f"尝试 {iface} 接口时出错: {e}")
            
            if not connected:
                print('所有接口连接尝试都失败')
                print('请检查设备权限和驱动是否正确安装')
                
                # 添加更多关于HID权限的调试信息
                print("\n调试HID接口权限问题:")
                print("检查当前用户组:")
                os.system("groups")
                
                print("\n当前用户是否在plugdev组中:")
                os.system("groups | grep plugdev")
                
                print("\n检查hidraw设备权限:")
                os.system("ls -la /dev/hidraw*")
                
                # 尝试直接访问hidraw设备
                try:
                    with open('/dev/hidraw0', 'rb') as f:
                        print("可以打开hidraw设备进行读取")
                except Exception as e:
                    print(f"无法访问hidraw设备: {e}")
                
                return False
            
            # Validate connection
            if not driver.valid():
                print('连接无效。设备可能已断开连接。')
                return False
            else:
                print('连接有效，准备进行测量')
            
            # Calculate frequency range
            freq = [self.start_freq + i * (self.end_freq - self.start_freq) / (self.num_of_points - 1) 
                    for i in range(self.num_of_points)]
            
            print(f"正在扫描频率范围: {self.start_freq/1e9}GHz 至 {self.end_freq/1e9}GHz，共 {self.num_of_points} 个点")
            
            # Execute S11 scan
            print("开始S11扫描...")
            s11, _, _, _ = driver.scan(freq, 10, pocketvna.NetworkParams.S11)
            print(f"扫描完成，获取了 {len(s11)} 个数据点")
            
            # Convert S11 to dB
            s11_db = [20 * math.log10(math.sqrt(s.real**2 + s.imag**2)) for s in s11]
            
            # Calculate minimum, maximum and average values
            self.s11_min = min(s11_db)
            self.s11_max = max(s11_db)
            self.s11_mean = sum(s11_db) / len(s11_db)
            
            print(f"S11统计: 最小值 = {self.s11_min:.2f}dB, 最大值 = {self.s11_max:.2f}dB, 平均值 = {self.s11_mean:.2f}dB")
            
            # Close connection
            driver.close()
            print("设备连接已关闭")
            
            return True
            
        except Exception as e:
            print(f"测量错误: {e}")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误发生位置: {__file__}:{sys._getframe().f_lineno}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            try:
                pocketvna.close_api()
                print("API已关闭")
            except Exception as e:
                print(f"关闭API时发生错误: {e}")

    def evaluate_fuzzy_logic(self):
        """Execute fuzzy logic reasoning"""
        # Fuzzification
        CL_fit_low = fuzz.interp_membership(self.x_CL, self.CL_low, self.s11_mean)
        CL_fit_mid = fuzz.interp_membership(self.x_CL, self.CL_mid, self.s11_mean)
        CL_fit_high = fuzz.interp_membership(self.x_CL, self.CL_high, self.s11_mean)
        
        # Rule evaluation
        rule1 = np.fmin(CL_fit_low, self.SE_not)
        rule2 = np.fmin(CL_fit_mid, self.SE_little)
        rule3 = np.fmin(CL_fit_high, self.SE_high)
        
        # Aggregate rule outputs
        out_SE = np.fmax(np.fmax(rule1, rule2), rule3)
        
        # Defuzzification
        defuzzified = fuzz.defuzz(self.y_SE, out_SE, 'centroid')
        result = fuzz.interp_membership(self.y_SE, out_SE, defuzzified)
        
        # Display fuzzy logic output
        self.axs[1].clear()
        self.axs[1].plot(self.y_SE, self.SE_not, 'r', linewidth=0.5, linestyle='--', label='No Enhancement')
        self.axs[1].plot(self.y_SE, self.SE_little, 'g', linewidth=0.5, linestyle='--', label='Light Enhancement')
        self.axs[1].plot(self.y_SE, self.SE_high, 'b', linewidth=0.5, linestyle='--', label='High Enhancement')
        self.axs[1].fill_between(self.y_SE, 0, out_SE, facecolor='Orange', alpha=0.7)
        self.axs[1].plot([defuzzified, defuzzified], [0, result], 'k', linewidth=1.5, alpha=0.9)
        self.axs[1].set_title('Fuzzy Logic Output')
        self.axs[1].set_xlabel('Speech Enhancement Value')
        self.axs[1].set_ylabel('Membership')
        self.axs[1].legend()
        
        # Determine processing mode based on defuzzified value
        if defuzzified >= 39:
            self.mode = "Advanced AV Mode"
        elif 25 <= defuzzified < 39:
            self.mode = "Standard AV Mode"
        elif 12 <= defuzzified < 25:
            self.mode = "Light AV Mode"
        elif 9 <= defuzzified < 12:
            self.mode = "Audio-Only Enhancement Mode"
        else:
            self.mode = "No Enhancement Mode"
            
        return defuzzified

    def update(self, frame):
        """Update function for animation"""
        # Measure S11
        if self.measure_s11():
            current_time = len(self.times)
            self.times.append(current_time)
            self.s11_values.append(self.s11_mean)
            
            # Limit displayed data points
            if len(self.times) > 50:
                self.times = self.times[-50:]
                self.s11_values = self.s11_values[-50:]
            
            # Update S11 graph
            self.line.set_data(self.times, self.s11_values)
            self.axs[0].set_xlim(min(self.times), max(self.times) + 1)
            
            # Evaluate fuzzy logic
            defuzzified = self.evaluate_fuzzy_logic()
            
            # Update mode text
            self.mode_text.set_text(f'S11 Average: {self.s11_mean:.2f} dB\nMode: {self.mode}')
            
            # Print to console
            print(f"Time: {current_time}s | S11: {self.s11_mean:.2f} dB | Processing Mode: {self.mode}")
            
        return self.line, self.mode_text

    def run(self):
        """Run monitoring"""
        # Set up animation
        ani = FuncAnimation(self.fig, self.update, frames=None, interval=1000, blit=True, cache_frame_data=False)
        plt.show()


if __name__ == "__main__":
    print("="*80)
    print("启动 PocketVNA S11 实时监控系统（修复版）...")
    print(f"系统使用 PocketVNA API 路径: {os.path.join(os.path.dirname(__file__), 'pocketvna_api')}")
    print("按 Ctrl+C 停止")
    print("="*80)
    
    try:
        print("尝试导入必要模块...")
        # 检查所有需要的模块是否可用
        import matplotlib
        print(f"matplotlib 版本: {matplotlib.__version__}")
        import skfuzzy
        print(f"skfuzzy 版本: {skfuzzy.__version__ if hasattr(skfuzzy, '__version__') else '未知'}")
        import numpy
        print(f"numpy 版本: {numpy.__version__}")
        
        print("所有模块导入成功")
        monitor = PocketVNAMonitor()
        monitor.run()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请验证PocketVNA API安装路径是否正确以及所有依赖项是否已安装")
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n程序已停止")