from statistics import covariance
import numpy as np
#from robot import robotModel
from filterpy.kalman import KalmanFilter
import warnings
warnings.filterwarnings("ignore")

# https://www.youtube.com/watch?v=fojH-viOxI4
# General tutorial: https://cocalc.com/share/public_paths/7557a5ac1c870f1ec8f01271959b16b49df9d087/08-Designing-Kalman-Filters.ipynb
# State transition matrix: https://www.youtube.com/watch?v=uX5E8ZOI5Ms

class predictor:


    def __init__(self,noisy_pos_xt, noisy_pos_zt, num_steps):
        kalmanFilterObject = KalmanFilter(dim_x=4, dim_z=2) # 4 metrics --> x,z,vx(dt),vz(dt)

        # Matrix of position and velocity of robot at time t.
        self.Xt = [[noisy_pos_xt,noisy_pos_zt],[num_steps,num_steps ]] # [x,z,vx(dt),vz(dt)]
        vel_x = num_steps
        vel_z = num_steps
    
        # Covariance matrix associated to Xt.
        try:
            self.Pt = [[self.cov(noisy_pos_xt,noisy_pos_xt),self.cov(noisy_pos_xt,vel_x),
            self.cov(noisy_pos_zt,noisy_pos_zt),self.cov(noisy_pos_zt,vel_z)
            ],[self.cov(vel_x,vel_x),self.cov(vel_x,noisy_pos_xt),
            self.cov(vel_z,vel_z),self.cov(vel_z,noisy_pos_xt)]]
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

    




