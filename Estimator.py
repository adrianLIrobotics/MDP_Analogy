from statistics import covariance
import numpy as np
from robot import robotModel
from filterpy.kalman import KalmanFilter
import warnings
warnings.filterwarnings("ignore")

# General tutorial: https://cocalc.com/share/public_paths/7557a5ac1c870f1ec8f01271959b16b49df9d087/08-Designing-Kalman-Filters.ipynb
# State transition matrix: https://www.youtube.com/watch?v=uX5E8ZOI5Ms

class predictor:


    def __init__(self,robotObject):
        kalmanFilterObject = KalmanFilter(dim_x=4, dim_z=2) # 4 metrics --> x,z,vx(dt),vz(dt)

        # Matrix of position and velocity of robot at time t.
        self.Xt = [[robotObject.gps()[0],robotObject.gps()[1]],[robotObject.imu()[0],robotObject.imu()[1] ]] # [x,z,vx(dt),vz(dt)]
    
        # Covariance matrix associated to Xt.
        try:
            self.Pt = [[self.cov(robotObject.pos_x,robotObject.pos_x),self.cov(robotObject.pos_x,robotObject.vel_x),
            self.cov(robotObject.pos_z,robotObject.pos_z),self.cov(robotObject.pos_z,robotObject.vel_z)
            ],[self.cov(robotObject.vel_x,robotObject.vel_x),self.cov(robotObject.vel_x,robotObject.pos_x),
            self.cov(robotObject.vel_z,robotObject.vel_z),self.cov(robotObject.vel_z,robotObject.pos_x)]]
        except:
            self.Pt = [[0,0,0,0],[0,0,0,0]] # Initial covarianza matrix at time t=0
        # Time for 1 cycle.
        self.dt = 1
        # State transition matrix
        self.A = np.array(np.identity(4))
        self.A[0][2] = self.dt
        self.A[1][3] = self.dt
        # State Transition Function
        kalmanFilterObject.F 

    def cov(self,x:list[float],y:list[float]) -> int:
        """Compute the linear relationship between two random variables samples"""
        return np.cov(x,y)#covariance(x, y)

    




