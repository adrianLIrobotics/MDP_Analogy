from tkinter import *
from object import objectModel
from colour import Object_Colour
from configparser import ConfigParser
import pathlib

# Get general configuration data
config_path = pathlib.Path(__file__).parent.absolute() / "config.ini"
config = ConfigParser()
config.read(config_path)
mapSize = config['map']['mapSize']

class Cell:

    def __init__(self,pos_x,pos_z,object,empty,indexTk):
        self.pos_x = pos_x       
        self.pos_z = pos_z
        self.empty = empty
        self.object = object
        self.tkinterCellIndex = indexTk
        self.colour = '#fff' # White
        self.reward = self.calculate_reward()
        self.border = self.check_if_border() 
        self.border_edge = self.check_if_border_edge()
        self.first_column = self.check_first_column()
        self.last_column = self.check_last_column()
        self.first_row = self.check_if_first_row()
        self.lighting_condition = 0

    '''
    Constructor for a cell with no object. Empty white cell.
    '''
    def __init__(self,pos_x,pos_z,empty,indexTk):
        self.pos_x = pos_x       
        self.pos_z = pos_z
        self.empty = empty
        self.object = None
        self.reward = -0.04
        self.colour = '#fff' # By default the cell is white -none object Cell constructor-
        self.tkinterCellIndex = indexTk
        self.border = self.check_if_border() # If None --> no border tile
        self.border_edge = self.check_if_border_edge()
        self.first_column = self.check_first_column()
        self.last_column = self.check_last_column()
        self.first_row = self.check_if_first_row()
        self.last_row = self.check_if_last_row()
        self.lighting_condition = 0
       
    def update_reward(self):
        self.calculate_reward()

    def update_colour(self, colour_param):
        self.colour = colour_param

    '''
    Cells with property of been in the last row
    '''
    def check_if_last_row(self):
        for x in range (0,int(mapSize)): 
            if ((int(mapSize)**2)-int(mapSize)) < self.tkinterCellIndex <= int(mapSize)**2:
                return True
        return False
    '''
    Cells with property of been in the first row
    '''
    def check_if_first_row(self):
        for x in range (0,int(mapSize)): 
            if self.tkinterCellIndex <= int(mapSize):
                return True
        return False

    '''
    Cells with property of been in the first column.
    '''
    def check_first_column(self):
        for x in range (0,int(mapSize)): 
            if self.tkinterCellIndex == ((int(mapSize)*x)+1):
                return True
        return False
    '''
    Cells with property of been in the last column.
    '''
    def check_last_column(self):
        if self.tkinterCellIndex == int(mapSize)**2:
            return True
        for x in range (0,int(mapSize)): 
            if self.tkinterCellIndex == ((int(mapSize)*x)):
                return True
        return False

    '''
    The 4 corners of the grid
    '''
    def check_if_border_edge(self):
        if self.tkinterCellIndex == 1:
            return True
        if self.tkinterCellIndex == int(mapSize)**2:
            return True
        if self.tkinterCellIndex == int(mapSize):
            return True
        if self.tkinterCellIndex == ((int(mapSize)**2)-(int(mapSize)-1)):
            return True
        return False

    '''
    Define the bounderies of the map
    '''
    def check_if_border(self):
        if 1 <= self.tkinterCellIndex <= int(mapSize):
            return True
        if self.tkinterCellIndex == (int(mapSize) +1):
            return True
        # Last row first cell is a border:
        if self.tkinterCellIndex == (int(mapSize)**2 -(int(mapSize)-1)):
            return True
        # Last row is all a border:
        if int(mapSize)*(int(mapSize)-1)  <= self.tkinterCellIndex <= int(mapSize)*int(mapSize):
            return True
        for x in range (1,int(mapSize)): # Iterate by column
            if self.tkinterCellIndex == ((x-1)*int(mapSize))+1: # First column values are all borders.
                return True
            if self.tkinterCellIndex == int(mapSize)*x: # Las column is all a border
                return True
        return False
      
    def fill_cell(self,objectType):
        self.empty = False
        objectTemp = objectModel(self.pos_x,self.pos_z,objectType)
        self.colour = objectTemp.colour
        self.object = objectTemp
        self.reward = self.calculate_reward()

    def empty_cell(self):
        self.empty = True
        self.colour = '#fff'

    def calculate_reward(self):
        if self.colour == Object_Colour.Fire.value:
            self.reward = -1
        if self.colour == '#fff': # Empty tile 
            self.reward = -0.04
        if self.colour == Object_Colour.Wall.value:
            self.reward = -0.1
        if self.colour == Object_Colour.Goal.value:
            self.reward = 1000
