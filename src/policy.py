import numpy as np
import utilities
import random
import pathlib

path_to_policies = "data/policies/"
policy_file_name = "policies_stored.txt"

class PolicyModel:

    def __init__(self,num_states, robot):
        self.num_states = num_states # Number of states in the mdp.
        self.state_history = [] # Trajectory over applied policy.
        self.robot = robot # Agent
        self.policy_data = [] # Actual policy (list of actions to arrive to goal given current state)

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
        
    def read_policies(self):
        #TODO
        raise NotImplementedError
        policies = []
        lines = open(path_to_policies + policy_file_name, 'r').readlines()
        for line in lines:
            print(line)
            all_words = last_line.split()
            policy_name = all_words[0]
            

    '''
    Get the actual mathematical rule for a random generated policy data.
    '''
    def get_policy_rule_from_data(self,policy_data):
        #TODO
        raise NotImplementedError

    def get_last_policy_stored(self):
      
        #with open(path_to_policies + policy_file_name, 'r') as f:
        with open(path_to_policies + policy_file_name, 'r') as f:
            try:
                last_line = f.readlines()[-1]
                f.close()
            except:
                f.close()
                return None
        all_words = last_line.split()
        print(all_words)
        temp = all_words[0]
        policy_name = temp[:temp.find(":")]
        policy_number = policy_name[policy_name.find("_")+1:]
        policy_data = all_words[1:]
        return (policy_name,policy_number,policy_data)

    '''
    Add the score (return) to a stored policy that does not have a score.
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
    def write_policy_no_score(self,policy_name, policy_data):
        score = '' 
        self.write_policy(policy_name, policy_data, score)

    '''
    Store the policy in a file
    '''
    def write_policy(self,policy_name, policy_data, score):
        exists = utilities.check_file_exists(path_to_policies,policy_file_name)
        if exists == True:
            if utilities.check_file_is_empty(path_to_policies,policy_file_name):
                f = open(path_to_policies + policy_file_name, "w")
                policy_name = 'policy_1'
                f.write(policy_name + ":" + str(score) +"; "+str(policy_data))
                f.close()
            else:
                f = open(path_to_policies + policy_file_name, "a")
                f.write(policy_name + ":"  + str(score) +"; "+ str(policy_data)+ '\n')
                f.close()
        else:
            policy_name = 'policy_1'
            f = open(path_to_policies + policy_file_name, "w")
            f.close()
            f = open(path_to_policies + policy_file_name, "a")
            f.write(policy_name + ":"  + str(score) +";"+ str(policy_data)+ '\n')
            f.close()
        

    '''
    Compare two policies based on their policy value function.
    '''
    def compare_policies(self, policy1, policy2):
        if (policy1.value_function  >= policy2.value_function):
            return policy1
        else:
            return policy2

    '''
    Choose random policy
    '''
    def choose_random_policy(self):
        #TODO
        raise NotImplementedError

    '''
    Generates a rule to be applied to a policy
    '''
    def generate_random_rule(self, state_vector):
        # state_vector [x: all posible states, y: all posible states ]
        # All rules must provide an answer for all posible states. Use if then 

        # Number of logical propositions
        # state_vector = [robot.pos_xt, pos_zt, robot.localized_believe, robot.vel_x, vel_z, pos_x, pos_z ]

        # Choose with states from the vector to consider for the rule
        number_elements_considered = random.randint(0, len(state_vector))
        considered_states = random.sample(state_vector, number_elements_considered)

        considered_states = state_vector
        actions = self.robot.get_robot_actions()
        chosen_action = random.choice(actions)
    


    ''' 
    π(s)
    '''
    def generate_random_policy(self):
        policy = np.zeros(self.num_states)
        policy_list = []
        actions = self.robot.get_robot_actions()
        for index in range(0,len(policy)):   
            policy_list.append(random.choice(actions))
        # Check if this policy already exists
        # Put right name to new policy
        last_policy = self.get_last_policy_stored() 
        if last_policy == None:
            print('policy_1',policy_list)
            self.write_policy_no_score('policy_1',policy_list)
            return 'policy_1', policy_list
        else:
            print('policy_'+str(int(last_policy[1])+1), policy_list[2:])
            self.write_policy_no_score('policy_'+str(int(last_policy[1])+1),policy_list[2:])
            return 'policy_'+str(int(last_policy[1])+1), policy_list[2:]

    def generate_set_of_policies(self, limit):
        print("Limit: ",limit)
        try:
            for x in range(0,int(limit)):
                self.generate_random_policy()

        except:
            # If the content of limit is empty, do nothing.
            print("error")
            pass

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