from policy import PolicyModel
from robot import robotModel
from map import Map
from ui import GridApp
from tkinter import *
from configparser import ConfigParser
import pathlib

# Get general configuration data
config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"
config = ConfigParser()
config.read(config_path)
num_robot_actions = config['robot']['number_of_actions']
num_states = config['map']['mapSize']

# Set the whole thing running
root = Tk()
grid = GridApp(root, int(num_states), 600, 600, 5)
root.mainloop()

print("hola")

#robot_object = robotModel()
#policy_object = PolicyModel(num_robot_actions,num_states)