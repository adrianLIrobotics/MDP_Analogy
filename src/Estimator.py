from statistics import covariance
import numpy as np
#from robot import robotModel
from filterpy.kalman import KalmanFilter
import warnings
from scipy.linalg import block_diag
from filterpy.common import Q_discrete_white_noise
from numpy import array, asarray
warnings.filterwarnings("ignore")

# https://www.youtube.com/watch?v=fojH-viOxI4
# General tutorial: https://cocalc.com/share/public_paths/7557a5ac1c870f1ec8f01271959b16b49df9d087/08-Designing-Kalman-Filters.ipynb
# State transition matrix: https://www.youtube.com/watch?v=uX5E8ZOI5Ms

class predictor:
    #self.kalman = predictor(self.pos_x_noisy_encoder, self.pos_z_noisy_encoder, self.pos_x_noisy_camera, self.pos_z_noisy_camera)
    def __init__(self):
        self.tracker = KalmanFilter(dim_x=4, dim_z=2) # 4 metrics --> x,z,vx(dt),vz(dt) # dim_z = 2
        dt = 1.   # time step 1 

        # State model
        # x = [x, vel_x, z, vel_z]

        # State variables initial conditions 
        self.tracker.x = np.array([[0,0,0,0]]).T
        self.tracker.P = np.eye(4) * 500. # Since that is a pure guess, we will set the covariance matrix P to a large value.
        
        # State Transition Function
        self.tracker.F = np.array([[1, dt, 0,  0],
                      [0,  1, 0,  0],
                      [0,  0, 1, dt],
                      [0,  0, 0,  1]])

        # Process Noise Matrix
        q = Q_discrete_white_noise(dim=2, dt=dt, var=0.05)
        self.tracker.Q = block_diag(q, q)

        # Control Function TODO
        self.tracker.B

        # Measurement Function
        #self.tracker.H = array([[1., 0., 1., 0.], [1., 0., 1., 0.]]) # They are both positions, so the conversion is nothing more than multiplying by one:
        #self.tracker.H = array([[1, 0, 1, 0], [1, 0, 1, 0], [1, 0, 1, 0], [1, 0, 1, 0]])
        self.tracker.H = np.array([[1, 0, 0, 0],[0, 0, 1, 0]])

        # Measurement Noise Matrix
        self.tracker.R = np.eye(2) * 5
        #self.tracker.R[0, 0] = 1.5**2
        #self.tracker.R[1, 1] = 3**2

    def cov(self,x:list[float],y:list[float]) -> int:
        """Compute the linear relationship between two random variables samples"""
        return np.cov(x,y)#covariance(x, y)

    def predict(self, z): 
        # z and tracker.x should be the same shape.
        self.tracker.predict()
        self.tracker.update(z)

        return self.tracker.x, self.tracker.P.diagonal

        '''
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
        tracker.F 
        '''

    




