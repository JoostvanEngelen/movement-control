import os
import time
import sys
import clr
import threading
import numpy as np
import threading
import PySimpleGUI as sg

from misc_functions import *

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
# from Thorlabs.MotionControl.
from System import Decimal  # necessary for real world units


class LTS300:
    def __init__(self, ID: str, serial_num: str, settings_dic: dict, window) -> None:
        self.ID = ID
        self.axis = ID[0]
        self.serial_num = serial_num
        self.settings_dic = settings_dic
        self.connected = False
        self.connection_tries = 0
        self.zero_point = 0

        # Connect to device
        self.device = LongTravelStage.CreateLongTravelStage(self.serial_num)

        while self.connected == False and self.connection_tries < 10:
            # print(f'Attempting connecting to stage {self.ID}. Attempt {self.connection_tries+1} / {self.settings_dic["max_connect_attempts"]}')
            window.refresh()
            self.connection_tries += 1
            try:
                self.device.Connect(serial_num)
                print(f'Enabled connection with LTS with ID {self.ID} and serial number {self.serial_num}')
                window.refresh()
                self.connected = True
            except Exception as exception:
                # print(f'Exception raised when trying to connect to LTS device {self.ID}: {exception}')
                time.sleep(0.25)
                self.device = LongTravelStage.CreateLongTravelStage(self.serial_num)
                pass

        if not self.connected:
            print(f'Device {self.ID} ({self.serial_num}) seems unconnectable after {self.connection_tries} attempts. \n Please Try again. Closing program.')
            window.refresh()
            time.sleep(2)
            exit()
        

        # Ensure that the device settings have been initialized
        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.device.IsSettingsInitialized() is True

        # Start polling and enable
        self.device.StartPolling(settings_dic['polling_rate'])
        time.sleep(settings_dic['polling_rate'] * 2 / 1000)  # Wait for two polling cycles
        self.device.EnableDevice()
        time.sleep(settings_dic['polling_rate'] * 2 / 1000)  # Wait for device to enable
        

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
        jog_params = self.device.GetJogParams()
        jog_params.StepSize = Decimal(self.settings_dic['jog_step_size'])
        jog_params.MaxVelocity = Decimal(self.settings_dic['jog_velocity'])
        # jog_params.JogMode = ControlParameters.JogParametersBase.JogModes.SingleStep
        self.device.SetJogParams(jog_params)


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
        if position < self.settings_dic['safety_margin'] or position > 300 - self.settings_dic['safety_margin']:
            print('Move command (move to {position}) exceeds safety margins of the linear stage. Ignoring command')
            return
        try:
            self.device.MoveTo(Decimal(position), self.settings_dic['move_timeout'])
        except Exception as exception:
            print(f'Exception raised when moving LTS device {self.ID}: {exception}')

    def move_to_thread(self, position):
        thread = threading.Thread(target=self.move_to, args=(position,))
        thread.start()
        return thread
    
    def abort_movement(self):
        self.device.StopImmediate()

    def set_zero(self, position):
        self.zero_point = position

    def jog(self, direction, distance):
        old_jog_params = self.device.GetJogParams()
        jog_params = old_jog_params
        jog_params.StepSize = Decimal(distance)
        self.device.SetJogParams(jog_params)

        try:
            self.device.MoveJog(Decimal(direction), self.settings_dic['move_timeout'])
        except Exception as exception:
            print(f'Exception raised when jogging LTS device {self.ID}: {exception}')

        self.device.SetJogParams(old_jog_params)

    def jog_thread(self, direction, distance):
        thread = threading.Thread(target=self.jog, args=(direction, distance,))
        thread.start()
        return thread

    

    # def move_to_relative(self, position):
    #     absolute_position = self.zero_point + position

    #     if absolute_position < self.settings_dic['safety_margin'] or absolute_position > 300 - self.settings_dic['safety_margin']:
    #         print('Move command (move to {position}) exceeds safety margins of the linear stage. Ignoring command')
    #         return
    #     try:
    #         self.device.MoveTo(Decimal(absolute_position), self.settings_dic['move_timeout'])
    #     except Exception as exception:
    #         print(f'Exception raised when moving LTS device {self.ID}: {exception}')

    # def move_to_relative_thread(self, position):
    #     thread = threading.Thread(target=self.move_to_relative, args=(position,))
    #     thread.start()
    #     return thread


class LTS300System:
    def __init__(self, serial_nums: dict, settings_dic: dict, window) -> None:
        self.serial_nums = serial_nums
        self.IDs = [i for i in self.serial_nums.keys()]
        self.axes = {i: i[0] for i in self.serial_nums.keys()}
        self.stages = {}
        self.settings_dic = settings_dic
        self.homed = False
        self.movement_in_progress = False
        self.safety_margin = settings_dic['safety_margin']
        self.zero_points = {
            'x1': 0.0,
            'x2': 0.0,
            'y1': 0.0,
            'y2': 0.0
        }

        for ID in self.IDs:
            self.stages[ID] = LTS300(ID, serial_nums[ID], settings_dic, window)
            window.refresh()
            

    def terminate(self):
        for ID in self.IDs:
            self.stages[ID].terminate()
            print(f'Terminated connection with LTS with ID {ID} and serial number {self.serial_nums[ID]}')

    def home(self, window):
        self.movement_in_progress = True
        threads = []
        for ID in self.IDs:
            thread = self.stages[ID].home_thread()
            threads.append(thread)
        for thread in threads:
            thread.join()
        self.movement_in_progress = False
        window.write_event_value('-HOMING DONE-', '')
        self.homed = True
        self.set_zero_here()

    def home_window_thread(self, window):
        threading.Thread(target=self.home, args=(window, ), daemon=True).start()

    def move_to_absolute_position(self, target_position:dict, window):
        if not self.homed:
            print('The stages have not been homed yet. Please home the stages before proceeding.')
            return

        if not self.get_absolute_target_position_safety(target_position):
            return

        threads = []
        for ID in self.IDs:
            threads.append(self.stages[ID].move_to_thread(target_position[ID]))
        for thread in threads:
            thread.join()
        window.write_event_value('-MOVING DONE-', '')  

    def move_to_absolute_position_thread(self, target_position:dict, window):
        threading.Thread(target=self.move_to_absolute_position, args=(target_position, window)).start()

    def move_to_relative_position_thread(self, relative_target_position:dict, window):
        absolute_target_position = {ID: relative_target_position[ID] + self.zero_points[ID] for ID in self.IDs}
        threading.Thread(target=self.move_to_absolute_position, args=(absolute_target_position, window)).start()

    def set_zero(self, position_dic:dict):
        for ID in self.IDs:
            self.stages[ID].set_zero(position_dic[ID])
            self.zero_points[ID] = position_dic[ID]

    def set_zero_here(self):
        position_dic = self.get_absolute_position_dic()
        self.set_zero(position_dic)

    def abort_movement(self):
        self.homed = False
        for ID in self.IDs:
            self.stages[ID].device.StopImmediate()

    def get_absolute_position_dic(self):
        return {ID: float(str(self.stages[ID].device.Position)) for ID in self.IDs}

    def get_relative_position_dic(self):
        return {ID: float(str(self.stages[ID].device.Position)) - self.zero_points[ID] for ID in self.IDs}

    def relative_to_absolute_position(self, relative_position):
        return {ID: relative_position[ID] + self.zero_points[ID] for ID in self.IDs}

    def absolute_to_relative_position(self, absolute_position):
        return {ID: absolute_position[ID] - self.zero_points[ID] for ID in self.IDs}

    def get_relative_target_position_safety(self, relative_target_position):
        if relative_target_position is None:
            return False
        absolute_target_position = self.relative_to_absolute_position(relative_target_position)
        return self.get_absolute_target_position_safety(absolute_target_position)

    def get_absolute_target_position_safety(self, absolute_target_position):
        if absolute_target_position is None:
            return False
        for id in self.IDs:
            if absolute_target_position[id] > 300 - self.safety_margin or absolute_target_position[id] < self.safety_margin:
                return False
        return True

    def create_target_position_jogging(self, affected_axes, distance, direction):
        current_absolute_position = self.get_absolute_position_dic()
        absolute_target_position = {}
        for id in self.IDs:
            if affected_axes[id] == True:
                absolute_target_position[id] = current_absolute_position[id] + direction * distance
            else:
                absolute_target_position[id] = current_absolute_position[id]
        return absolute_target_position
        

        

        
