import sys
from tkinter import *
from tkinter import filedialog
from object import objectModel
from colour import Object_Colour
from robot import robotModel
from map import Map
from policy import PolicyModel
from mdp import Mdp

# A simple colouring grid app, with load/save functionality.
# Christian Hill, August 2018.

# The "default" colour for an unfilled grid cell
UNFILLED = '#fff'

class GridApp:
    """The main class representing a grid of coloured cells."""

    # The colour palette
    colours = (UNFILLED, 'red', 'green', 'blue', 'cyan', 'orange', 'yellow',
               'magenta', 'brown', 'black')
    ncolours = len(colours)

    def key_pressed(self,event):
        print(event.char)

    def setNumberFeatures(self,event):
            featureNumber = self.inputFeatures.get(1.0, "end-1c")
            print(featureNumber)

    def clearTextBox(self):
        self.debug.delete(1.0, END)

    def writeTextBox(self,text):
        self.debug.insert(END,str(text)+"\n")

    def __init__(self, master, n, width=1000, height=1500, pad=5): # width=600, height=600
        """Initialize a grid and the Tk Frame on which it is rendered."""
        
        # Number of cells in each dimension.
        self.n = n
        # Some dimensions for the App in pixels.
        self.width, self.height = width, height
        palette_height = 40
        # Padding stuff: xsize, ysize is the cell size in pixels (without pad).
        npad = n + 1
        self.pad = pad
        xsize = (width - npad*pad) / n
        ysize = (height - npad*pad) / n
        # Canvas dimensions for the cell grid and the palette.
        c_width, c_height = width, height
        p_pad = 5
        p_width = p_height = palette_height - 2*p_pad

        # The main frame onto which we draw the App's elements.
        frame = Frame(master)
        frame.pack()

        # The Debug window.

        debugframe = LabelFrame(master, text="Debug control")
        debugframe.pack( padx=pad, pady=pad)

        scroll_bar = Scrollbar(debugframe)
        scroll_bar.pack(side=RIGHT)


        self.debug=Text(debugframe,height =palette_height/13,width = int(c_width/8),yscrollcommand=scroll_bar.set)
        self.debug.pack()

        self.openNewWindow(master,c_width,palette_height,frame)
        

        self.ics = 9#0
        self.select_colour(self.ics)

        # The canvas onto which the grid is drawn.
        self.w = Canvas(master, width=c_width, height=c_height)
        self.w.pack()

        # Add the cell rectangles to the grid canvas.
        self.gridMap = Map(n,self.w) # self.gridMap = Map(50,self.w)

        # Add the robot
        self.robot = robotModel(True,self.gridMap.mapSize,self.gridMap,self)

        # Add MDP
        Mdp(n, self.robot, self.gridMap)
        #policy_object = PolicyModel(self.gridMap.mapSize**2,self.robot)
        
        mapframe = LabelFrame(frame, text="Map control")
        mapframe.pack(side=RIGHT, padx=pad, pady=pad)

        systemframe = LabelFrame(frame, text="System control")
        systemframe.pack(side=RIGHT, padx=pad, pady=pad)

        # Load, save image and ramdom map generator buttons
        b_load = Button(systemframe, text='open', command=self.gridMap.loadMap)
        b_load.pack(side=RIGHT, padx=pad, pady=pad)
        b_save = Button(systemframe, text='save', command= self.gridMap.saveMap)
        b_save.pack(side=RIGHT, padx=pad, pady=pad)
        b_random = Button(mapframe, text='random',command= lambda: self.gridMap.createRamdomMap(self.inputFeatures.get("1.0","end-1c")))
        b_random.pack(side=RIGHT, padx=pad, pady=pad)
        # Add a button to clear the grid
        b_clear = Button(mapframe, text='clear', command=self.gridMap.clearMap)
        b_clear.pack(side=RIGHT, padx=pad, pady=pad)

        #input buttom
        self.inputFeatures = Text(mapframe,height = 1.5,width = 5)
        self.inputFeatures.pack(side=RIGHT, padx=pad, pady=pad)

        #frame.bind("<Key>",self.key_pressed)

        labelframe = LabelFrame(frame, text="robot control")
        labelframe.pack(side=RIGHT, padx=pad, pady=pad)

        b_up = Button(labelframe, text='UP', command=self.robot.moveUpOne)
        b_up.pack(side=RIGHT, padx=pad, pady=pad)

        b_down = Button(labelframe, text='DOWN', command=self.robot.moveDownOne)
        b_down.pack(side=RIGHT, padx=pad, pady=pad)

        b_left = Button(labelframe, text='LEFT', command=self.robot.moveLeftOne)
        b_left.pack(side=RIGHT, padx=pad, pady=pad)

        b_right = Button(labelframe, text='RIGHT', command=self.robot.moveRightOne)
        b_right.pack(side=RIGHT, padx=pad, pady=pad)

        mdpFrame = LabelFrame(frame, text="MDP")
        mdpFrame.pack(side=RIGHT, padx=pad, pady=pad)

        self.inputPolicy = Text(mdpFrame,height = 1.5,width = 5)
        self.inputPolicy.pack(side=RIGHT, padx=pad, pady=pad)

        b_up = Button(mdpFrame, text='Generate policy', command=lambda: policy_object.generate_set_of_policies(self.inputPolicy.get("1.0","end-1c")))
        b_up.pack(side=RIGHT, padx=pad, pady=pad)

        #input buttom
        #debug_window = Text(frame,height = 1.5,width = 5)
        #debug_window.pack( side= BOTTOM, padx=pad, pady=pad)# , expand= True
        #debug_window.place(relx=0.8, rely=0.2, relwidth=0.5, anchor='nw')


        def palette_click_callback(event):
            """Function called when someone clicks on the palette canvas."""
            x, y = event.x, event.y

            # Did the user click a colour from the palette?
            if p_pad < y < p_height + p_pad:
                # Index of the selected palette rectangle (plus padding)
                ic = x // (p_width + p_pad)
                # x-position with respect to the palette rectangle left edge
                xp = x - ic*(p_width + p_pad) - p_pad
                # Is the index valid and the click within the rectangle?
                if ic < self.ncolours and 0 < xp < p_width:
                    self.select_colour(ic)
        # Bind the palette click callback function to the left mouse button

        # press event on the palette canvas.
        self.palette_canvas.bind('<ButtonPress-1>', palette_click_callback)

        def w_click_callback(event):
            """Function called when someone clicks on the grid canvas."""
            x, y = event.x, event.y

            # Did the user click a cell in the grid?
            # Indexes into the grid of cells (including padding)
            ix = int(x // (xsize + pad))
            iy = int(y // (ysize + pad))
            xc = x - ix*(xsize + pad) - pad
            yc = y - iy*(ysize + pad) - pad
            if ix < n and iy < n and 0 < xc < xsize and 0 < yc < ysize:
                i = iy*n+ix

                print("X pos: ",str(self.gridMap.map[i].pos_x))
                print("Z pos: ",str(self.gridMap.map[i].pos_z))

                # If cell is empty and colour palete is black, change cell state to not empty and color to black.
                if ((self.gridMap.map[i].empty == True) and (self.colours[self.ics]==Object_Colour.Wall.value)):#
                    self.gridMap.map[i].fill_cell(Object_Colour.Wall.name)

                # If cell is empty and colour palete is blue, change cell state to not empty and color to blue.
                if ((self.gridMap.map[i].empty == True) and (self.colours[self.ics]==Object_Colour.Water.value)):#
                    self.gridMap.map[i].fill_cell(Object_Colour.Water.name)

                # If cell is empty and colour palete is red, change cell state to not empty and color to blue.
                if ((self.gridMap.map[i].empty == True) and (self.colours[self.ics]==Object_Colour.Fire.value)):#
                    self.gridMap.map[i].fill_cell(Object_Colour.Fire.name)

                # If cell is not empty adn colour palete is white, change cell state to empty.
                if (self.gridMap.map[i].empty == False) and (self.colours[self.ics]==UNFILLED):
                    self.gridMap.map[i].empty_cell()
                    print(self.gridMap.map[i].empty)
                
                self.w.itemconfig(self.gridMap.map[i].tkinterCellIndex, fill=self.colours[self.ics])
        # Bind the grid click callback function to the left mouse button
        # press event on the grid canvas.
        self.w.bind('<ButtonPress-1>', w_click_callback)

    def select_colour(self, i):
        """Select the colour indexed at i in the colours list."""

        self.palette_canvas.itemconfig(self.palette_rects[self.ics],
                                       outline='black', width=1)
        self.ics = i
        self.palette_canvas.itemconfig(self.palette_rects[self.ics],
                                       outline='black', width=5)

    def openNewWindow(self, master, c_width, palette_height,frame):
        newWindow = Toplevel(master)
        newWindow.title("New Window")
        newWindow.geometry("400x50")
        p_pad = 5
        p_width = p_height = palette_height - 2*p_pad
        
        # The palette for selecting colours.
        self.palette_canvas = Canvas(newWindow, width=c_width, height=palette_height)
        self.palette_canvas.pack()

        # Add the colour selection rectangles to the palette canvas.
        self.palette_rects = []
        for i in range(self.ncolours):
            x, y = p_pad * (i+1) + i*p_width, p_pad
            rect = self.palette_canvas.create_rectangle(x, y,
                            x+p_width, y+p_height, fill=self.colours[i])
            self.palette_rects.append(rect)
        # ics is the index of the currently selected colour.

'''    
# Get the grid size from the command line, if provided
try:
    n = int(sys.argv[1])
except IndexError:
    n = DEFAULT_N
except ValueError:
    print('Usage: {} <n>\nwhere n is the grid size.'.format(sys.argv[0]))
    sys.exit(1)
if n < 1 or n > MAX_N:
    print('Minimum n is 1, Maximum n is {}'.format(MAX_N))
    sys.exit(1)

# Set the whole thing running
root = Tk()
grid = GridApp(root, n, 600, 600, 5)
root.mainloop()
'''