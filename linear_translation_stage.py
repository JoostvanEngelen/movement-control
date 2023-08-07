import os
import time
import sys
import clr
import threading
import numpy as np
import threading

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal  # necessary for real world units


class LTS300:
    def __init__(self, ID: str, serial_num: str, settings_dic: dict) -> None:
        self.ID = ID
        self.axis = ID[0]
        self.serial_num = serial_num
        self.settings_dic = settings_dic

        # Connect to device
        self.device = LongTravelStage.CreateLongTravelStage(self.serial_num)
        try:
            self.device.Connect(serial_num)
        except Exception as exception:
            print(f'Exception raised when trying to connect to LTS device {self.ID}: {exception}')

        

        # Ensure that the device settings have been initialized
        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.device.IsSettingsInitialized() is True

        # Start polling and enable
        self.device.StartPolling(settings_dic['polling_rate'])
        time.sleep(settings_dic['polling_rate'] * 2 / 1000)  # Wait for two polling cycles
        self.device.EnableDevice()
        time.sleep(settings_dic['polling_rate'] * 2 / 1000)  # Wait for device to enable
        print(f'Enabled connection with LTS with ID {self.ID} and serial number {self.serial_num}')

        # Load info and configurations
        self.device_info = self.device.GetDeviceInfo()
        self.motor_config = self.device.LoadMotorConfiguration(self.serial_num)

        # Set homing parameters
        home_params = self.device.GetHomingParams()
        home_params.Velocity = Decimal(self.settings_dic['home_velocity'])
        self.device.SetHomingParams(home_params)

        # Set movement parameters
        vel_params = self.device.GetVelocityParams()
        vel_params.MaxVelocity = Decimal(self.settings_dic['move_velocity'])
        self.device.SetVelocityParams(vel_params)

        # Set jogging parameters
        # todo: set parameters


    def terminate(self):
        self.device.StopPolling()
        self.device.Disconnect()


    def change_setting(self, setting, value):
        self.settings_dic[setting] = value
        #todo: this only changes the dict 

    def home(self):
        try:
            self.device.Home(self.settings_dic['home_timeout'])
        except Exception as exception:
            print(f'Exception raised when homing LTS device {self.ID}: {exception}')

    def home_thread(self):
        thread = threading.Thread(target=self.home)
        thread.start()
        return thread

    def move_to(self, position):
        try:
            self.device.MoveTo(Decimal(position), self.settings_dic['move_timeout'])
        except Exception as exception:
            print(f'Exception raised when moving LTS device {self.ID}: {exception}')

    def move_to_thread(self, position):
        thread = threading.Thread(target=self.move_to, args=(position,))
        thread.start()
        return thread


class LTS300System:
    def __init__(self, serial_nums: dict, settings_dic: dict) -> None:
        self.serial_nums = serial_nums
        self.IDs = [i for i in self.serial_nums.keys()]
        self.axes = {i: i[0] for i in self.serial_nums.keys()}
        self.stages = {}
        self.homed = False
        for ID in self.IDs:
            self.stages[ID] = LTS300(ID, serial_nums[ID], settings_dic)

    def terminate(self):
        for ID in self.IDs:
            self.stages[ID].terminate()
            print(f'Terminated connection with LTS with ID {ID} and serial number {self.serial_nums[ID]}')

    def home(self):
        threads = []
        for ID in self.IDs:
            thread = self.stages[ID].home_thread()
            threads.append(thread)
        for thread in threads:
            thread.join()
        self.homed = True

    def move_to(self, x_position, y_position):
        if not self.homed:
            print('The stages have not been homed yet. Please home the stages before proceeding.')
            return

        threads = []
        for ID in [ID for ID in self.IDs if self.stages[ID].axis == 'x']:
            threads.append(self.stages[ID].move_to_thread(x_position))
        for ID in [ID for ID in self.IDs if self.stages[ID].axis == 'y']:
            threads.append(self.stages[ID].move_to_thread(y_position))
        # for thread in threads:
        #     thread.join()
        while any(thread.is_alive() for thread in threads):
            if not True:
                for ID in self.motors:
                    self.motors[ID].device.StopImmediate()
                print('All movement of linear stages aborted. Wait for timeout exception...')
                print('You will need to re-home the devices after this.')
            else:
                time.sleep(0.05)

    def move_to_middle(self):
        if not self.homed:
            print('The stages have not been homed yet. Please home the stages before proceeding.')
            return
        threads = []
        for ID in self.IDs:
            threads.append(self.stages[ID].move_to_thread(150))
        for thread in threads:
            thread.join()

        
