
import numpy as np
import utilities
import random

path_to_policies = "/data/policies/"
policy_file_name = "policies_stored.txt"

class PolicyModel:

    def __init__(self,num_actions,num_states,state_history, robot):
        self.num_actions = num_actions
        self.num_states = num_states
        #self.total_reward = 0 # Reward of policy
        self.state_history = state_history
        self.robot = robot

    def read_policies(self):
        #TODO
        raise NotImplementedError
        policies = []
        lines = open(path_to_policies + policy_file_name, 'r').readlines()
        for line in lines:
            print(line)
        

    '''
    Get the actual mathematical rule for a random generated policy data.
    '''
    def get_policy_rule_from_data(self,policy_data):
        #TODO
        raise NotImplementedError

    def get_last_policy_stored(self):

        with open(path_to_policies + policy_file_name, 'r') as f:
            last_line = f.readlines()[-1]
            f.close()
        all_words = last_line.split()
        temp_last_policy_name = all_words[0]
        temp_last_policy_number = all_words[temp_last_policy_name.find("_"):]

        return (temp_last_policy_name,temp_last_policy_number)

    '''
    Add the score to a stored policy that does not have a score.
    '''
    def add_score_of_policy(self,policy_name,score):

        def replace_line(line_num):
            lines = open(path_to_policies + policy_file_name, 'r').readlines()
            data = lines[line_num][lines[line_num].find(";"):]
            new_line = policy_name + ":"  + str(score) +";"+ str(data)
            lines[line_num] = new_line
            out = open(path_to_policies + policy_file_name, 'w')
            out.writelines(lines)
            out.close()

        try:
            file_read = open(path_to_policies + policy_file_name, "r")
            lines = file_read.readlines()
            new_list = []
            index = 0
            for line in lines:
                if policy_name in line:
                    new_list.insert(index, line)
                    index += 1
            file_read.close()
            if index == 0:
                raise Exception(policy_name+" does not exists inside the file.")
            else:
                #update the proper line with score included in specific policy
                replace_line(index)
        except :
            print("\nThe file doesn't exist!")

    '''
    Store the policy in a file
    '''
    def write_policy(self,policy_name, policy_data):
        score = '' 
        self.write_policy(self,policy_name, policy_data, score)

    '''
    Store the policy in a file
    '''
    def write_policy(self,policy_name, policy_data, score):

        exists = utilities.check_file_exists(path_to_policies,policy_file_name)
        if exists == True:
            if utilities.check_file_is_empty():
                policy_name = 'policy_1'
                f.write(policy_name + ":" + str(score) +";"+str(policy_data))
            else:
                f = open(path_to_policies + policy_file_name, "a")
                f.write(policy_name + ":"  + str(score) +";"+ str(policy_data))
                f.close()
        else:
            policy_name = 'policy_1'
            f = open(path_to_policies + policy_file_name, "w")
            f.close()
            f = open(path_to_policies + policy_file_name, "a")
            f.write(policy_name + ":"  + str(score) +";"+ str(policy_data))
            f.close()

    '''
    max(π)
    '''
    def get_best_policy(self):
        #TODO
        raise NotImplementedError
    
    ''' 
    π(s)
    '''
    def generate_random_policy(self):
        policy = np.zeros(self.num_states)
        actions = self.robot.get_robot_actions()
        for index in range(0,len(policy)):
                policy[index] = random.choice(actions)
        # Check if this policy already exists
           
        # Put right name to new policy
        last_policy = self.get_last_policy_stored()   
        return 'policy_'+str(int(last_policy[1])+1), policy

    def generate_set_of_policies(self, limit):
        counter = 0
        while(counter <= limit):
            policy = self.generate_random_policy()
            # Store the new policy in file.
            self.write_policy(policy[0],policy[1])

    ''' 
    P(s'| s, π(s))
    ''' 
    def execute_policy(self, robot, policy):
        total_reward = 0
        start_robot_pos = (robot.pos_x[0],robot.pos_z[0])
        s = utilities.get_state_from_pos(start_robot_pos)
        self.state_history = [s]
        while True:
            s_prime_cell = self.get_transitionted_state(s, policy[s])
            self.state_history.append(s_prime_cell.tkinterCellIndex)
            total_reward += s_prime_cell.reward
            # if s' is the goal (maximum reward), break
            if s_prime_cell.reward == 1:
                break

        return total_reward

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