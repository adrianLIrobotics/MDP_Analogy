import numpy as np
import matplotlib.pyplot as plt

'''
- Acción 0 significa moverse a la izquierda.
- Acción 1 significa moverse a la derecha.
'''

# Definir parámetros
num_states = 6
num_actions = 2
learning_rate = 0.8
discount_factor = 0.9
exploration_prob = 0.2
num_episodes = 1000

# Inicializar la matriz Q con ceros
Q = np.zeros((num_states, num_actions))

# Definir la función de selección de acción
def select_action(state):
    if np.random.rand() < exploration_prob:
        return np.random.choice(num_actions)
    else:
        return np.argmax(Q[state, :])
    
# Inicializar listas para almacenar datos del gráfico
episode_list = []
total_reward_list = []

# Simular episodios
for episode in range(num_episodes):
    current_state = 0
    total_reward = 0  # Inicializar el reward total por episodio

    while current_state != 5:
        action = select_action(current_state)

        # Simular la transición al nuevo estado
        next_state = current_state + (1 if action == 1 else -1)

        # Asegurarse de que el próximo estado esté dentro de los límites
        next_state = max(0, min(next_state, num_states - 1))

        # reward = 0 if next_state != 5 else 1  # Recompensa 1 si alcanza el objetivo, 0 de lo contrario
        reward = 1 if next_state == 5 else -0.1

        total_reward += reward  # Acumular el reward total por episodio

        # Actualizar el valor Q para la acción tomada
        Q[current_state, action] = (1 - learning_rate) * Q[current_state, action] + \
                                   learning_rate * (reward + discount_factor * np.max(Q[next_state, :]))

        current_state = next_state

    # Guardar datos del gráfico
    episode_list.append(episode + 1)
    total_reward_list.append(total_reward)

    # Imprimir el reward total por episodio
    print(f"Episodio {episode + 1}, Reward Total: {total_reward}")

# Generar el gráfico
plt.plot(episode_list, total_reward_list, label='Total Reward')
plt.xlabel('Episodio')
plt.ylabel('Total Reward')
plt.title('Recompensa Total por Episodio')
plt.legend()
plt.show()

# Imprimir la matriz Q
print("\nMatriz Q:")
print(Q)

# Encontrar el mejor camino desde el estado inicial al estado objetivo

current_state = 0
path = [current_state]

while current_state != 5:
    action = np.argmax(Q[current_state, :])
    next_state = current_state + (1 if action == 1 else -1)
    next_state = max(0, min(next_state, num_states - 1))
    path.append(next_state)
    current_state = next_state

print("Mejor camino:", path)

'''
RL: 

Q_TABLE 1 RL:

[[0 0 ]
 [0 0 ]
 [0 0 ]
 [0 0 ]
 [0 0]
 [0 0]]

Q_TABLE 2
 
 [[0 1 ]
 [0 1 ]
 [0 1 ]
 [0 1 ]
 [0 1]
 [0 1]]

 Q_TABLE 3

 [[1 0 ]
 [1 0 ]
 [1 0 ]
 [1 0 ]
 [1 0]
 [1 0]]

Q_TABLE LEARNED BY RL

[[0.18098 0.3122 ]
 [0.18098 0.458  ]
 [0.3122  0.62   ]
 [0.458   0.8    ]
 [0.62    1.     ]
 [0.      0.     ]]

 Learning rate: 0.999

 2 episode.


'''
