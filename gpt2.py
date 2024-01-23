import numpy as np
import matplotlib.pyplot as plt

# Definir parámetros
num_states = 6
num_actions = 2
learning_rate = 0.9999
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
q_value_changes = {state: [] for state in range(num_states)}

# Simular episodios
for episode in range(num_episodes):
    current_state = 0
    total_reward = 0  # Inicializar el reward total por episodio

    while current_state != 5:
        action = select_action(current_state)

        # Simular la transición al nuevo estado
        next_state = current_state + (1 if action == 1 else -1)
        next_state = max(0, min(next_state, num_states - 1))

        # Calcular la recompensa
        reward = 1 if next_state == 5 else -0.1
        total_reward += reward  # Acumular el reward total por episodio

        # Realizar un seguimiento de los cambios en los valores Q para cada estado
        for state in range(num_states):
            q_value_changes[state].append(Q[state, :].copy())

        # Actualizar el valor Q para la acción tomada
        Q[current_state, action] = (1 - learning_rate) * Q[current_state, action] + \
                                   learning_rate * (reward + discount_factor * np.max(Q[next_state, :]))

        current_state = next_state

    # Guardar datos del gráfico
    episode_list.append(episode + 1)
    total_reward_list.append(total_reward)

    # Imprimir el reward total por episodio
    print(f"Episodio {episode + 1}, Reward Total: {total_reward}")

# Generar el gráfico de cambio de valores Q para cada estado
plt.figure(figsize=(12, 8))
for state in range(num_states):
    q_value_changes[state] = np.array(q_value_changes[state])
    min_len = min(len(episode_list), len(q_value_changes[state]))
    plt.plot(episode_list[:min_len], q_value_changes[state][:min_len, 0], label=f'Q_value_{state}_Action_0')
    plt.plot(episode_list[:min_len], q_value_changes[state][:min_len, 1], label=f'Q_value_{state}_Action_1')

plt.xlabel('Episodio')
plt.ylabel('Valor Q')
plt.title('Cambio en los valores Q para cada Estado a lo largo de los Episodios')
plt.legend(loc='lower right')
plt.show()

# Encontrar el mejor camino desde el estado inicial al estado objetivo

current_state = 3
path = [current_state]

while current_state != 5:
    action = np.argmax(Q[current_state, :])
    next_state = current_state + (1 if action == 1 else -1)
    next_state = max(0, min(next_state, num_states - 1))
    path.append(next_state)
    current_state = next_state

print("Mejor camino:", path[1:])
