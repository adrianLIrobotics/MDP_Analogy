from tkinter import *
class Cell:

    def __init__(self,pos_x,pos_z,object,empty,indexTk):
        self.pos_x = pos_x       
        self.pos_z = pos_z
        self.empty = empty
        self.object = object
        self.tkinterCellIndex = indexTk

    def __init__(self,pos_x,pos_z,empty,indexTk):
        self.pos_x = pos_x       
        self.pos_z = pos_z
        self.empty = empty
        self.tkinterCellIndex = indexTk
      
    def fill_cell(self):
        self.empty = False

    def empty_cell(self):
        self.empty = True
