import pocketvna_calibration_loader as caliloader


import math
import cmath
import os
import skrf

MATPLOT= None
try:
    import matplotlib.pyplot as plot
    MATPLOT= True
except ImportError:
    MATPLOT= False

# current script's path
dir_path = os.path.dirname(os.path.realpath(__file__))

# Files
CALIBRATION_FILE=dir_path+"/some_tosm.cali"
RAW_DATA_FILE=dir_path+"/some_raw_data.s2p"

# Loading calibration file
loader= caliloader.CalibrationFileLoader(CALIBRATION_FILE)
caliData = loader.parse()

if caliData is None:
    print("Could not load file " + CALIBRATION_FILE)
    exit(1)

# Loading DUT raw data
dut = skrf.Network(RAW_DATA_FILE)


# Generate Ideals and Standards set from a calibration file
my_interpolated_ideals    = caliData.gen_ideal_networks(dut.f)
my_standards = caliData.gen_standard_networks()

# Interpolation is required. Each network in standards is interpolated separately by skrf's built-in functions
#  ## Pay attention: that dut.frequency should be passed. Not dut.f! Because the latter leads to exception
for standard in my_standards:
    standard.interpolate_self(dut.frequency)

# Create skrfs Calibration functor
cal = skrf.SOLT(
    ideals =   my_interpolated_ideals,
    measured = my_standards
)

# Apply calibration
dut_calibrated = cal.apply_cal(dut)

# Plot
if MATPLOT:
    plot.figure(1)
    dut_calibrated.plot_s_db(m=0,n=0, label='S11')

    plot.show()
