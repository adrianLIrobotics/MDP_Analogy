from tkinter import *
from object import objectModel

class Cell:

    def __init__(self,pos_x,pos_z,object,empty,indexTk):
        self.pos_x = pos_x       
        self.pos_z = pos_z
        self.empty = empty
        self.object = object
        self.tkinterCellIndex = indexTk
        self.colour = '#fff' # White

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
