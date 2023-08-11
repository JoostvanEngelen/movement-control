'''
This file contains settings for the Linear stages to be imported to the LTS class
'''

def generate_LTS_settings_dic():
    LTS_settings_dic = {
        'polling_rate': 100,  # ms
        'home_velocity': 5,  # mm/s
        'home_timeout': 60000,  # ms
        'move_velocity': 20,  # mm/s
        'move_timeout': 60000,  # ms
        'safety_margin': 0,  # mm
        'max_connect_attempts': 30, # attempts
        'jog_step_size': 10,  # mm
        'jog_velocity': 10,  # mm/s

    }
    return LTS_settings_dic