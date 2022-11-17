import random

class robotModel:

    def __init__(self,localized,mapSize,map):
        x,z = self.initialPoseRandom(mapSize,map) 
        self.pos_x = x    
        self.pos_z = z 
        self.localized = localized
        self.laserRange = 3
        self.detectedObjects = 0

    def setLaserRange(self,rangeNumber):
        self.laserRange = rangeNumber
    
    def initialPoseRandom(self,mapSize,map):
        pos_allowed = True
        val_x = 0
        val_z = 0

        while(pos_allowed):
            # Random number from all possible grid positions 
            val = random.randint(0, mapSize*mapSize-1)
            
            # Check that we are not placing the robot in an already busy place.
            val_x = (val // mapSize)
            val_z = (val % mapSize)

            if map[val_x][val_z] != -1:
                    return val_x,val_z



        # Generating row and column from the number
        


    def moveUpOne(self):
        self.pos_x = self.pos_x + 1

    def moveDownOne(self):
        self.pos_x = self.pos_x -1

    def moveLeftOne(self):
        self.pos_z = self.pos_z -1

    def moveRightOne(self):
        self.pos_z = self.pos_z +1

    def objectDetected(self,isObject,temp_x,temp_z):
        if ((temp_x < self.pos_x+self.laserRange) and (isObject==-1)):
            return True  
        elif ((temp_z < self.pos_z+self.laserRange) and (isObject==-1)):
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

    
