from tkinter import *
from object import objectModel
from colour import Object_Colour

class Cell:

    def __init__(self,pos_x,pos_z,object,empty,indexTk):
        self.pos_x = pos_x       
        self.pos_z = pos_z
        self.empty = empty
        self.object = object
        self.tkinterCellIndex = indexTk
        self.colour = '#fff' # White
        self.reward = self.calculate_reward()

    def __init__(self,pos_x,pos_z,empty,indexTk):
        self.pos_x = pos_x       
        self.pos_z = pos_z
        self.empty = empty
        self.object = None
        self.tkinterCellIndex = indexTk
      
    def fill_cell(self,objectType):
        self.empty = False
        objectTemp = objectModel(self.pos_x,self.pos_z,objectType)
        self.colour = objectTemp.colour
        self.object = objectTemp

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
            self.reward = 1
