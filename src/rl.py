import numpy as np
from policy import PolicyModel
from robot import robotModel
import random
import utilities

# Based upon Q Learning to get optimal policy.
class reinforment_learning():

    def __init__(self,robot,num_states):
        self.epsilon = 0.1 # ε-greedy value
        self.robot = robot
        self.num_states = num_states # Number of states in the mdp.
        self.number_episodes = 0 # An episode is the path of agent until it reaches destination.
        self.max_episode_steps = 100 # Maximum number of actions before arriving to goal.
        self.min_alpha = 0.02 # Learning rate
        self.discount_factor = 0.1 # γ Gamma discount factor for future accountability.

        # Q Values table - init at zeros dim(map)
        self.q_values = np.empty((0, robot.get_number_actions()), int)
        for states in range(0, self.num_states):
            self.q_values = np.vstack([self.q_values, np.zeros(robot.get_number_actions())])

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
    def update_q_value(self,s,s_prime,r):
        #Q(s,a) = Q(s,a) + α(R + γ * max Q(s',a) - Q(s,a))
        raise NotImplementedError

    '''
    Choose action based on epsilon greedy algorithm
    '''
    def epsilon_greedy_algorithm(self,s):
    #TODO: needs to be improved to slowed decae ganma over time.
        def exploit(s):
            # Choose action with highest Q value for state s.
            values = self.q_values[int(s),:]
            return self.robot.get_robot_actions()[values.index(max(values))]
        def explore():
            # Choose to explore other options.
            return random.choice(self.robot.get_robot_actions())

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