from statistics import covariance
import numpy as np
from robot import robotModel

#State transition matrix: https://www.youtube.com/watch?v=uX5E8ZOI5Ms

class kalman:

    

    def __init__(self,n,map):
        robotObject = robotModel(False,n,map)
        # matrix of position and velocity of robot at time t.
        Xt = [[robotObject.pos_xt,robotObject.pos_zt],[robotObject.vel_xt,robotObject.vel_zt]] # [x,z,vx(dt),vz(dt)]
        # covariance matrix associated to Xt.
        Pt = [[self.cov(robotObject.pos_x,robotObject.pos_x),self.cov(robotObject.pos_x,robotObject.vel_x),
        self.cov(robotObject.pos_z,robotObject.pos_z),self.cov(robotObject.pos_z,robotObject.vel_z)
        ],[self.cov(robotObject.vel_x,robotObject.vel_x),self.cov(robotObject.vel_x,robotObject.pos_x),
        self.cov(robotObject.vel_z,robotObject.vel_z),self.cov(robotObject.vel_z,robotObject.pos_z)]]
        # Time for 1 cycle.
        self.dt = 1
        # State transition matrix
        self.A = np.array(np.identity(4))
        self.A[0][2] = self.dt
        self.A[1][3] = self.dt

    def cov(self,x:list[float],y:list[float]) -> int:
        """Compute the linear relationship between two random variables samples"""
        return covariance(x, y)

    


x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
y = [1, 2, 3, 1, 2, 3, 1, 2, 3]
kalmanObject = kalman()
print(kalmanObject.cov(x,y))

