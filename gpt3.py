
import numpy as np
import matplotlib.pyplot as plt

# Definir parámetros
num_states = 6
num_actions = 2
learning_rate = 0.9
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
last_episode_with_q_change = 0  # Variable para almacenar el último episodio con cambio en los valores Q
last_q_change_episode = 0  # Variable para almacenar el episodio del último Q que deja de cambiar

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

    # Almacenar datos del gráfico
    episode_list.append(episode + 1)
    total_reward_list.append(total_reward)

    # Verificar si ha ocurrido un cambio en los valores Q
    q_changed = not np.array_equal(Q, q_value_changes[0][-1])
    for state in range(1, num_states):
        q_changed = q_changed or not np.array_equal(Q[state, :], q_value_changes[state][-1])

    if q_changed and episode - last_episode_with_q_change > last_episode_with_q_change - last_q_change_episode:
        last_episode_with_q_change = episode
        last_q_change_episode = episode

    # Imprimir el reward total por episodio
    print(f"Episodio {episode + 1}, Reward Total: {total_reward}")

# Encontrar el último Q que deja de cambiar más lejos en los episodios
# Definir un umbral de cambio
change_threshold = 0.0000001 # 0.00000000091  # Puedes ajustar este valor según tus necesidades -  0.0000000005

# Encontrar el último Q que deja de cambiar más lejos en los episodios con el umbral
last_q_change_episode = last_episode_with_q_change
max_distance = 0

for state in range(num_states):
    q_changes = np.abs(np.diff(np.array(q_value_changes[state]), axis=0))
    non_zero_changes = np.any(q_changes > change_threshold, axis=1)
    
    if np.any(non_zero_changes):
        last_change_episode = np.max(np.where(non_zero_changes)[0]) + 1
        distance = last_episode_with_q_change - last_change_episode
        max_distance = max(max_distance, distance)

last_q_change_episode = last_episode_with_q_change - max_distance



# Generar el gráfico de cambio de valores Q para cada estado
plt.figure(figsize=(12, 8))
for state in range(num_states):
    q_value_changes[state] = np.array(q_value_changes[state])
    min_len = min(len(episode_list), len(q_value_changes[state]))
    plt.plot(episode_list[:min_len], q_value_changes[state][:min_len, 0], label=f'Q_value_{state}_Action_0')
    plt.plot(episode_list[:min_len], q_value_changes[state][:min_len, 1], label=f'Q_value_{state}_Action_1')

# Añadir línea vertical negra en el episodio más lejano con cambio en algún valor Q
plt.axvline(x=last_q_change_episode, color='black', linestyle='--', label='Last Q Change')

plt.xlabel('Episode')
plt.ylabel('Q value')
plt.title('Change of the Q values for each state along each episode.')
plt.legend(loc='lower right')
plt.show()

# Generar el gráfico
# Calcular la media de las recompensas totales
average_rewards = np.convolve(total_reward_list, np.ones(10)/10, mode='valid')

# Generar el gráfico con la curva de recompensas totales y la media
# Calcular la media de las recompensas totales
average_rewards_per_episode = np.convolve(total_reward_list, np.ones(10)/10, mode='valid')

# Calcular la media total
average_total_reward = np.mean(total_reward_list)

# Generar el gráfico con la curva de recompensas totales, la media por episodio y la media total
plt.figure(figsize=(12, 8))
plt.plot(episode_list, total_reward_list, label='Total Reward')
plt.plot(episode_list[:-9], average_rewards_per_episode, label='Average Reward per Episode (Window Size=10)', linestyle='--', color='red')
plt.axhline(y=average_total_reward, color='green', linestyle='-.', label=f'Average Total Reward: {average_total_reward:.2f}')
plt.xlabel('Episode')
plt.ylabel('Reward')
plt.title('Total reward per episode with Average Reward')
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

print("Mejor camino:", path[1:])
print("last_q_change_episode: "+str(last_q_change_episode))
