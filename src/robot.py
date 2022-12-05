import random
from numpy.random import randn
from colour import Object_Colour

class robotModel:

    def __init__(self,localized,mapSize,gridMap):
        x,z = self.initialPoseRandom(mapSize,gridMap) 
        self.pos_xt = x # Position in x axes at time t.
        self.pos_zt = z # Position in z axes at time t.
        self.vel_xt = 0 # Velocity in x axes at time t.
        self.vel_zt = 0 # Voisy velocity in z axes at time t.
        self.pos_x = [self.pos_xt] # Noisy historical position in x axes.
        self.pos_z = [self.pos_zt] # Noisy historical position in z axes.
        self.vel_x = [0] # Noisy historical velocity in x axes.
        self.vel_z = [0] # Noisy historical velocity in z axes.
        self.localized = localized
        self.laserRange = 3
        self.detectedObjects = 0
    
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
                    # Put the color of the robot in the canvas.
                    gridMap.canvas.itemconfig(gridMap.map[val].tkinterCellIndex, fill=Object_Colour.Robot.value)
                    return gridMap.map[val].pos_x,gridMap.map[val].pos_z

    def gps(self):
        """Noisy gps position readings"""
        noise_std=0.1
        return self.pos_xt + randn() * noise_std, self.pos_zt + randn() * noise_std
        #return self.pos_xt,self.pos_zt

    def imu(self):
        """Noisy velocity readings"""
        noise_std=0.1
        return self.vel_xt + randn() * noise_std, self.vel_zt + randn() * noise_std 

    def moveUpOne(self):
        """Move one unit up - prob(slip low)"""
        self.pos_xt = self.pos_xt + 1

    def moveUpTwo(self):
        """Move one unit up - prob(slip high)"""
        self.pos_xt = self.pos_xt + 1

    def moveDownOne(self):
        """Move one unit down"""
        self.pos_xt = self.pos_xt -1

    def moveLeftOne(self):
        """Move one unit left"""
        self.pos_zt = self.pos_zt -1

    def moveRightOne(self):
        """Move one unit right"""
        self.pos_zt = self.pos_zt +1

    def objectDetected(self,isObject,temp_x,temp_z):
        if ((temp_x < self.pos_xt+self.laserRange) and (isObject==-1)):
            return True  
        elif ((temp_z < self.pos_zt+self.laserRange) and (isObject==-1)):
            return True
        else:
            return False

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


