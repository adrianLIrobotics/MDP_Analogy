import random
from numpy.random import randn
from colour import Object_Colour

class robotModel:

    def __init__(self,localized,mapSize,gridMap,master):
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
        self.gridRobot1DPosition = 0
        self.gridMap = gridMap
        self.mapSize = mapSize
        self.collided = False
        self.master = master
    
    def coordinateTranslationTo1D(self, x_pos, z_pos):
        '''Convert 2D position array to 1D position array for TKinter canvas'''
        position1D = z_pos * (self.mapSize) + x_pos
        print("Translation: ",position1D)
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
                    # Put the color of the robot in the canvas.
                    gridMap.canvas.itemconfig(gridMap.map[val].tkinterCellIndex, fill=Object_Colour.Robot.value)
                    self.gridPosition = val
                    print(gridMap.map[val].pos_x,gridMap.map[val].pos_z)
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
        oldPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        newPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt-1)
        

        if (self.gridMap.map[newPosition].empty == False):
            self.collided = True
            print("Collided: ",self.collided)
            self.master.writeTextBox("Robot collided!")
        else:
            self.collided = False
            self.pos_zt -= 1
            self.pos_x.append(self.pos_xt)
            self.pos_z.append(self.pos_zt)

            # Remove robot from canvas actual position
            self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
            self.gridMap.map[oldPosition].object = None
            self.gridMap.map[oldPosition].empty = True
            # Move robot in canvas one up.
            self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)

            self.master.writeTextBox("Moved 1 Up")

    def moveUpTwo(self):
        """Move one unit up - prob(slip high)"""
        self.pos_xt = self.pos_xt + 1

    def moveDownOne(self):
        """Move one unit down"""
        oldPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        newPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt+1)

        if (self.gridMap.map[newPosition].empty == False):
            self.collided = True
            print("Collided: ",self.collided)
        else:
            self.collided = False
            self.pos_zt += 1
            self.pos_x.append(self.pos_xt)
            self.pos_z.append(self.pos_zt)

            # Remove robot from canvas actual position
            self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
            self.gridMap.map[oldPosition].object = None
            self.gridMap.map[oldPosition].empty = True
            # Move robot in canvas one up.
            self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
            self.master.writeTextBox("Moved 1 down")

    def moveLeftOne(self):
        """Move one unit left"""
        oldPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        newPosition = self.coordinateTranslationTo1D(self.pos_xt-1,self.pos_zt)

        if (self.gridMap.map[newPosition].empty == False):
            self.collided = True
            print("Collided: ",self.collided)
        else:
            self.collided = False
            self.pos_xt -= 1
            self.pos_x.append(self.pos_xt)
            self.pos_z.append(self.pos_zt)

            # Remove robot from canvas actual position
            self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
            self.gridMap.map[oldPosition].object = None
            self.gridMap.map[oldPosition].empty = True
            # Move robot in canvas one up.
            self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
            self.master.writeTextBox("Moved 1 Left")

    def moveRightOne(self):
        """Move one unit right"""
        oldPosition = self.coordinateTranslationTo1D(self.pos_xt,self.pos_zt)
        newPosition = self.coordinateTranslationTo1D(self.pos_xt+1,self.pos_zt)

        if (self.gridMap.map[newPosition].empty == False):
            self.collided = True
            print("Collided: ",self.collided)
        else:
            self.collided = False
            self.pos_xt += 1
            self.pos_x.append(self.pos_xt)
            self.pos_z.append(self.pos_zt)

            # Remove robot from canvas actual position
            self.gridMap.canvas.itemconfig(self.gridMap.map[oldPosition].tkinterCellIndex, fill='#fff')
            self.gridMap.map[oldPosition].object = None
            self.gridMap.map[oldPosition].empty = True
            # Move robot in canvas one up.
            self.gridMap.canvas.itemconfig(self.gridMap.map[newPosition].tkinterCellIndex, fill=Object_Colour.Robot.value)
            self.master.writeTextBox("Moved 1 Right")

    def objectDetected(self,isObject,temp_x,temp_z):
        if ((temp_x < self.pos_xt+self.laserRange) and (isObject==-1)):
            return True  
        elif ((temp_z < self.pos_zt+self.laserRange) and (isObject==-1)):
            return True
        else:
            return False

    def get_robot_actions(self):
        return ['moveUpOne','moveUpTwo','moveDownOne','moveDownTwo','moveLeftOne','moveLeftTwo','moveRightOne','moveRightTWo','stay']

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


