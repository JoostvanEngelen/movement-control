'''
@author: Joost van Engelen - joost.johannes.van.engelen@cern.ch
'''

import os
import time
import sys
import clr
import threading
import numpy as np
import PySimpleGUI as sg
sg.theme("DefaultNoMoreNagging") 

# sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
# print = sg.Print


clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal  # necessary for real world units

import device_settings
from linear_translation_stage import LTS300, LTS300System
import GUI
from misc_functions import *
from aperture import *

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# def create_raster_sequence(midpoint, size, resolution):
#     # This is now just a square centered around the middle but could be anything
#     xgrid = np.linspace(midpoint - size/2, midpoint + size/2, resolution) 
#     ygrid = np.linspace(midpoint - size/2, midpoint + size/2, resolution)
#     xscan = []
#     yscan = []
#     for i, yi in enumerate(ygrid):
#         xscan.append(xgrid[::(-1)**i]) # reverse when i is odd
#         yscan.append(np.ones_like(xgrid) * yi)
#     xscan = np.concatenate(xscan)
#     yscan = np.concatenate(yscan)
#     sequence = []
#     for i in range(len(xscan)):
#         sequence.append((xscan[i], yscan[i]))
#     return sequence


def measurement_sequence(LTS_setup, sequence, window):
    for x_co, y_co in sequence:
        target_position = {
            'x1': x_co,
            'x2': x_co,
            'y1': y_co,
            'y2': y_co
        }
        LTS_setup.move_to_absolute_position(target_position, window)
        # HERE DO THE MEASUREMENT
        time.sleep(0.5) # this is a replacement for some measurement
    return




# to be moved to the GUI.py file later
def place_holder_main_window(LTS_setup):
    sg.theme('Default 1')

    def draw_figure(canvas, figure):
        tkcanvas = FigureCanvasTkAgg(figure, canvas)
        tkcanvas.draw()
        tkcanvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        return tkcanvas

    def create_fig():
        plt.figure(figsize=(3, 3))
        x_vals_bound = [0, 300, 300, 0, 0]
        y_vals_bound = [0, 0, 300, 300, 0]
        plt.text(50, 150, "PLOT NOT ACTIVE")
        plt.plot(x_vals_bound, y_vals_bound, linestyle = "--")        
        return plt.gcf()

    fig = create_fig()

    top_info = [
        [sg.Text("Main Window", size=(20, 1), font=("Helvetica", 16)), sg.Button('home', key='-HOME-'), sg.Button('ABORT MOVEMENT', button_color='red', key='-ABORT-')]
    ]

    col1 = [
        [sg.Text("Device correctly homed:", size=(20,1)), sg.Text("", size=(10, 1), key='-HOMED-')],
        [sg.Text("Absolute Device Position: X1 =", size=(21, 1)), sg.Text("", size=(10, 1), key='-X1_ABS-'),
        sg.Text("Y1 ="), sg.Text("", size=(10, 1), key='-Y1_ABS-')],
        [sg.Text("Absolute Device Position: X1 =", size=(21, 1)), sg.Text("", size=(10, 1), key='-X2_ABS-'),
        sg.Text("Y2 ="), sg.Text("", size=(10, 1), key='-Y2_ABS-')],

        [sg.Text("", size=(20,1))],

        [sg.Text("Relative Device Position: X1 =", size=(21, 1)), sg.Text("", size=(10, 1), key='-X1_REL-'),
        sg.Text("Y1 ="), sg.Text("", size=(10, 1), key='-Y1_REL-')],
        [sg.Text("Relative Device Position: X1 =", size=(21, 1)), sg.Text("", size=(10, 1), key='-X2_REL-'),
        sg.Text("Y2 ="), sg.Text("", size=(10, 1), key='-Y2_REL-')],

        [sg.Button("Go to absolute position", key='-GOTO_ABS-'), 
        sg.Button("Go to relative position", key='-GOTO_REL-')],

        [sg.Text('')],
        
        [sg.Button("Set Zero position", key='SET_ZERO_COOR'), sg.Button("Set Current Position as Zero", key='-CUR_POS_ZERO-')],

        [sg.Text('Jogging:')],
        [sg.Spin([i for i in range(1,10)], initial_value=1, k='-JOG_DIS-'), sg.Text("x 10 ^"), sg.Spin([i for i in range(-3,3)], initial_value=0, k='-JOG_FAC-'), sg.Text("-->"), sg.Text("0", key='-JOG_OUTPUT-')],
        [sg.Text("Affected axes: "), sg.Checkbox('X1', default=True, k='-JOG_X1-'), sg.Checkbox('X2', default=True, k='-JOG_X2-'), sg.Checkbox('Y1', default=False, k='-JOG_Y1-'), sg.Checkbox('Y2', default=False, k='-JOG_Y2-')],
        [sg.Button("Jog positive", key='-JOG_POS-'), sg.Button("Jog negative", key='-JOG_NEG-')]
    ]


    col2 = [
        [sg.Canvas(size = (50, 50), key='-CANVAS-')],

        [sg.Button("Close")]
    ]

    bottom_info = [
        [sg.Text('Raster sequence eliptical aperture:')],
        [sg.Button('Set dimensions and go', k='-RASTER_GO-')]
    ]


    layout = [top_info, [sg.Column(col1), sg.Column(col2)], bottom_info]

    window = sg.Window("Concept", layout, finalize=True, icon='images/favicon.ico')
    tkcanvas = draw_figure(window['-CANVAS-'].TKCanvas, fig)

    # Event loop
    while True:
        event, values = window.read(timeout=.25)

        if event == sg.WIN_CLOSED or event == "Close":
            break


        current_absolute_position = LTS_setup.get_absolute_position_dic()
        current_relative_position = LTS_setup.get_relative_position_dic()
        

        window['-X1_ABS-'].update(value = f'{current_absolute_position["x1"]:.3f}')
        window['-X2_ABS-'].update(value = f'{current_absolute_position["x2"]:.3f}')
        window['-Y1_ABS-'].update(value = f'{current_absolute_position["y1"]:.3f}')
        window['-Y2_ABS-'].update(value = f'{current_absolute_position["y2"]:.3f}')
        window['-X1_REL-'].update(value = f'{current_relative_position["x1"]:.3f}')
        window['-X2_REL-'].update(value = f'{current_relative_position["x2"]:.3f}')
        window['-Y1_REL-'].update(value = f'{current_relative_position["y1"]:.3f}')
        window['-Y2_REL-'].update(value = f'{current_relative_position["y2"]:.3f}')
        window['-HOMED-'].update(value = str(LTS_setup.homed))

        jog_str = f'{values["-JOG_DIS-"] * 10 ** values["-JOG_FAC-"]:.3f} mm'
        window['-JOG_OUTPUT-'].update(value = jog_str)

        window.refresh()


        if event == '-RASTER_GO-':
            aperture_dimensions = GUI.input_aperture_popup()
            raster_step_size = GUI.input_step_size_popup()

            ap_height = aperture_dimensions['height']
            ap_width = aperture_dimensions['width']
            ap_center = (aperture_dimensions['center_x'], aperture_dimensions['center_y'])
            ap_angle = aperture_dimensions['angle']

            if aperture_dimensions['shape'] == 'Elliptical':
                aperture = EllipcicalAperture(ap_height, ap_width, ap_center, ap_angle)
            elif aperture_dimensions['shape'] == 'Rectangular':
                aperture = RectangularAperture(ap_height, ap_width, ap_center, ap_angle)
            
            seq = raster_given_aperture(aperture, raster_step_size)

            measurement_sequence(LTS_setup, seq, window)



            



        if event == '-CUR_POS_ZERO-':
            LTS_setup.set_zero_here()

        if event == 'SET_ZERO_COOR':
            zero_position = GUI.input_coordinates_popup()
            LTS_setup.set_zero(zero_position)

        if event == "-HOME-":
            LTS_setup.home_window_thread(window)
            # print('homing started')

        if event == "-GOTO_REL-":
            target_position = GUI.input_coordinates_popup()
            if target_position == None or target_position == 'None':
                continue
            if LTS_setup.get_relative_target_position_safety(target_position):
                LTS_setup.move_to_relative_position_thread(target_position, window)
            else:
                sg.Popup(f"This target position is not safe.\nAbsolute target: {LTS_setup.relative_to_absolute_position(target_position)}. \nRelative target {target_position}", keep_on_top=True)

        if event == "-GOTO_ABS-":
            target_position = GUI.input_coordinates_popup()
            if target_position == None or target_position == 'None':
                continue
            if LTS_setup.get_absolute_target_position_safety(target_position):
                LTS_setup.move_to_absolute_position_thread(target_position, window)
            else:
                sg.Popup(f"This target position is not safe.\nAbsolute target: {target_position}. \nRelative target {LTS_setup.absolute_to_relative_position(target_position)}", keep_on_top=True)

        if event == "-JOG_POS-":
            affected_axes = {
                'x1': values['-JOG_X1-'],
                'x2': values['-JOG_X2-'],
                'y1': values['-JOG_Y1-'],
                'y2': values['-JOG_Y2-'],
            }
            distance = values['-JOG_DIS-'] * 10 ** values['-JOG_FAC-']
            target_position = LTS_setup.create_target_position_jogging(affected_axes, distance, 1)

            if LTS_setup.get_absolute_target_position_safety(target_position):
                LTS_setup.move_to_absolute_position_thread(target_position, window)
            else:
                sg.Popup(f"This target position is not safe.\nAbsolute target: {target_position}. \nRelative target {LTS_setup.absolute_to_relative_position(target_position)}", keep_on_top=True)

        if event == "-JOG_NEG-":
            affected_axes = {
                'x1': values['-JOG_X1-'],
                'x2': values['-JOG_X2-'],
                'y1': values['-JOG_Y1-'],
                'y2': values['-JOG_Y2-'],
            }
            distance = values['-JOG_DIS-'] * 10 ** values['-JOG_FAC-']
            target_position = LTS_setup.create_target_position_jogging(affected_axes, distance, -1)

            if LTS_setup.get_absolute_target_position_safety(target_position):
                LTS_setup.move_to_absolute_position_thread(target_position, window)
            else:
                sg.Popup(f"This target position is not safe.\nAbsolute target: {target_position}. \nRelative target {LTS_setup.absolute_to_relative_position(target_position)}", keep_on_top=True)

        if event == '-ABORT-': 
            LTS_setup.abort_movement()


    # Close the window on exit
    window.close()





serial_nums = {
    'x1': '45294984',
    'x2': '45325034',
    'y1': '45316884',
    'y2': '45332564'
    
}


DeviceManagerCLI.BuildDeviceList()

ready_state=0
# make a short window for startup
layout = [
    [[sg.Output(size=(80, 10))]]
]
window_init = sg.Window('Concept', layout, finalize=True,  icon='images/favicon.ico')
print('initializing...')
window_init.refresh()
LTS_settings_dic = device_settings.generate_LTS_settings_dic()
LTS_setup = LTS300System(serial_nums, LTS_settings_dic, window_init)
window_init.close()




# sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
# print = sg.Print         
GUI.home_window(LTS_setup)


if LTS_setup.homed:
    place_holder_main_window(LTS_setup)


LTS_setup.terminate()
print('Einde')