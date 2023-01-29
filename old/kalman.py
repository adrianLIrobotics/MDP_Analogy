from statistics import covariance
import numpy as np
#from robot import robotModel
from filterpy.kalman import KalmanFilter
import warnings
from scipy.linalg import block_diag
from filterpy.common import Q_discrete_white_noise
from numpy import array, asarray
from numpy.random import randn
import copy

class PosSensor1(object):
    def __init__(self, pos=(0, 0), vel=(0, 0), noise_std=1.):
        self.vel = vel
        self.noise_std = noise_std
        self.pos = [pos[0], pos[1]]
        
    def read(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        
        #print([self.pos[0] + randn() * self.noise_std,
         #       self.pos[1] + randn() * self.noise_std])
        #z [58.736110936863064, 29.607997705350797]

        return [self.pos[0] + randn() * self.noise_std,
                self.pos[1] + randn() * self.noise_std]


def tracker1():
    tracker = KalmanFilter(dim_x=4, dim_z=2)
    dt = 1.0   # time step

    tracker.F = np.array([[1, dt, 0,  0],
                          [0,  1, 0,  0],
                          [0,  0, 1, dt],
                          [0,  0, 0,  1]])
    tracker.u = 0.
    tracker.H = np.array([[1/0.3048, 0, 0, 0],
                          [0, 0, 1/0.3048, 0]])

    tracker.R = np.eye(2) * 5 # array([[5., 0.],
                              #       [0., 5.]])
    q = Q_discrete_white_noise(dim=2, dt=dt, var=0.05)
    tracker.Q = block_diag(q, q)
    tracker.x = np.array([[0, 0, 0, 0]]).T
    tracker.P = np.eye(4) * 500.
    return tracker

# simulate robot movement
N = 30
sensor = PosSensor1 ([0, 0], (2, 1), 1.)
#print(sensor.vel)
zs = np.array([np.array([sensor.read()]).T for _ in range(N)])
#print(zs)

# run filter
robot_tracker = tracker1()
mu, cov, _, _ = robot_tracker.batch_filter(zs)

print(mu)