# Example of q learning from: https://medium.com/@curiousily/solving-an-mdp-with-q-learning-from-scratch-deep-reinforcement-learning-for-hackers-part-1-45d1d360c120
# https://arshren.medium.com/an-introduction-to-markov-decision-process-8cc36c454d46

from copy import deepcopy
import numpy as np
import random
import pickle


ZOMBIE = "z"
CAR = "c"
ICE_CREAM = "i"
EMPTY = "*"

grid = [
    [ICE_CREAM, EMPTY],
    [ZOMBIE, CAR]
]

for row in grid:
    print(' '.join(row))

class State:
    
    def __init__(self, grid, car_pos):
        self.grid = grid
        self.car_pos = car_pos
        
    def __eq__(self, other):
        return isinstance(other, State) and self.grid == other.grid and self.car_pos == other.car_pos
    
    def __hash__(self):
        return hash(str(self.grid) + str(self.car_pos))
    
    def __str__(self):
        return f"State(grid={self.grid}, car_pos={self.car_pos})"

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3

ACTIONS = [UP, DOWN, LEFT, RIGHT]

start_state = State(grid=grid, car_pos=[1, 1])

def act(state, action):
    
    def new_car_pos(state, action):
        p = deepcopy(state.car_pos)
        if action == UP:
            p[0] = max(0, p[0] - 1) # X axes
        elif action == DOWN:
            p[0] = min(len(state.grid) - 1, p[0] + 1) # X axes
        elif action == LEFT:
            p[1] = max(0, p[1] - 1) # Y axes
        elif action == RIGHT:
            p[1] = min(len(state.grid[0]) - 1, p[1] + 1)  # Y axes
        else:
            raise ValueError(f"Unknown action {action}")
        return p
            
    p = new_car_pos(state, action) # New position of car
    grid_item = state.grid[p[0]][p[1]]
    
    new_grid = deepcopy(state.grid)
    
    if grid_item == ZOMBIE:
        reward = -100
        is_done = True
        new_grid[p[0]][p[1]] += CAR
    elif grid_item == ICE_CREAM:
        reward = 1000
        is_done = True
        new_grid[p[0]][p[1]] += CAR
    elif grid_item == EMPTY:
        reward = -1
        is_done = False
        old = state.car_pos # Antigua posicion del coche.
        new_grid[old[0]][old[1]] = EMPTY # In the place were there was a car, now is empty cause it moved.
        new_grid[p[0]][p[1]] = CAR # The new position of car now has a car.
    elif grid_item == CAR:
        reward = -1
        is_done = False
    else:
        raise ValueError(f"Unknown grid item {grid_item}")
    
    return State(grid=new_grid, car_pos=p), reward, is_done

random.seed(42) # for reproducibility

N_STATES = 4
N_EPISODES = 200

MAX_EPISODE_STEPS = 100

MIN_ALPHA = 0.02

alphas = np.linspace(1.0, MIN_ALPHA, N_EPISODES)
gamma = 1.0
eps = 0.2

q_table = dict()

def q(state, action=None):
    # q_table[state] = value --> asigna como key 'state' y valor para esa key 'value'
    if state not in q_table:
        q_table[state] = np.zeros(len(ACTIONS))
        
    if action is None:
        return q_table[state] # Si no especifico la accion, devuelvo todas las acciones posibles del estado.
    
    
    return q_table[state][action] # returns the q-value of the corresponding index of the given action.

def choose_action(state):
    if random.uniform(0, 1) < eps:
        return random.choice(ACTIONS) 
    else:
        val = q(state)
        return np.argmax(val) # Choose best possible action.

def save_object(obj, filename):
    with open(filename, 'wb') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)

def save_q_table(q_table_param):
    states_list = []
    for key in q_table_param:

        states_list.append(q_table_param[key])
    #save_object(states_list, 'states.pkl')

def restore_objects():
    with open('states.pkl', 'rb') as inp:
        states_pickle = pickle.load(inp)
    return states_pickle

for e in range(N_EPISODES):
    
    state = start_state
    total_reward = 0
    alpha = alphas[e]
    
    for _ in range(MAX_EPISODE_STEPS):
        action = choose_action(state)
        next_state, reward, done = act(state, action)
        total_reward += reward
        # Update the q value associated with the given state and action.
        q(state)[action] = q(state, action) + \
                alpha * (reward + gamma *  np.max(q(next_state)) - q(state, action))
        #print("update data:  ",q(state))
        state = next_state
        if done:
            # save q-table.
            save_q_table(q_table)
            break
    #print(f"Episode {e + 1}: total reward -> {total_reward}")
    print(q_table)