import numpy as np
from policy import PolicyModel
from robot import robotModel
import random
import utilities
from state import state_model
from colour import Object_Colour
from configparser import ConfigParser
import pathlib
import time
from datetime import datetime
from tkinter import filedialog

# https://stackoverflow.com/questions/4901815/object-of-custom-type-as-dictionary-key

now = datetime.now()
current_time = now.strftime("%Y_%m_%d_%H_%M_%S")

path_to_policies = "data/policies/"
policy_file_name = "action_q_values_"+str(current_time)+".txt"
q_value_file = "q_value_file_"+str(current_time)+".txt"


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
    Get q values for state
    '''
    def get_qvalues(self, state):
        return self.q(state)

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
    Easy handle of the q_table dictionary
    '''
    def q(self,state, action=None):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.actions)) # The key of the dict is state.
            
        if action is None:
            return self.q_table[state] # If an action is not specified as input param, return all possible actions for a given state.
    
        return self.q_table[state][action] # returns the q-value of the corresponding index of the given action.

    def open_file_read(self, name_param, path_param = None):
        if (path_param == None):
            f = open(name_param, "r")
            return f
        else:
            f = open(path_param + name_param, "r")
            return f

    def open_file_write(self, path_param, name_param):
        f = open(path_param + name_param, "w")
        return f

    '''Save learning summery'''
    def write_learning_routes(self,val, f):
        f.write(str(val)+'\n')

    def write_q_value(self, val, f):
        f.write(str(val))
        
    def close_file(self,f):
        f.close() 

    '''
    Save in local file the q table for specific map
    '''
    def save_q_table(self):

        def save_q_values():
            for key, value in self.q_table.items():
                #fob.write(str(key.grid)+";"+str(key.robotPose)+":"+str(value)+"\n")
                fob.write(str(key.grid)+";"+str(key.robotPose)+":"+str(value.tolist()).replace("]","").replace("[","")+"\n")

        file = filedialog.asksaveasfilename(
        filetypes=[("txt file", ".txt")],
        defaultextension=".txt")
        fob=open(file,'w')
        save_q_values()
        fob.close()

    '''
    Read from local file the q table.
    '''
    def read_q_table(self):
        qtable_file = filedialog.askopenfilename(filetypes=(
                ('Grid files', '.grid'),
                ('Text files', '.txt'),
                ('All files', '*.*'))) # Get name of q_file
        self.q_table.clear() # Clear the previous loaded q_table for reset.

        def parser_q_map(string_map):
            indexes = utilities.find(string_map, ']')
            previous_index = 0
            temp_map = [] # Temporal map
            for index_pos in indexes:
                row = string_map[previous_index:index_pos] # Get row
                previous_index = index_pos
                cleaned_row = row.replace("[","").replace("]","").replace("'","")
                row_tokens = cleaned_row.split(", ")
                new_list = list(filter(lambda x: x != '', row_tokens))
                if indexes[-1] != index_pos:
                    temp_map.append(new_list)
            return temp_map

        def parser_robot_pose_q(string_robot_pose):
            x_pose_parsed = int(string_robot_pose[string_robot_pose.index("[")+1:string_robot_pose.index(",")])
            z_pose_parsed = int(string_robot_pose[string_robot_pose.index(",")+2:string_robot_pose.index("]")])
            tempRobot = robotModel(False,0) # Create a temporal robot
            tempRobot.pos_xt = x_pose_parsed
            tempRobot.pos_zt = z_pose_parsed
            tempRobot.pos_xt_kalman = x_pose_parsed
            tempRobot.pos_zt_kalman = z_pose_parsed
            return tempRobot
        
        def parser_actions_q(string_actions):
            temp = np.array(string_actions.replace("\n","").split(",")).astype(float)
            print(temp)
            return temp
        
        # Complete the action_state_dict
        def get_action_state_dict():
            f = self.open_file_read(qtable_file)
            lines = f.readlines()
            for line in lines:
                state_q = state_model(parser_q_map(line[0:line.find(";")]), parser_robot_pose_q(line[line.find(";"):line.find(":")]))
                actions_q = parser_actions_q(line[line.find(":")+1:])
                self.q_table[state_q] = actions_q
            f.close()
        # Read the file and load the action_state to self.q_table.
        get_action_state_dict()

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
        print("=============================")
        print("Number of ep: "+str(self.number_episodes))
        print("Number of steps in episode: "+str(self.max_episode_steps))
        print("=============================")
        f = self.open_file_write(path_to_policies,policy_file_name) # Start saving the route info 
        h = self.open_file_write(path_to_policies, q_value_file)

        for e in range(self.number_episodes):
            state = self.start_state
            total_reward = 0
            alpha = self.alphas[e]
            
            for i in range(0, self.max_episode_steps): #
                action = self.epsilon_greedy_algorithm(state)
                #self.write_learning_routes(utilities.translate_action_id_to_name(action), f)
                next_state, reward, done = self.get_transitionted_state(state, action)
                total_reward += reward
                # Update the q value associated with the given state and action.
                self.update_q_value(state,next_state,reward,alpha,action)
                state = next_state
                if done:
                    print("Robot is in goal cell")
                    self.reset_simulation()
                    #self.robot.goal_reached = False
                    break
            
            self.reset_simulation() # Reset simulation for new cycle. MAYBE THIS IS NOT NEEDED.
            #self.reset_simulation() # Take care with this one.
            print(f"Episode {e + 1}: total reward -> {total_reward}")
            self.write_learning_routes(f"Episode {e + 1}: total reward -> {total_reward}", f)
        print("Finished training...")
        self.write_learning_routes("Finished training...", f)
        self.close_file(f)
        self.write_q_value(self.q_table,h) # Save Q_table to file.
        self.close_file(h)
        # Reset self.goal_reached for running eval.
        self.robot.goal_reached = False

    ''' 
    P(s' | s, a)
    '''
    def get_transitionted_state(self,current_state,action):
        # Run action in robot
        if self.actions[0] == action:
            self.robot.moveUp(1) 
          #  time.sleep(3)
        if self.actions[1] == action:
            self.robot.moveUp(2)
           # time.sleep(3)
        if self.actions[2] == action:
            self.robot.moveDown(1)
           # time.sleep(3)
        if self.actions[3] == action:
            self.robot.moveDown(2)
            #time.sleep(3)
        if self.actions[4] == action:
            self.robot.moveLeft(1)
            #time.sleep(3)
        if self.actions[5] == action:
            self.robot.moveLeft(1)
           # time.sleep(3)
        if self.actions[6] == action:
            self.robot.moveRight(1)
           #time.sleep(3)
        if self.actions[7] == action:
            self.robot.moveRight(2)
            #time.sleep(3)
        #if self.actions[8] == action:
            #time.sleep(3)
           # pass
        
        # return s' 
        #s_prime = utilities.get_state_from_pos(self.robot.pos_x[0],self.robot.pos_z[0])
        '''Use kalman filter estimation to get new pose'''
        #s_prime = utilities.get_state_from_pos((self.robot.pos_xt_kalman,self.robot.pos_zt_kalman))
        #s_prime = utilities.get_state_from_pos((self.robot.pos_xt,self.robot.pos_zt))
        
        '''
        # if robot collides with wall, reward is -0.1
        if (current_state == s_prime) and (self.robot.collided == True):
            self.robot.gridMap.map[s_prime].reward = -0.1
        ''' 
        # Check if robot has arrived to destination
        if (self.robot.goal_reached == True):
            is_done = True
        else:
            is_done = False
        '''
        try:
            if (self.grid.map[s_prime].colour == Object_Colour.Goal.value):
                is_done = True
            else:
                is_done = False
        except:
            is_done = False
        '''

        #return state_model(grid=self.grid, robotPose=[self.robot.pos_xt, self.robot.pos_zt]), self.grid.map[s_prime].reward, is_done
        return state_model(self.grid.get_stateMap(), self.robot), self.robot.current_reward , is_done
        

    '''
    max(π) | s
    '''
    def get_optimal_policy(self, current_state):          
        return np.argmax(self.q(current_state))

    
