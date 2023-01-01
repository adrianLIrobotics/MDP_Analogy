from state import state_model
from rl import reinforment_learning
import random

class Mdp:

    def __init__(self,map_size,robot,grid):

        self.robot = robot # Robot using mdp
        self.num_states = map_size**2
        self.num_actions = self.robot.get_number_actions()
        self.state_history = [state_model(grid, robot)] # Historical state storage. Add initial state.
        self.actions = self.robot.return_robot_actions_id() # Get array of ids of robot actions.
        self.learning = reinforment_learning(self.robot,self.num_states,grid)
        self.total_reward = 0 # Total reward of agent.
        self.current_state = self.state_history[-1] # Current state in the MDP.

    '''
    S' | S, max(π)
    '''
    def apply_best_action(self,current_state):
        # Use q-table to find best action
        action = self.learning.get_optimal_policy(current_state)
        # Apply the best action
        next_state, reward, done = self.learning.get_transitionted_state(current_state, action)
        self.state_history.append(next_state)
        self.total_reward += reward

    '''
    S' | S, random(π)
    '''
    def apply_random_action(self,current_state):
        action = random.choice(self.actions)
        next_state, reward, done = self.learning.get_transitionted_state(current_state, action)
        self.state_history.append(next_state)
        self.total_reward += reward

    '''
    max(π) | s
    '''
    def train_model(self):
        # Solve the MDP by finding optimal policy using q-learning
        self.learning.q_learning()

    
    def get_best_policy_model(self):
        return self.learning.q_table
 

    

    
