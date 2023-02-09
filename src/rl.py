import numpy as np
from policy import PolicyModel
from robot import robotModel
import random
import utilities
from state import state_model
from colour import Object_Colour
from configparser import ConfigParser
import pathlib

path_to_policies = "data/policies/"
policy_file_name = "action_q_values.txt"


# Get general configuration data
config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"
config = ConfigParser()
config.read(config_path)
n_episodes = config['q_learning']['number_of_episodes']
max_steps_ep = config['q_learning']['max_episode_steps']


# Based upon Q-Learning to get optimal policy.
class reinforment_learning():

    def __init__(self,robot,num_states,gridMap):
        self.epsilon = 0.1 # ε-greedy value
        self.robot = robot
        self.num_states = num_states # Number of states in the mdp.
        self.number_episodes = int(n_episodes) # An episode is the path of agent until it reaches destination.
        self.max_episode_steps = int(max_steps_ep) # Maximum number of actions before arriving to goal.
        self.min_alpha = 0.02 # Learning rate
        self.discount_factor = 0.5 # γ Gamma discount factor for future accountability.
        self.alphas = np.linspace(1.0, self.min_alpha, self.number_episodes) # Decay the learning rate, alpha, every episode 
        self.q_table = dict() # Q-Values table
        self.actions = self.robot.return_robot_actions_id() # Get array of ids of robot actions.
        self.grid = gridMap
        self.start_state = state_model(self.grid.map, self.robot) # Start state.
        self.total_reward = 0 

    '''
    Update Q Value
    '''
    def update_q_value(self,state,next_state,reward,alpha, action):
        #Q(s,a) = Q(s,a) + α(R + γ * max Q(s',a) - Q(s,a))
        self.q(state)[action] = self.q(state, action) + \
                alpha * (reward + self.discount_factor *  np.max(self.q(next_state)) - self.q(state, action))

    '''
    Choose action based on epsilon greedy algorithm
    '''
    def epsilon_greedy_algorithm(self,s):
        def exploit(s):
            return np.argmax(self.q(s)) # Choose action with highest Q value for state s.
        def explore():
            # Choose to explore other options.
            return random.choice(self.actions)

        if random.uniform(0, 1) > self.epsilon:
            return exploit(s)
        else:
            return explore()

    '''
    Save in local file the q table for specific map
    '''
    def save_q_table(self):

        def save_q_values_per_action():
            for key in self.q_table:
                f = open(path_to_policies + policy_file_name, "w")
                f.write(self.q_table[key]+'\n')
                f.close()
        
        def save_states():
            states_list = []
            for key in self.q_table:
                states_list.append(key)
            utilities.save_object(states_list,'states.pkl')

        save_q_values_per_action()
        save_states()


    '''
    Read from local file the q table from specific map.
    '''
    def read_q_table(self):
        raise NotImplementedError

    '''
    Easy handle of the q_table dictionary
    '''
    def q(self,state, action=None):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.actions)) # The key of the dict is state.
            
        if action is None:
            return self.q_table[state] # If an action is not specified as input param, return all possible actions for a given state.
    
        return self.q_table[state][action] # returns the q-value of the corresponding index of the given action.

    '''
    Reset the system for new episode of training.
    '''
    def reset_simulation(self):
        # Teleport the robot to initial position.
        self.robot.reset_simulation()

    '''
    Generate from q learning max(π) and q table
    '''
    def q_learning(self):
        for e in range(self.number_episodes):
    
            state = self.start_state
            total_reward = 0
            alpha = self.alphas[e]

            for _ in range(self.max_episode_steps):
                action = self.epsilon_greedy_algorithm(state)
                print("Action chosen: "+str(action))
                next_state, reward, done = self.get_transitionted_state(state, action)
                total_reward += reward
                # Update the q value associated with the given state and action.
                self.update_q_value(state,next_state,reward,alpha,action)
                state = next_state
                if done:
                    # save q-table.
                    #self.save_q_table()
                    break
            self.reset_simulation() # Reset simulation for new cycle.
            # Reset map and robot position --> TODO
            print(f"Episode {e + 1}: total reward -> {total_reward}")
        print("Finished training...")


    ''' 
    P(s' | s, a)
    '''
    def get_transitionted_state(self,current_state,action):
        # Run action in robot
        if self.actions[0] == action:
            self.robot.moveUp(1) 
        if self.actions[1] == action:
            self.robot.moveUp(2)
        if self.actions[2] == action:
            self.robot.moveDown(1)
        if self.actions[3] == action:
            self.robot.moveDown(2)
        if self.actions[4] == action:
            self.robot.moveLeft(1)
        if self.actions[5] == action:
            self.robot.moveLeft(1)
        if self.actions[6] == action:
            self.robot.moveRight(1)
        if self.actions[7] == action:
            self.robot.moveRight(2)
        if self.actions[8] == action:
            pass
        
        # return s' 
        #s_prime = utilities.get_state_from_pos(self.robot.pos_x[0],self.robot.pos_z[0])
        '''Use kalman filter estimation to get new pose'''
        s_prime = utilities.get_state_from_pos((self.robot.pos_xt_kalman,self.robot.pos_zt_kalman))
        
        '''
        # if robot collides with wall, reward is -0.1
        if (current_state == s_prime) and (self.robot.collided == True):
            self.robot.gridMap.map[s_prime].reward = -0.1
        ''' 
        # Check if robot has arrived to destination
        if (self.grid.map[s_prime].colour == Object_Colour.Goal.value):
            is_done = True
        else:
            is_done = False

        #return state_model(grid=self.grid, robotPose=[self.robot.pos_xt, self.robot.pos_zt]), self.grid.map[s_prime].reward, is_done
        return state_model(self.grid, self.robot), self.robot.cumulative_reward, is_done
        

    '''
    max(π) | s
    '''
    def get_optimal_policy(self, current_state):          
        return np.argmax(self.q(current_state))

    
