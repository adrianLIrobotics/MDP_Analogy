import random
from numpy.random import randn
from colour import Object_Colour
from configparser import ConfigParser
import pathlib
import utilities
import logging
from datetime import date
import numpy as np
from Estimator import predictor
from numpy import array, asarray
from object import objectModel

# https://howtothink.readthedocs.io/en/latest/PvL_H.html

class robotModel:

    def __init__(self):
        self.pos_xt = 0
        self.pos_zt = 0

    def __init__(self,localized,mapSize,gridMap=None,master=None):

        if (master == None):
            self.pos_xt = 0
            self.pos_zt = 0
        else:
            '''Read configuration file'''
            config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"
            config = ConfigParser()
            config.read(config_path)
            self.initial_pose_x = config['robot']['initial_pose_x']
            self.initial_pose_z = config['robot']['initial_pose_z']
            initial_pose_known = config['robot']['initial_pose_known']
            range_laser = config['robot']['laser_range']

            '''Configure logger'''
            today = date.today()
            logging.basicConfig(filename='logs/'+str(today)+'.log', encoding='utf-8', level=logging.DEBUG)

            '''Configure robot initial position'''
            if (self.initial_pose_x == 'random') and (self.initial_pose_z == 'random'):
                x,z = self.initialPoseRandom(mapSize,gridMap) 
            else:
                x,z = self.manual_robot_pose(int(self.initial_pose_x),int(self.initial_pose_z),gridMap)

            self.gridMap = gridMap
            self.gaussian_variance_camera = float(config['robot']['camera_sensor_noise']) # Camera sensor robot noise.
            self.gaussian_variance_encoder = float(config['robot']['encoder_sensor_noise'])
            self.mapSize = int(config['map']['mapSize']) # Number of columns in map.
            self.pos_xt = x # Real Position in x axes at time t.
            self.pos_zt = z # Real Position in z axes at time t.
            self.vel_xt = 0 # Velocity in x axes at time t.
            self.vel_zt = 0 # Voisy velocity in z axes at time t.
            self.pos_x = [self.pos_xt] # Historical Real data in x axes.
            self.pos_z = [self.pos_zt] # Historical Real data in z axes.
            self.noisy_pos_xt_encoder = self.apply_gaussian_noise_encoder(self.pos_xt) # Noisy position in x axes at time t from encoder.
            self.noisy_pos_zt_encoder = self.apply_gaussian_noise_encoder(self.pos_zt) # Noisy position in z axes at time t from encoder.
            self.pos_x_noisy_encoder = [self.apply_gaussian_noise_encoder(self.pos_xt)] # Noisy historical position in x axes from encoder.
            self.pos_z_noisy_encoder = [self.apply_gaussian_noise_encoder(self.pos_zt)] # Noisy historical position in z axes from encoder.
            self.noisy_pos_xt_camera = self.apply_gaussian_noise_camera(self.pos_xt) # Noisy position in x axes at time t from camera sensor.
            self.noisy_pos_zt_camera = self.apply_gaussian_noise_camera(self.pos_zt) # Noisy position in z axes at time t from camera sensor.
            self.pos_x_noisy_camera = [self.apply_gaussian_noise_camera(self.pos_xt)] # Noisy historical position in x axes from camera sensor.
            self.pos_z_noisy_camera = [self.apply_gaussian_noise_camera(self.pos_zt)] # Noisy historical position in z axes from camera sensor.
            self.pos_xt_kalman = 0
            self.pos_zt_kalman = 0
            self.pos_1d_kalman = 0
            self.pos_x_kalman = [self.pos_xt_kalman]
            self.pos_z_kalman = [self.pos_zt_kalman]
            self.vel_x = [0] # Noisy historical velocity in x axes.
            self.vel_z = [0] # Noisy historical velocity in z axes.
            self.found_goal = False # By default the robot hasnt found the goal.
            self.goal_reached = False
            self.localized = localized # True if 90 or more --> Depricated, will not be used.
            self.laserRange = int(range_laser) # Robot laser range signal.
            self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])# x 2, z 0   
            self.gridMap.canvas.itemconfig(self.gridMap.map[self.gridRobot1DPosition].tkinterCellIndex, fill=Object_Colour.Robot.value) # Put the current cell as object of type robot.
            self.collided = False # Robot collided with object at time t.
            self.master = master
            self.cumulative_reward = 0
            self.current_reward = 0
            # Id's of robot actions
            moveUpOne = 0
            moveUpTwo = 1
            moveDownOne = 2
            moveDownTwo = 3
            moveLeftOne = 4
            moveLeftTwo = 5
            moveRightOne = 6
            moveRightTWo = 7
            stay = 8
            self.actions = [moveUpOne, moveUpTwo, moveDownOne, moveDownTwo, moveLeftOne, moveLeftTwo, moveRightOne, moveRightTWo]
            ''' Robot estimated initial pose definition'''
            if initial_pose_known == "Yes":
                self.pos_xt_estimated = self.pos_xt
                self.pos_zt_estimated = self.pos_zt
                self.localized_believe = 100 # Believe in % over localization
            else:
                self.pos_xt_estimated = 0 # Estimated position of robot in x axes at time t using kalman filter.
                self.pos_zt_estimated = 0 # Estimated position of robot in z axes at time t using kalman filter.
                self.localized_believe = 0 # Believe in % over localization

            self.pos_x_estimated = [self.pos_xt_estimated]  # Historical estimated position of robot in x axes.
            self.pos_z_estimated = [self.pos_zt_estimated] # Historical estimated position of robot in z axes.

            self.kalman = predictor() # Init kalman filter
            
    '''Apply gaussian noise over encoder signal'''
    def apply_gaussian_noise_encoder(self, data):
        try:
            noisy_data = round(np.random.normal(data,self.gaussian_variance_encoder,1)[0])
            return noisy_data
        except:
            # Init noisy
            noisy_data = round(np.random.normal(data,0.5,1)[0])
            return noisy_data

    '''Apply gaussian noise over camera signal'''
    def apply_gaussian_noise_camera(self, data):
        position = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        try:
            #print("Number of objects detected from camera: "+str(self.num_objects_detected()))
            # Depending on the number of objects the camera detects, position output is better or worse.
            if self.num_objects_detected() == 0:
                self.gaussian_variance_camera = 0.6
            elif self.num_objects_detected() == 1:
                self.gaussian_variance_camera = 0.3 # 0.4
            elif self.num_objects_detected() == 2:
                self.gaussian_variance_camera = 0.2
            elif self.num_objects_detected() == 3: #more than 3
                self.gaussian_variance_camera = 0.1
        except:
            pass

        # Check the lighing conditions of the cell the robot is in to calculate a proper variance over the gaussian normal.
        self.gaussian_variance_camera += utilities.get_variance_from_light_condition(self.gridMap.map[position].lighting_condition)
        try:
            noisy_data = round(np.random.normal(data,self.gaussian_variance_camera,1)[0])
            return noisy_data
        except:
            # Init noisy
            variance = 0.5 + utilities.get_variance_from_light_condition(self.gridMap.map[position].lighting_condition)
            noisy_data = round(np.random.normal(data,variance,1)[0])
            return noisy_data
        
    '''Return robot action id's'''
    def return_robot_actions_id(self):
        return self.actions

    '''Teleport robot to given coordinates''' 
    def manual_robot_pose(self,x,z,gridMap):
        pos_allowed = True
        
        while(pos_allowed):
            # Random number from all possible grid positions 
            val = utilities.get_state_from_pos((x,z))
#            print(gridMap.map[val].empty)
            if (gridMap.map[val].empty):
                gridMap.map[val].empty = False
                gridMap.map[val].colour = Object_Colour.Robot.value
                gridMap.map[val].object = self #Object_Colour.Robot.name
                # Put the color of the robot in the canvas.
                gridMap.canvas.itemconfig(gridMap.map[val].tkinterCellIndex, fill=Object_Colour.Robot.value)
                self.gridPosition = val
                #print(gridMap.map[val].pos_x,gridMap.map[val].pos_z)
                return gridMap.map[val].pos_x,gridMap.map[val].pos_z

    '''Convert 2D position array to 1D position array for TKinter canvas'''
    def coordinateTranslationTo1D(self, x_pos, z_pos):
        position1D = z_pos * (self.mapSize) + x_pos
        logging.debug("Translation: " + str(position1D))
        return position1D

    '''Robot kinematic equations'''
    def robotkinematicEquation(self):
        dt = 1
        self.pos_xt = self.pos_xt+(self.vel_xt*dt)
        self.pos_zt = self.pos_zt+(self.vel_zt*dt)

    '''Set robot laser sensor range'''
    def setLaserRange(self,rangeNumber):
        self.laserRange = rangeNumber
    
    '''Set initial random pose of robot '''
    def initialPoseRandom(self,mapSize,gridMap):
        pos_allowed = True
        while(pos_allowed):
            # Random number from all possible grid positions 
            val = random.randint(0, mapSize*mapSize-1)
            if (gridMap.map[val].empty):
                gridMap.map[val].empty = False
                gridMap.map[val].object = self#Object_Colour.Robot.name
                gridMap.map[val].object.objectType = Object_Colour.Robot.name
                # Put the color of the robot in the canvas.
                gridMap.canvas.itemconfig(gridMap.map[val].tkinterCellIndex, fill=Object_Colour.Robot.value)
                self.gridPosition = val
                logging.debug("Robot init pose: "+gridMap.map[val].pos_x,gridMap.map[val].pos_z)
                return gridMap.map[val].pos_x,gridMap.map[val].pos_z

    '''Noisy gps position readings'''
    def gps(self):
        noise_std=0.1
        return [self.pos_xt + randn() * noise_std, self.pos_zt + randn() * noise_std]

    '''Noisy velocity readings'''
    def imu(self):
        noise_std=0.1
        return self.vel_xt + randn() * noise_std, self.vel_zt + randn() * noise_std 

    '''
    Control command to move the robot in the up direction with
    parameter number of steps.
    '''
    def moveUp(self, num_steps):

        oldPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        collidedPlusOnePosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt-1)
        if (num_steps == 1):
            newPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt-1)
        else:
            newPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt-2)
        
        if (self.gridMap.map[newPosition].empty == False) | (newPosition < 0) | (self.gridMap.map[collidedPlusOnePosition].empty == False):
            self.collided = True
            if (num_steps == 1):
                self.cumulative_reward += -0.1
                self.current_reward = -0.1
                # If collided, robot position is the same
                newPosition = oldPosition
            else:
                # Collided act is worse if going faster
                self.cumulative_reward += -0.2
                self.current_reward = -0.2
                # If collided, robot position is the same
                newPosition = oldPosition
            #print("Collided: ",self.collided)
            self.master.writeTextBox("Robot collided!")
            # Check if robot can move at least one up.
            if ((self.gridMap.map[collidedPlusOnePosition].empty == True) and (self.gridMap.map[collidedPlusOnePosition].first_row)) or ((self.gridMap.map[collidedPlusOnePosition].empty == True) and not (self.gridMap.map[oldPosition].first_row)):
                #print("Moving only 1...")
                newPosition = collidedPlusOnePosition
                # Remove robot from canvas actual position
                self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
                self.gridMap.map[oldPosition].object = None
                self.gridMap.map[oldPosition].empty = True
                # Move robot in canvas one up.
                self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
                # Update robot internal pose
                self.pos_zt -= 1
        else:
            if (num_steps == 1):
                #print("Reward "+str(self.gridMap.map[newPosition].reward))# empty reward
                self.cumulative_reward += self.gridMap.map[newPosition].reward
                self.current_reward = self.gridMap.map[newPosition].reward
                self.pos_zt -= 1
            else:
                self.cumulative_reward += self.gridMap.map[newPosition].reward / 2
                self.current_reward = self.gridMap.map[newPosition].reward / 2
                self.pos_zt -= 2

            self.collided = False

            # Remove robot from canvas actual position
            self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
            self.gridMap.map[oldPosition].object = None
            self.gridMap.map[oldPosition].empty = True
            # Move robot in canvas one up.
            self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
            self.master.writeTextBox("Moved Up "+ str(num_steps))
        # Update control panel UI
        try:
            self.master.updateRewardTextBox(self.cumulative_reward)
        except:
            pass
        # Update new cell with object type robot and old cell of type #fff
        self.gridMap.map[newPosition].object = self
        self.gridMap.map[newPosition].object.objectType = Object_Colour.Robot.name
        #print("self.pos_zt " + str(self.pos_zt))
        #print("self.pos_xt " + str(self.pos_xt))
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])
        # Update history
        self.pos_x.append(self.pos_xt)
        self.pos_z.append(self.pos_zt)
        # Update noisy history
        self.pos_x_noisy_encoder.append(self.apply_gaussian_noise_encoder(self.pos_xt))
        self.pos_z_noisy_encoder.append(self.apply_gaussian_noise_encoder(self.pos_zt))
        self.pos_x_noisy_camera.append(self.apply_gaussian_noise_camera(self.pos_xt))
        self.pos_z_noisy_camera.append(self.apply_gaussian_noise_camera(self.pos_zt))
        '''Estimate new position using kalman filter'''
        z = array([[self.pos_x_noisy_camera[-1]],[self.pos_z_noisy_camera[-1]]])
        mu, cov = self.kalman.predict(z)
        #print("self.pos_x_noisy_camera[-1] "+str(self.pos_x_noisy_camera[-1]))
        #print("self.pos_z_noisy_camera[-1] "+str(self.pos_z_noisy_camera[-1]))
        
        # Update kalman signal history
        self.pos_xt_kalman =round(mu[0][0])
        self.pos_zt_kalman = round(mu[2][0])
        self.pos_1d_kalman = utilities.get_state_from_pos([self.pos_zt_kalman,self.pos_xt_kalman])
        self.pos_x_kalman.append(self.pos_xt_kalman)
        self.pos_z_kalman.append(self.pos_zt_kalman)

        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, newPosition, self.pos_xt, self.pos_1d_kalman, self.pos_xt_kalman, self.pos_zt_kalman)
        self.master.updateXPlot(self.pos_x, self.pos_x_noisy_encoder, self.pos_x_noisy_camera, self.pos_x_kalman)
        self.master.updateYPlot(self.pos_z, self.pos_z_noisy_encoder, self.pos_z_noisy_camera, self.pos_z_kalman)

        # Check if robot arrived to destionatio.
        if self.gridMap.map[newPosition].colour == Object_Colour.Goal.value:
            self.goal_reached = True

        self.gridMap.map[oldPosition].colour = '#fff'
        self.gridMap.map[newPosition].colour = Object_Colour.Robot.value

    '''
    Control command to move the robot in the down direction with
    parameter number of steps.
    '''
    def moveDown(self, num_steps):

        oldPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        collidedPlusOnePosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt+1)
        
        if (num_steps == 1):
            newPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt+1)
        else:
            newPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt+2)

        # Robot collided
        try:
            robot_collided = (self.gridMap.map[newPosition].empty == False) | (self.gridMap.map[collidedPlusOnePosition].empty == False)# | (newPosition < (self.mapSize**2))
        except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
            robot_collided = True
        if robot_collided:
            self.collided = True
            #print("Robot collided!")
            self.master.writeTextBox("Robot collided!")
            if (num_steps == 1):
                self.cumulative_reward += -0.1
                self.current_reward = -0.1
                # If collided, robot position is the same
                newPosition = oldPosition
            else:
                # Collided act is worse if going faster
                self.cumulative_reward += -0.2 
                self.current_reward = -0.2
                # If collided, robot position is the same
                newPosition = oldPosition

            # Check if robot can move at least one down.
            try: 
                move_one = ((self.gridMap.map[collidedPlusOnePosition].empty == True) and (self.gridMap.map[collidedPlusOnePosition].last_row)) or ((self.gridMap.map[collidedPlusOnePosition].empty == True) and not (self.gridMap.map[oldPosition].last_row))
            except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
                move_one = False
            if move_one:
                #"Moving only 1")
                newPosition = collidedPlusOnePosition
                # Remove robot from canvas actual position
                self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
                self.gridMap.map[oldPosition].object = None
                self.gridMap.map[oldPosition].empty = True
                # Move robot in canvas one down.
                self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
                # Update robot internal pose
                self.pos_zt += 1 

        # Robot did not collide
        else:
            if (num_steps == 1):
                self.cumulative_reward += self.gridMap.map[newPosition].reward
                self.current_reward = self.gridMap.map[newPosition].reward
                self.pos_zt += 1
            else:
                self.cumulative_reward += self.gridMap.map[newPosition].reward / 2
                self.current_reward = self.gridMap.map[newPosition].reward / 2
                self.pos_zt += 2

            self.collided = False
            # Remove robot from canvas actual position
            self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
            self.gridMap.map[oldPosition].object = None
            self.gridMap.map[oldPosition].empty = True
            # Move robot in canvas.
            self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
            self.master.writeTextBox("Moved down "+ str(num_steps))
                
        try:
            self.master.updateRewardTextBox(self.cumulative_reward)
        except:
            pass
        
        # Update new cell with object type robot and old cell of type #fff
        self.gridMap.map[newPosition].object = self
        self.gridMap.map[newPosition].object.objectType = Object_Colour.Robot.name
        #print("self.pos_zt " + str(self.pos_zt))
        #print("self.pos_xt " + str(self.pos_xt))
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])
        # Update history
        self.pos_x.append(self.pos_xt)
        self.pos_z.append(self.pos_zt)
        # Update noisy history
        self.pos_x_noisy_encoder.append(self.apply_gaussian_noise_encoder(self.pos_xt))
        self.pos_z_noisy_encoder.append(self.apply_gaussian_noise_encoder(self.pos_zt))
        self.pos_x_noisy_camera.append(self.apply_gaussian_noise_camera(self.pos_xt))
        self.pos_z_noisy_camera.append(self.apply_gaussian_noise_camera(self.pos_zt))
        '''Estimate new position using kalman filter'''
        z = array([[self.pos_x_noisy_camera[-1]],[self.pos_z_noisy_camera[-1]]])
        mu, cov = self.kalman.predict(z)

        self.pos_xt_kalman =round(mu[0][0])
        self.pos_zt_kalman = round(mu[2][0])
        self.pos_1d_kalman = utilities.get_state_from_pos([self.pos_zt_kalman,self.pos_xt_kalman])

        self.pos_x_kalman.append(self.pos_xt_kalman)
        self.pos_z_kalman.append(self.pos_zt_kalman)
        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, newPosition, self.pos_xt, self.pos_1d_kalman, self.pos_xt_kalman, self.pos_zt_kalman)
        self.master.updateXPlot(self.pos_x, self.pos_x_noisy_encoder, self.pos_x_noisy_camera, self.pos_x_kalman)
        self.master.updateYPlot(self.pos_z, self.pos_z_noisy_encoder, self.pos_z_noisy_camera, self.pos_z_kalman)

        # Check if robot arrived to destionatio.
        if self.gridMap.map[newPosition].colour == Object_Colour.Goal.value:
            self.goal_reached = True

        self.gridMap.map[oldPosition].colour = '#fff'
        self.gridMap.map[newPosition].colour = Object_Colour.Robot.value

    '''
    Control command to move the robot in the left direction with
    parameter number of steps.
    '''
    def moveLeft(self, num_steps):

        oldPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        collidedPlusOnePosition = self.coordinateTranslationTo1D(self.pos_xt-1,self.pos_zt)

        if (num_steps == 1):
            newPosition = self.coordinateTranslationTo1D(self.pos_xt-1,self.pos_zt)
        else:
            newPosition = self.coordinateTranslationTo1D(self.pos_xt-2,self.pos_zt)

        # Robot collided
        try:
            robot_collided = (self.gridMap.map[newPosition].empty == False) or (self.gridMap.map[oldPosition].first_column) or (self.gridMap.map[collidedPlusOnePosition].first_column and num_steps == 2) | (self.gridMap.map[collidedPlusOnePosition].empty == False)
        except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
            robot_collided = True
        if robot_collided:
            self.collided = True
            #print("Robot collided!")
            self.master.writeTextBox("Robot collided!")
            if (num_steps == 1):
                self.cumulative_reward += -0.1
                self.current_reward = -0.1
                # If collided, robot position is the same
                newPosition = oldPosition
            else:
                # Collided act is worse if going faster
                self.cumulative_reward += -0.2 
                self.current_reward = -0.2
                # If collided, robot position is the same
                newPosition = oldPosition

            # Check if robot can move at least one left.
            try: 
                move_one = ((self.gridMap.map[collidedPlusOnePosition].empty == True) and (self.gridMap.map[collidedPlusOnePosition].first_column)) or ((self.gridMap.map[collidedPlusOnePosition].empty == True) and not (self.gridMap.map[oldPosition].first_column))
            except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
                move_one = False

            if move_one:
                #print("Moving only 1")
                newPosition = collidedPlusOnePosition
                # Remove robot from canvas actual position
                self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
                self.gridMap.map[oldPosition].object = None
                self.gridMap.map[oldPosition].empty = True
                # Move robot in canvas one down.
                self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
                # Update robot internal pose
                self.pos_xt -= 1

        # Robot did not collide
        else:
            if (num_steps == 1):
                self.cumulative_reward += self.gridMap.map[newPosition].reward
                self.current_reward = self.gridMap.map[newPosition].reward
                self.pos_xt -= 1
            else:
                self.cumulative_reward += self.gridMap.map[newPosition].reward / 2
                self.current_reward = self.gridMap.map[newPosition].reward / 2
                self.pos_xt -= 2

            self.collided = False

            # Remove robot from canvas actual position
            self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
            self.gridMap.map[oldPosition].object = None
            self.gridMap.map[oldPosition].empty = True
            # Move robot in canvas.
            self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
            self.master.writeTextBox("Moved left "+ str(num_steps))

        try:
            self.master.updateRewardTextBox(self.cumulative_reward)
        except:
            pass
        
        # Update new cell with object type robot and old cell of type #fff
        self.gridMap.map[newPosition].object = self
        self.gridMap.map[newPosition].object.objectType = Object_Colour.Robot.name
        #print("self.pos_zt " + str(self.pos_zt))
        #print("self.pos_xt " + str(self.pos_xt))
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])
        # Update history
        self.pos_x.append(self.pos_xt)
        #print("self.pos_x h " +str(self.pos_x))
        self.pos_z.append(self.pos_zt)
        # Update noisy history
        self.pos_x_noisy_encoder.append(self.apply_gaussian_noise_encoder(self.pos_xt))
        self.pos_z_noisy_encoder.append(self.apply_gaussian_noise_encoder(self.pos_zt))
        self.pos_x_noisy_camera.append(self.apply_gaussian_noise_camera(self.pos_xt))
        self.pos_z_noisy_camera.append(self.apply_gaussian_noise_camera(self.pos_zt))
        '''Estimate new position using kalman filter'''
        z = array([[self.pos_x_noisy_camera[-1]],[self.pos_z_noisy_camera[-1]]])
        mu, cov = self.kalman.predict(z)

        self.pos_xt_kalman =round(mu[0][0])
        self.pos_zt_kalman = round(mu[2][0])
        self.pos_1d_kalman = utilities.get_state_from_pos([self.pos_zt_kalman,self.pos_xt_kalman])
        self.pos_x_kalman.append(self.pos_xt_kalman)
        self.pos_z_kalman.append(self.pos_zt_kalman)

        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, newPosition, self.pos_xt, self.pos_1d_kalman, self.pos_xt_kalman, self.pos_zt_kalman)
        self.master.updateXPlot(self.pos_x, self.pos_x_noisy_encoder, self.pos_x_noisy_camera, self.pos_x_kalman)
        self.master.updateYPlot(self.pos_z, self.pos_z_noisy_encoder, self.pos_z_noisy_camera, self.pos_z_kalman)

        # Check if robot arrived to destionatio.
        if self.gridMap.map[newPosition].colour == Object_Colour.Goal.value:
            self.goal_reached = True
        
        self.gridMap.map[oldPosition].colour = '#fff'
        self.gridMap.map[newPosition].colour = Object_Colour.Robot.value

    '''
    Control command to move the robot in the right direction with
    parameter number of steps.
    '''  
    def moveRight(self, num_steps):

        oldPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        collidedPlusOnePosition = self.coordinateTranslationTo1D(self.pos_xt+1,self.pos_zt)

        if (num_steps == 1):
            newPosition = self.coordinateTranslationTo1D(self.pos_xt+1,self.pos_zt)
        else:
            newPosition = self.coordinateTranslationTo1D(self.pos_xt+2,self.pos_zt)

        # Robot collided
        try:
            robot_collided = (self.gridMap.map[newPosition].empty == False) or (self.gridMap.map[oldPosition].last_column) or (self.gridMap.map[collidedPlusOnePosition].last_column and num_steps == 2) | (self.gridMap.map[collidedPlusOnePosition].empty == False)
        except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
            robot_collided = True
        if robot_collided:
            self.collided = True
            #print("Robot collided!")
            self.master.writeTextBox("Robot collided!")
            if (num_steps == 1):
                self.cumulative_reward += -0.1
                self.current_reward = -0.1
                # If collided, robot position is the same
                newPosition = oldPosition
            else:
                # Collided act is worse if going faster
                self.cumulative_reward += -0.2 
                self.current_reward = -0.2
                # If collided, robot position is the same
                newPosition = oldPosition

            # Check if robot can move at least one left.
            try: 
                move_one = ((self.gridMap.map[collidedPlusOnePosition].empty == True) and (self.gridMap.map[collidedPlusOnePosition].last_column)) or ((self.gridMap.map[collidedPlusOnePosition].empty == True) and not (self.gridMap.map[oldPosition].last_column))
            except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
                move_one = False

            if move_one:
                #print("Moving only 1")
                newPosition = collidedPlusOnePosition
                # Remove robot from canvas actual position
                self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
                self.gridMap.map[oldPosition].object = None
                self.gridMap.map[oldPosition].empty = True
                # Move robot in canvas one down.
                self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
                # Update robot internal pose
                self.pos_xt += 1

        # Robot did not collide
        else:
            if (num_steps == 1):
                print("Reward: "+str(self.gridMap.map[newPosition].reward))
                self.cumulative_reward += self.gridMap.map[newPosition].reward
                self.current_reward = self.gridMap.map[newPosition].reward
                self.pos_xt += 1
            else:
                self.cumulative_reward += self.gridMap.map[newPosition].reward / 2
                self.current_reward = self.gridMap.map[newPosition].reward / 2
                self.pos_xt += 2

            self.collided = False

            # Remove robot from canvas actual position
            self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
            self.gridMap.map[oldPosition].object = None
            self.gridMap.map[oldPosition].empty = True
            # Move robot in canvas.
            self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
            self.master.writeTextBox("Moved left "+ str(num_steps))

        try:
            self.master.updateRewardTextBox(self.cumulative_reward)
        except:
            pass
        
        # Update new cell with object type robot and old cell of type #fff
        self.gridMap.map[newPosition].object = self
        self.gridMap.map[newPosition].object.objectType = Object_Colour.Robot.name
        #print("self.pos_zt " + str(self.pos_zt))
        #print("self.pos_xt " + str(self.pos_xt))
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])
        # Update history
        self.pos_x.append(self.pos_xt)
        self.pos_z.append(self.pos_zt)
        # Update noisy history
        self.pos_x_noisy_encoder.append(self.apply_gaussian_noise_encoder(self.pos_xt))
        self.pos_z_noisy_encoder.append(self.apply_gaussian_noise_encoder(self.pos_zt))
        self.pos_x_noisy_camera.append(self.apply_gaussian_noise_camera(self.pos_xt))
        self.pos_z_noisy_camera.append(self.apply_gaussian_noise_camera(self.pos_zt))

        '''Estimate new position using kalman filter'''
        z = array([[self.pos_x_noisy_camera[-1]],[self.pos_z_noisy_camera[-1]]])
        mu, cov = self.kalman.predict(z)
        self.pos_xt_kalman =round(mu[0][0])
        self.pos_zt_kalman = round(mu[2][0])
        self.pos_1d_kalman = utilities.get_state_from_pos([self.pos_zt_kalman,self.pos_xt_kalman])
        self.pos_x_kalman.append(self.pos_xt_kalman)
        self.pos_z_kalman.append(self.pos_zt_kalman)

        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, newPosition, self.pos_xt, self.pos_1d_kalman, self.pos_xt_kalman, self.pos_zt_kalman)
        self.master.updateXPlot(self.pos_x, self.pos_x_noisy_encoder, self.pos_x_noisy_camera, self.pos_x_kalman)
        self.master.updateYPlot(self.pos_z, self.pos_z_noisy_encoder, self.pos_z_noisy_camera, self.pos_z_kalman) 

        # Check if robot arrived to destionatio.
        if self.gridMap.map[newPosition].colour == Object_Colour.Goal.value:
            self.goal_reached = True

        self.gridMap.map[oldPosition].colour = '#fff'
        self.gridMap.map[newPosition].colour = Object_Colour.Robot.value

    '''Get number of objects detected and check if goal found.'''
    def num_objects_detected(self):
        #print("2. self.gridRobot1DPosition "+ str(self.gridRobot1DPosition))
        num_objects_detected = 0
        # Check up
        for x in range(1, self.laserRange + 1):
            try:
                if (self.gridRobot1DPosition-self.mapSize*x) < 0: # Out of bounds
                    break
                if self.gridMap.map[self.gridRobot1DPosition-self.mapSize*x].empty == False:
                    num_objects_detected += 1
                    logging.debug("found object in front")
                    break # If there are further objects behind the one detected by robot, they will not be seen.
                if self.gridMap.map[self.gridRobot1DPosition-self.mapSize*x].colour == Object_Colour.Goal.value:
                    self.found_goal = True
                    self.master.writeTextBox("Goal found!")
            except:
                #print("exception: ")
                pass
        
        # Check down
        for x in range(1, self.laserRange + 1):
            try:
                if self.gridMap.map[self.gridRobot1DPosition+self.mapSize*x].empty == False:
                    num_objects_detected += 1
                    break # If there are further objects behind the one detected by robot, they will not be seen.
                if self.gridMap.map[self.gridRobot1DPosition+self.mapSize*x].colour == Object_Colour.Goal.value:
                    self.found_goal = True
                    self.master.writeTextBox("Goal found!")
            except:
                pass
        # Check right
        for x in range(1, self.laserRange + 1):
            try:
                if self.gridMap.map[self.gridRobot1DPosition+x].empty == False:
                    num_objects_detected += 1
                    break # If there are further objects behind the one detected by robot, they will not be seen.
                if self.gridMap.map[self.gridRobot1DPosition+x].colour == Object_Colour.Goal.value:
                    self.found_goal = True
                    self.master.writeTextBox("Goal found!")
            except:
                pass
        # Check left
        for x in range(1, self.laserRange + 1):
            try:
                if self.gridMap.map[self.gridRobot1DPosition-x].empty == False:
                    num_objects_detected += 1
                    break # If there are further objects behind the one detected by robot, they will not be seen.
                if self.gridMap.map[self.gridRobot1DPosition+x].colour == Object_Colour.Goal.value:
                    self.found_goal = True
                    self.master.writeTextBox("Goal found!")
            except:
                pass
        #print("num_objects_detected: ",num_objects_detected)
        return num_objects_detected


    def objectDetected(self,isObject,temp_x,temp_z):
        if ((temp_x < self.pos_xt+self.laserRange) and (isObject==-1)):
            return True  
        elif ((temp_z < self.pos_zt+self.laserRange) and (isObject==-1)):
            return True
        else:
            return False

    def get_robot_actions(self):
        return ['moveUpOne','moveUpTwo','moveDownOne','moveDownTwo','moveLeftOne','moveLeftTwo','moveRightOne','moveRightTWo','stay']

    def get_number_actions(self):
        return 9

    def robotCrushed(self):
        return True


    '''Reset simulation to the initial configuration.'''
    def reset_simulation(self):
        print("Reset simulation...")
        
        self.gridMap.map[self.gridRobot1DPosition].colour = '#fff'
        self.gridMap.canvas.itemconfig(self.gridMap.map[self.gridRobot1DPosition].tkinterCellIndex, fill='#fff')

        # 1. Put back the color of the goal cell in init pose of goal and add object type goal.
        goalObject = objectModel(self.gridMap.goal_x_pose,self.gridMap.goal_z_pose,Object_Colour.Goal.name)
        self.gridMap.map[self.gridMap.goal_1D_pose].object = goalObject
        self.gridMap.canvas.itemconfig(self.gridMap.map[self.gridMap.goal_1D_pose].tkinterCellIndex, fill=Object_Colour.Goal.value)
        self.gridMap.map[self.gridMap.goal_1D_pose].colour = Object_Colour.Goal.value
        

        # 2. Reset all rewards for robot and history.
        temp_robot_pose = utilities.get_state_from_pos((int(self.pos_xt),int(self.pos_zt)))
        self.gridMap.map[temp_robot_pose].empty = True
        temp_robot_pose2 = utilities.get_state_from_pos((int(self.initial_pose_x),int(self.initial_pose_z)))
        self.gridMap.map[temp_robot_pose2].empty = True
        x,z = self.manual_robot_pose(int(self.initial_pose_x),int(self.initial_pose_z),self.gridMap) # Will move the robot also in the simulation.
        
        self.pos_xt = x # Reset real Position in x axes at time t.
        self.pos_zt = z # Reset real Position in z axes at time t.
        self.vel_xt = 0 # Reset velocity in x axes at time t.
        self.vel_zt = 0 # Reset velocity in x axes at time t.
        

        self.noisy_pos_xt_encoder = self.apply_gaussian_noise_encoder(self.pos_xt)
        self.noisy_pos_zt_encoder = self.apply_gaussian_noise_encoder(self.pos_zt)
        self.noisy_pos_xt_camera = self.apply_gaussian_noise_camera(self.pos_xt)
        self.noisy_pos_zt_camera = self.apply_gaussian_noise_camera(self.pos_zt)

        self.pos_x.clear()
        self.pos_z.clear()
        self.pos_x_noisy_encoder.clear()
        self.pos_z_noisy_encoder.clear()
        self.pos_x_noisy_camera.clear()
        self.pos_z_noisy_camera.clear()

        self.pos_xt_kalman = 0
        self.pos_zt_kalman = 0
        self.pos_x_kalman.clear()
        self.pos_z_kalman.clear()

        self.vel_x.clear()
        self.vel_z.clear()
        self.found_goal = False # By default the robot hasnt found the goal.
        self.localized = False # True if 90 or more
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])# x 2, z 0   
        self.collided = False # Robot collided with object at time t.
        self.cumulative_reward = 0
        self.goal_reached = False

        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, self.gridRobot1DPosition, self.pos_xt, self.pos_1d_kalman, self.pos_xt_kalman, self.pos_zt_kalman)
        self.master.updateXPlot(self.pos_x, self.pos_x_noisy_encoder, self.pos_x_noisy_camera, self.pos_x_kalman)
        self.master.updateYPlot(self.pos_z, self.pos_z_noisy_encoder, self.pos_z_noisy_camera, self.pos_z_kalman)
        

    def amcl(self,map): 
        # Needs at least detecting two objects for localization. If not, robot lost.
        numberDetectedObjects = 0
        temp_x = 0
        temp_z = 0
        for row in map:
            for value in row:
                detected = self.objectDetected(value,temp_x,temp_z)
                temp_z = temp_z +1
                if detected == True: numberDetectedObjects = numberDetectedObjects +1
            temp_x = temp_x +1

        # Update the number of objects the robot is currently detecting.
        self.detectedObjects = numberDetectedObjects
        if numberDetectedObjects >=2:
            self.localized = False
            return False
        else:
            self.localized = True
            return True


