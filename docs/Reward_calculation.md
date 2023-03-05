## How reward is calculated for each action:
___
Process of calculating the reward for each possible action of the robot. Summery:

When the robot moves in either direction, the following calculations are made:

1) Did the robot collided? 

    1.1) True AND moving 1 step at a time.
    ```
    self.current_reward = -0.1
    ```
    1.2) True AND moving 2 steps at a time
    ```
    self.current_reward = -0.2
    ```
    1.3) False AND moving 1 step at a time.
    ```
    self.current_reward = self.gridMap.map[newPosition].reward
    ```
    Here the program checks the lighting conditions of the cell, if over or equal to 50% return: -0.04. Else return -0.1. 
    If the cell contains the goal, return 1000.

    1.4) False AND moving 2 steps at a time.
    ```
    self.current_reward = self.gridMap.map[newPosition].reward
    ```
    Here the program also checks the lighting conditions of the cell, if over or equal to 50% return: -0.04. Else return -0.1. 
    If the cell contains the goal, return 1000.

2) How well the robot is localized?

    2.1) If number_objects_detected == 0:
    ```
    self.current_reward += -0.1
    ```
    2.2) If number_objects_detected == 1:
    ```
    self.current_reward += -0.05
    ```
    2.3) If number_objects_detected >= 2:
    ```
    self.current_reward += -0.01
    ```

3) How fast the robot is moving with rewards to its current localization:

    3.1) if (number_objects_detected >= 2) and (num_steps == 2):
    ```
    self.current_reward += -0.01
    ```
    3.2) if (number_objects_detected <= 1) and (num_steps == 2):
    ```
    self.current_reward += -0.1
    ```