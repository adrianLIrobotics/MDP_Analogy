from configparser import ConfigParser
import pathlib
from os.path import exists
import os
import pickle


config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"
config = ConfigParser()
config.read(config_path)
num_cols = config['map']['mapSize']

'''
 Get the mdp state (tkinter index cell) from the 2d coordinates position.
'''
def get_state_from_pos(pos):
    print(pos)
    return pos[0] * int(num_cols) + pos[1]

'''
 Get the 2d coordinates position from mdp state (tkinter index cell).
'''
def get_pos_from_state(state):
    return state // num_cols, state % num_cols
    
'''
Add element to dictionary
'''
def add_element_to_dic(dict, key, value):
    if key not in dict:
        dict[key] = []
    dict[key].append(value)

def check_file_exists(path_to_file, file_name):
    return exists(path_to_file + file_name)

def check_file_is_empty(path_to_file, file_name):
    return os.stat(path_to_file + file_name).st_size == 0

'''
Save python object as byte file
'''
def save_object(obj, filename):
    with open(filename, 'wb') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)

'''
Restore pickle file to python object
'''
def restore_objects(filename):
    with open(filename, 'rb') as inp:
        states_pickle = pickle.load(inp)
    return states_pickle

'''
Get the variance according to the light of the cell.
'''
def get_variance_from_light_condition(light_cell_value):
    if light_cell_value >= 50:
        return 0
    if light_cell_value < 50:
        return 0.2

'''
Get the % of localization believe of the robot.
'''
def get_localized_believe(real_pose_x, real_pose_z, estimated_pose_x, estimated_pose_z):
    pass


                        
