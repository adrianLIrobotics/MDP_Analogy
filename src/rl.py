import numpy as np
from policy import PolicyModel
from robot import robotModel
import random
import utilities

# Based upon Q-Learning to get optimal policy.
class reinforment_learning():

    def __init__(self,robot,num_states):
        self.epsilon = 0.1 # ε-greedy value
        self.robot = robot
        self.num_states = num_states # Number of states in the mdp.
        self.number_episodes = 20 # An episode is the path of agent until it reaches destination.
        self.max_episode_steps = 100 # Maximum number of actions before arriving to goal.
        self.min_alpha = 0.02 # Learning rate
        self.discount_factor = 0.5 # γ Gamma discount factor for future accountability.
        self.alphas = np.linspace(1.0, self.min_alpha, self.number_episodes) # Decay the learning rate, alpha, every episode 
        self.q_table = dict() # Q-Values table
        self.actions = self.robot.return_robot_actions_id() # Get array of ids of robot actions.

    ''' 
    P(s'| s, a)
    ''' 
    def execute_action(self, robot, a): 
        start_robot_pos = (robot.pos_x[0],robot.pos_z[0])
        s = utilities.get_state_from_pos(start_robot_pos)
        s_prime_cell = self.get_transitionted_state(s, a)
        self.update_q_value(s,s_prime_cell,s_prime_cell.reward)

    '''
    Update Q Value
    '''
    def update_q_value(self,state,next_state,reward,alpha):
        #Q(s,a) = Q(s,a) + α(R + γ * max Q(s',a) - Q(s,a))
        self.q(state)[self.action] = self.q(state, self.action) + \
                alpha * (reward + self.discount_factor *  np.max(self.q(next_state)) - self.q(state, self.action))

    '''
    Choose action based on epsilon greedy algorithm
    '''
    def epsilon_greedy_algorithm(self,s):
        def exploit(s):
            return np.argmax(self.q(s)) # Choose action with highest Q value for state s.
        def explore():
            # Choose to explore other options.
            return random.choice(self.actions)

        if random.random > self.epsilon:
            return exploit(s)
        else:
            return explore()

    '''
    Save in local file the q table for specific map
    '''
    def save_q_table(self):
        raise NotImplementedError

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
            self.q_table[state] = np.zeros(len(self.actions))
            
        if action is None:
            return self.q_table[state] # If an action is not specified as input param, return all possible actions for a given state.
    
        return self.q_table[state][action] # returns the q-value of the corresponding index of the given action.

    '''
    Generate from q learning max(π) and q table
    '''
    def q_learning(self):
        #TODO 
        optimal_policy =  PolicyModel()
        return optimal_policy

    ''' 
    P(s' | s, a)
    '''
    def get_transitionted_state(self,current_state,action):
        # Run action in robot
        if "moveUpOne" in action:
            self.robot.moveUpOne() 
        if "moveUpTwo" in action:
            self.robot.moveUpTwo()
        if "moveDownOne" in action:
            self.robot.moveDownOne()
        if "moveDownTwo" in action:
            self.robot.moveDownTwo()
        if "moveLeftOne" in action:
            self.robot.moveLeftOne()
        if "moveLeftTwo" in action:
            self.robot.moveLeftTwo()
        if "moveRightOne" in action:
            self.robot.moveRightOne()
        if "moveRightTWo" in action:
            self.robot.moveRightTWo()
        if "stay" in action:
            pass
        
        # return s' 
        s_prime = utilities.get_state_from_pos(self.robot.pos_x[0],self.robot.pos_z[0])
        
        # if robot collides with wall, reward is -0.1
        if (current_state == s_prime) and (self.robot.collided == True):
            self.robot.gridMap.map[s_prime].reward = -0.1
            
        # return cell class object in map from new s'
        return self.robot.gridMap.map[s_prime]