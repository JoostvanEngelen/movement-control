'''
@author: Joost van Engelen - joost.johannes.van.engelen@cern.ch
'''

import os
import time
import sys
import clr
import threading
import numpy as np

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal  # necessary for real world units

import device_settings
from linear_translation_stage import LTS300, LTS300System


def create_raster_sequence(size, resolution):
    # This is now just a square centered around the middle but could be anything
    xgrid = np.linspace(150 - size/2, 150 + size/2, resolution) 
    ygrid = np.linspace(150 - size/2, 150 + size/2, resolution)
    xscan = []
    yscan = []
    for i, yi in enumerate(ygrid):
        xscan.append(xgrid[::(-1)**i]) # reverse when i is odd
        yscan.append(np.ones_like(xgrid) * yi)
    xscan = np.concatenate(xscan)
    yscan = np.concatenate(yscan)
    sequence = []
    for i in range(len(xscan)):
        sequence.append((xscan[i], yscan[i]))
    return sequence


def measurement_sequence(LTS_system, sequence):
    for x_co, y_co in sequence:
        LTS_system.move_to(x_co, y_co)
        # HERE DO THE MEASUREMENT
        time.sleep(0.5) # this is a replacement for some measurement
    return






serial_nums = {
    'x1': '45294984',
    'y1': '45316884',
    'x2': '45325034',
    'y2': '45332564'
}


DeviceManagerCLI.BuildDeviceList()

LTS_settings_dic = device_settings.generate_LTS_settings_dic()
# motor = LTS300('x1', serial_num, LTS_settings_dic)


combi = LTS300System(serial_nums, LTS_settings_dic)

print('______________________\nsetup complete.\n______________________')

command = ''
while command != 'q':
    print('\noptions: \ntype m: move to coordinates in x and y \ntype h: home\ntype q: quit\ntype r: raster sequence\ntype x: move to middle')
    command = input()
    if command == "m":
        x_co = float(input("x-coordinate (0-300): "))
        y_co = float(input("y-coordinate (0-300): "))
        combi.move_to(x_co, y_co)
        
    
    if command == 'h':
        combi.home()

    if command == 'r':
        size = float(input("size of grid: (0-300): "))
        resolution = int(input("measurements per axis: "))
        sequence = create_raster_sequence(size, resolution)
        measurement_sequence(combi, sequence)

    if command == 'x':
        combi.move_to_middle()

    
    print('_______________________________')

combi.terminate()
print('done')