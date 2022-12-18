
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from time import time
from policy import PolicyModel
import utilities

class Mdp:

    def __init__(self,map_size,map,robot):

        self.robot = robot # Robot using mdp
        self.num_rows = map_size
        self.num_cols = map_size
        self.num_states = map_size**2
        self.num_actions = 9 # up/x2, down/x2, left/x2 , right/x2, stay 
        self.map_reward_table = self.get_map_reward_diccionary(map) # Reward base on cell
        self.reward = self.get_reward_value()
        self.transition_model = self.get_transition_model()
        self.total_reward = 0 # cumulative reward
        self.state_history = [] # Historical state storage
        
        policy = PolicyModel(self.num_actions,self.num_states,self.state_history,robot)
 

    ''''
    Populate the reward dictionary based on the generated map ONLY.
    '''
    def get_map_reward_diccionary(map):
        reward_state_dictionary = {} # Dictionary key (state)- value (reward)
        for cell in map.map:
            utilities.add_element_to_dic(reward_state_dictionary,cell.tkinterCellIndex,cell.reward) 
        return reward_state_dictionary

    

    
