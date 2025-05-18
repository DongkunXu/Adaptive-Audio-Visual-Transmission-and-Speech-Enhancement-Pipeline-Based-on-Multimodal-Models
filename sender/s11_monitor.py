#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real-time PocketVNA S11 Monitoring and Processing Mode Selection Module
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'pocketvna_api'))
import pocketvna

import numpy as np
import math
import time
import skfuzzy as fuzz

class S11Monitor:
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
        self.defuzzified_value = 0
        
        # Initialize fuzzy logic system parameters
        self.x_CL = np.arange(-85, -25, 0.1)
        self.y_SE = np.arange(0, 46, 1)
        
        # Create fuzzy membership functions
        self.init_fuzzy_sets()
        
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

    def measure_s11(self):
        """Measure S11 value"""
        try:
            # Create driver instance
            driver = pocketvna.Driver()
            
            # Check device connection
            if driver.count() < 1:
                print('No device detected.')
                return False
            
            # Connect to the first device
            if not driver.connect_to_first(pocketvna.ConnectionInterfaceCode.CIface_HID):
                print('HID connection failed')
                return False
            
            # Validate connection
            if not driver.valid():
                print('Connection invalid. Device may be disconnected.')
                return False
            
            # Calculate frequency range
            freq = [self.start_freq + i * (self.end_freq - self.start_freq) / (self.num_of_points - 1) 
                    for i in range(self.num_of_points)]
            
            # Execute S11 scan
            s11, _, _, _ = driver.scan(freq, 10, pocketvna.NetworkParams.S11)
            
            # Convert S11 to dB
            s11_db = [20 * math.log10(math.sqrt(s.real**2 + s.imag**2)) for s in s11]
            
            # Calculate minimum, maximum and average values
            self.s11_min = min(s11_db)
            self.s11_max = max(s11_db)
            self.s11_mean = sum(s11_db) / len(s11_db)
            
            # Close connection
            driver.close()
            
            return True
            
        except Exception as e:
            print(f"Measurement error: {e}")
            return False
        finally:
            pocketvna.close_api()

    def evaluate_fuzzy_logic(self):
        """Execute fuzzy logic reasoning and return processing mode"""
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
        self.defuzzified_value = fuzz.defuzz(self.y_SE, out_SE, 'centroid')
        
        # Determine processing mode based on defuzzified value
        if self.defuzzified_value >= 39:
            self.mode = "Advanced AV Mode"
            mode_code = 4
        elif 25 <= self.defuzzified_value < 39:
            self.mode = "Standard AV Mode"
            mode_code = 3
        elif 12 <= self.defuzzified_value < 25:
            self.mode = "Light AV Mode"
            mode_code = 2
        elif 9 <= self.defuzzified_value < 12:
            self.mode = "Audio-Only Enhancement Mode"
            mode_code = 1
        else:
            self.mode = "No Enhancement Mode"
            mode_code = 0
            
        return {
            "mode": self.mode,
            "mode_code": mode_code,
            "s11_mean": self.s11_mean,
            "defuzzified_value": self.defuzzified_value
        }

    
    def get_current_status(self):
        """Get current S11 measurement and processing mode decision"""
        if self.measure_s11():
            decision = self.evaluate_fuzzy_logic()
            print(f"S11: {self.s11_mean:.2f} dB | Processing Mode: {self.mode}")
            return decision
        else:
            # 当无法获取S11数据时，默认选择"Advanced AV Mode"
            print("S11 measurement failed, defaulting to Advanced AV Mode")
            return {
                "mode": "Advanced AV Mode",
                "mode_code": 4,            # 对应Advanced AV Mode的代码
                "s11_mean": -30,           # 设置一个较差的S11值，表示信道质量较差
                "defuzzified_value": 40    # 高于39的值会触发Advanced AV Mode
            }
 