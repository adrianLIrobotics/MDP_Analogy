from state import state_model
from rl import reinforment_learning
import random
import utilities

class Mdp:

    def __init__(self,map_size,robot,grid): # grid == gridMap

        self.robot = robot # Robot using mdp
        self.num_states = map_size**2
        self.num_actions = self.robot.get_number_actions()
        self.state_history = [state_model(grid.map, robot)] # Historical state storage. Add initial state.
        self.actions = self.robot.return_robot_actions_id() # Get array of ids of robot actions.
        self.learning = reinforment_learning(self.robot,self.num_states,grid)
        self.total_reward = 0 # Total reward of agent.
        self.current_state = self.state_history[-1] # Current state in the MDP.

    '''
    S' | S, max(π)
    '''
    def apply_best_action(self,current_state = None):
        # Use q-table to find best action
        action = self.learning.get_optimal_policy(self.current_state)
        action_out = utilities.translate_action_id_to_name(action)
        print("Best action: "+str(action_out))
        # Apply the best action
        next_state, reward, done = self.learning.get_transitionted_state(current_state, action)
        self.state_history.append(next_state)
        self.total_reward += reward

    '''
    Run trained model max(π) until goal is reached. 
    '''
    def run_best_policy(self):
        print("Running best policy")
        print(self.robot.goal_reached)
        while (self.robot.goal_reached != True):
            self.apply_best_action()
        # Reset self.robot.goal_reached
        self.robot.goal_reached = False

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
 

    

    
