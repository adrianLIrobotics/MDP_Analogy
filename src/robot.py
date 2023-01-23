import random
from numpy.random import randn
from colour import Object_Colour
from configparser import ConfigParser
import pathlib
import utilities
import logging
from datetime import date

# https://howtothink.readthedocs.io/en/latest/PvL_H.html

class robotModel:

    def __init__(self,localized,mapSize,gridMap,master):
        # Read configuration file
        config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"
        config = ConfigParser()
        config.read(config_path)
        initial_pose_x = config['robot']['initial_pose_x']
        initial_pose_z = config['robot']['initial_pose_z']

        #Configure logger
        today = date.today()
        logging.basicConfig(filename='logs/'+str(today)+'.log', encoding='utf-8', level=logging.DEBUG)

        # Configure robot initial position.
        if (initial_pose_x == 'random') and (initial_pose_z == 'random'):
            x,z = self.initialPoseRandom(mapSize,gridMap) 
        else:
           x,z = self.manual_robot_pose(int(initial_pose_x),int(initial_pose_z),gridMap)
           #x += 1 # Off set 

        self.pos_xt = x # Position in x axes at time t.
        self.pos_zt = z # Position in z axes at time t.
        self.vel_xt = 0 # Velocity in x axes at time t.
        self.vel_zt = 0 # Voisy velocity in z axes at time t.
        self.pos_x = [self.pos_xt] # Noisy historical position in x axes.
        self.pos_z = [self.pos_zt] # Noisy historical position in z axes.
        self.vel_x = [0] # Noisy historical velocity in x axes.
        self.vel_z = [0] # Noisy historical velocity in z axes.
        self.found_goal = False # By default the robot hasnt found the goal.
        self.localized = localized
        self.localized_believe = 0
        self.laserRange = 1

        #self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_xt,self.pos_zt])
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])# x 2, z 0   
        self.gridMap = gridMap
        self.mapSize = mapSize
        self.collided = False
        self.master = master
        self.cumulative_reward = 0

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
        self.actions = [moveUpOne, moveUpTwo, moveDownOne, moveDownTwo, moveLeftOne, moveLeftTwo, moveRightOne, moveRightTWo, stay]

        # Update Control panel with initial data of robot:
        
    def return_robot_actions_id(self):
        return self.actions

    '''
    Teleport robot to given coordinates.
    '''
    def manual_robot_pose(self,x,z,gridMap):
        pos_allowed = True
        
        while(pos_allowed):
            # Random number from all possible grid positions 
            val = utilities.get_state_from_pos((x,z))
            print("val ",val)
            if (gridMap.map[val].empty):
                gridMap.map[val].empty = False
                gridMap.map[val].object = self #Object_Colour.Robot.name
                # Put the color of the robot in the canvas.
                gridMap.canvas.itemconfig(gridMap.map[val].tkinterCellIndex, fill=Object_Colour.Robot.value)
                self.gridPosition = val
                print(gridMap.map[val].pos_x,gridMap.map[val].pos_z)
                return gridMap.map[val].pos_x,gridMap.map[val].pos_z
    
    def coordinateTranslationTo1D(self, x_pos, z_pos):
        '''Convert 2D position array to 1D position array for TKinter canvas'''
        position1D = z_pos * (self.mapSize) + x_pos
        logging.debug("Translation: " + str(position1D))
        return position1D

    def robotkinematicEquation(self):
        dt = 1
        self.pos_xt = self.pos_xt+(self.vel_xt*dt)
        self.pos_zt = self.pos_zt+(self.vel_zt*dt)

    def setLaserRange(self,rangeNumber):
        self.laserRange = rangeNumber
    
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

    def gps(self):
        """Noisy gps position readings"""
        noise_std=0.1
        return [self.pos_xt + randn() * noise_std, self.pos_zt + randn() * noise_std]

    def imu(self):
        """Noisy velocity readings"""
        noise_std=0.1
        return self.vel_xt + randn() * noise_std, self.vel_zt + randn() * noise_std 

    '''
    Control command to move the robot in the up direction with
    parameter number of steps.
    '''
    def moveUp(self, num_steps):
        # Update history
        self.pos_x.append(self.pos_xt)
        self.pos_z.append(self.pos_zt)

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
                # If collided, robot position is the same
                newPosition = oldPosition
            else:
                # Collided act is worse if going faster
                self.cumulative_reward += -0.2
                # If collided, robot position is the same
                newPosition = oldPosition
            print("Collided: ",self.collided)
            self.master.writeTextBox("Robot collided!")
            # Check if robot can move at least one up.
            if ((self.gridMap.map[collidedPlusOnePosition].empty == True) and (self.gridMap.map[collidedPlusOnePosition].first_row)) or ((self.gridMap.map[collidedPlusOnePosition].empty == True) and not (self.gridMap.map[oldPosition].first_row)):
                print("Moving only 1...")
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
                self.cumulative_reward += self.gridMap.map[newPosition].reward
                self.pos_zt -= 1
            else:
                self.cumulative_reward += self.gridMap.map[newPosition].reward / 2
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
        print("self.pos_zt " + str(self.pos_zt))
        print("self.pos_xt " + str(self.pos_xt))
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])
        print("now good gridRobot1DPosition" + str(self.gridRobot1DPosition))
        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, newPosition, self.pos_xt)
        print("pos_x "+str(self.pos_x))
        self.master.updateXPlot(self.pos_x)
    '''
    Control command to move the robot in the down direction with
    parameter number of steps.
    '''
    def moveDown(self, num_steps):
        """Move one unit down"""
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
            print("Robot collided!")
            self.master.writeTextBox("Robot collided!")
            if (num_steps == 1):
                self.cumulative_reward += -0.1
                # If collided, robot position is the same
                newPosition = oldPosition
            else:
                # Collided act is worse if going faster
                self.cumulative_reward += -0.2 
                # If collided, robot position is the same
                newPosition = oldPosition

            # Check if robot can move at least one down.
            try: 
                move_one = ((self.gridMap.map[collidedPlusOnePosition].empty == True) and (self.gridMap.map[collidedPlusOnePosition].last_row)) or ((self.gridMap.map[collidedPlusOnePosition].empty == True) and not (self.gridMap.map[oldPosition].last_row))
            except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
                move_one = False
            if move_one:
                print("Moving only 1")
                newPosition = collidedPlusOnePosition
                # Remove robot from canvas actual position
                self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
                self.gridMap.map[oldPosition].object = None
                self.gridMap.map[oldPosition].empty = True
                # Move robot in canvas one down.
                self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
                # Update robot internal pose
                self.pos_zt += 1
                # Update history
                self.pos_x.append(self.pos_xt)
                self.pos_z.append(self.pos_zt)

        # Robot did not collide
        else:
            if (num_steps == 1):
                self.cumulative_reward += self.gridMap.map[newPosition].reward
                self.pos_zt += 1
            else:
                self.cumulative_reward += self.gridMap.map[newPosition].reward / 2
                self.pos_zt += 2

            self.collided = False
            # Append to historical path
            self.pos_x.append(self.pos_xt)
            self.pos_z.append(self.pos_zt)

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
        print("self.pos_zt " + str(self.pos_zt))
        print("self.pos_xt " + str(self.pos_xt))
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])
        print("1. now good gridRobot1DPosition " + str(self.gridRobot1DPosition))

        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, newPosition, self.pos_xt)

    '''
    Control command to move the robot in the left direction with
    parameter number of steps.
    '''
    def moveLeft(self, num_steps):
        """Move left"""
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
            print("Robot collided!")
            self.master.writeTextBox("Robot collided!")
            if (num_steps == 1):
                self.cumulative_reward += -0.1
                # If collided, robot position is the same
                newPosition = oldPosition
            else:
                # Collided act is worse if going faster
                self.cumulative_reward += -0.2 
                # If collided, robot position is the same
                newPosition = oldPosition

            # Check if robot can move at least one left.
            try: 
                move_one = ((self.gridMap.map[collidedPlusOnePosition].empty == True) and (self.gridMap.map[collidedPlusOnePosition].first_column)) or ((self.gridMap.map[collidedPlusOnePosition].empty == True) and not (self.gridMap.map[oldPosition].first_column))
            except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
                move_one = False

            if move_one:
                print("Moving only 1")
                newPosition = collidedPlusOnePosition
                # Remove robot from canvas actual position
                self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
                self.gridMap.map[oldPosition].object = None
                self.gridMap.map[oldPosition].empty = True
                # Move robot in canvas one down.
                self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
                # Update robot internal pose
                self.pos_xt -= 1
                # Update history
                self.pos_x.append(self.pos_xt)
                self.pos_z.append(self.pos_zt)

        # Robot did not collide
        else:
            if (num_steps == 1):
                self.cumulative_reward += self.gridMap.map[newPosition].reward
                self.pos_xt -= 1
            else:
                self.cumulative_reward += self.gridMap.map[newPosition].reward / 2
                self.pos_xt -= 2

            self.collided = False
            # Append to historical path
            self.pos_x.append(self.pos_xt)
            self.pos_z.append(self.pos_zt)

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
        print("self.pos_zt " + str(self.pos_zt))
        print("self.pos_xt " + str(self.pos_xt))
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])
        print("1. now good gridRobot1DPosition " + str(self.gridRobot1DPosition))
        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, newPosition, self.pos_xt)

    '''
    Control command to move the robot in the right direction with
    parameter number of steps.
    '''  
    def moveRight(self, num_steps):
        """Moves right"""
        print("num_steps ", str(num_steps))
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
            print("Robot collided!")
            self.master.writeTextBox("Robot collided!")
            if (num_steps == 1):
                self.cumulative_reward += -0.1
                # If collided, robot position is the same
                newPosition = oldPosition
            else:
                # Collided act is worse if going faster
                self.cumulative_reward += -0.2 
                # If collided, robot position is the same
                newPosition = oldPosition

            # Check if robot can move at least one left.
            try: 
                move_one = ((self.gridMap.map[collidedPlusOnePosition].empty == True) and (self.gridMap.map[collidedPlusOnePosition].last_column)) or ((self.gridMap.map[collidedPlusOnePosition].empty == True) and not (self.gridMap.map[oldPosition].last_column))
            except: # out of scope number from grid, means robot is trying to exit natural limits of grid.
                move_one = False

            if move_one:
                print("Moving only 1")
                newPosition = collidedPlusOnePosition
                # Remove robot from canvas actual position
                self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
                self.gridMap.map[oldPosition].object = None
                self.gridMap.map[oldPosition].empty = True
                # Move robot in canvas one down.
                self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
                # Update robot internal pose
                self.pos_xt += 1
                # Update history
                self.pos_x.append(self.pos_xt)
                self.pos_z.append(self.pos_zt)

        # Robot did not collide
        else:
            if (num_steps == 1):
                self.cumulative_reward += self.gridMap.map[newPosition].reward
                self.pos_xt += 1
            else:
                self.cumulative_reward += self.gridMap.map[newPosition].reward / 2
                self.pos_xt += 2

            self.collided = False
            # Append to historical path
            self.pos_x.append(self.pos_xt)
            self.pos_z.append(self.pos_zt)

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
        print("self.pos_zt " + str(self.pos_zt))
        print("self.pos_xt " + str(self.pos_xt))
        self.gridRobot1DPosition = utilities.get_state_from_pos([self.pos_zt,self.pos_xt])
        print("1. now good gridRobot1DPosition " + str(self.gridRobot1DPosition))
        self.master.update_control_panel(self.num_objects_detected(), self.pos_zt, newPosition, self.pos_xt)

    '''
    Get number of objects detected and check if goal found.
    '''
    def num_objects_detected(self):
        print("2. self.gridRobot1DPosition "+ str(self.gridRobot1DPosition))
        num_objects_detected = 0
        # Check up
        for x in range(1, self.laserRange + 1):
            logging.debug("x: " +str(x))
            logging.debug("self.gridRobot1DPosition " +str(self.gridRobot1DPosition))
            logging.debug("self.mapSize " + str(self.mapSize))
            logging.debug("calculation: "+ str(self.gridRobot1DPosition-self.mapSize*x))
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
                print("exception: ")
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
        print("num_objects_detected: ",num_objects_detected)
        
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


