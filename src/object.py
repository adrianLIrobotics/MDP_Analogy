from tkinter import *
from colour import Object_Colour
class objectModel:

    def __init__(self,pos_x,pos_z,objectType):
        self.pos_x = pos_x       
        self.pos_z = pos_z
        self.objectType = objectType
        self.colladed = False
        self.colour = '#fff'

        if self.objectType == 'Wall':
            self.colour = Object_Colour.Wall.value
        if self.objectType == 'Water':
            self.colour = Object_Colour.Water.value
        if self.objectType == 'Fire':
            self.colour = Object_Colour.Fire.value