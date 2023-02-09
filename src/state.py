class state_model:

    def __init__(self,gridMap,robot):
        self.grid = gridMap
        self.robotPose = robot.pos_xt, robot.pos_zt
        #self.localized_robot_believe = robot.localized_believe
        
    def __eq__(self, other):
        return isinstance(other, state_model) and self.grid == other.grid and self.robotPose == other.robotPose
    
    def __hash__(self):
        return hash(str(self.grid) + str(self.robotPose))
    
    def __str__(self):
        return f"State(grid={self.grid}, car_pos={self.robotPose})"