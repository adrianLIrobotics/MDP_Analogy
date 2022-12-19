from configparser import ConfigParser
import pathlib
from os.path import exists
import os

config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"
config = ConfigParser()
config.read(config_path)
num_cols = config['map']['mapSize']

'''
 Get the mdp state (tkinter index cell) from the 2d coordinates position.
'''
def get_state_from_pos(pos):
     return pos[0] * num_cols + pos[1]

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
    return os.stat(path_to_file, file_name).st_size == 0

