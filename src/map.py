from tkinter import filedialog
from cell import Cell
from object import objectModel
import random
from colour import Object_Colour
from robot import robotModel
UNFILLED = '#fff'
colours = (UNFILLED, 'red', 'green', 'blue', 'cyan', 'orange', 'yellow',
               'magenta', 'brown', 'black')
width=600
height=600 
pad=5

class Map:
    
    def __init__(self,size,canvas):
        self.mapSize = size
        self.mapMaxSize = 50
        self.canvas = canvas
        self.map = []  
        self.ObjectsNumber = 5

        npad = self.mapSize + 1
        xsize = (width - npad*pad) / self.mapSize
        ysize = (height - npad*pad) / self.mapSize

        # Populate map with cells class objects which have tkinter rectangles.
        for iy in range(self.mapSize):
            for ix in range(self.mapSize):
                xpad, ypad = pad * (ix+1), pad * (iy+1) 
                x, y = xpad + ix*xsize, ypad + iy*ysize
                rect = self.canvas.create_rectangle(x, y, x+xsize,
                                           y+ysize, fill=UNFILLED)
                
                cell = Cell(ix,iy,True,rect)
                self.map.append(cell)#gridMap.map.append(rect)

    def createRamdomMap(self): # Of walls only
        """ Populate the grid map with obstacles in random cell positions """
        # Track of number of objects already set up
        count = 0
        while count < self.ObjectsNumber:

            # Random number from all possible grid positions 
            val = random.randint(0, self.mapSize*self.mapSize-1)

            # Place the object, if it doesn't already have one
            if self.map[val].empty == True:
                count = count + 1

                # Create an object of type Wall.
                wallObject = objectModel(self.map[val].pos_x,self.map[val].pos_z,Object_Colour.Wall.name)
                self.map[val].empty = False
                self.map[val].object = wallObject

                # Change the cell colour in the tkinter canvas
                self.canvas.itemconfig(self.map[val].tkinterCellIndex, fill=self.map[val].object.colour)

    def clearMap(self):
        """Reset the grid to the background "UNFILLED" colour."""

        for cell in self.map:
            if type(cell.object) == robotModel:
                pass
            if type(cell.object) == objectModel:
                self.canvas.itemconfig(cell.tkinterCellIndex, fill=UNFILLED)
                cell.empty = True
                cell.object= None

    def loadMap(self):
        """Load an image from a provided file."""

        def _coords_to_index(coords):
            """
            Translate from the provided coordinate (e.g. 'A1') to an index
            into the grid cells list.
            """

            ix = ord(coords[0])-65
            iy = self.mapSize - int(coords[1:])
            return iy*self.mapSize + ix

        self.filename = filedialog.askopenfilename(filetypes=(
                ('Grid files', '.grid'),
                ('Text files', '.txt'),
                ('All files', '*.*')))
        if not self.filename:
            return
        print('Loading file from', self.filename)
        self.clearMap()
        # Open the file and read the image, setting the cell colours as we go.
        with open(self.filename) as fi:
            for line in fi.readlines():
                line = line.strip()
                if line in colours:
                    this_colour = line
                    continue
                if not line or line.startswith('-'):
                    continue
                coords = line.split(',')
                if not coords:
                    continue
                for coord in coords:
                    i = _coords_to_index(coord.strip())
                    self.canvas.itemconfig(self.map[i].tkinterCellIndex, fill=this_colour)

                    # Attach object to the cell if it is not white
                    if this_colour == Object_Colour.Wall.value:
                        self.map[i].fill_cell(Object_Colour.Wall.name)

                    if this_colour == Object_Colour.Fire.value:
                        self.map[i].fill_cell(Object_Colour.Fire.name)

                    if this_colour == Object_Colour.Water.value:
                        self.map[i].fill_cell(Object_Colour.Water.name)


    def _get_cell_coords(self, i):
        """Get the <letter><number> coordinates of the cell indexed at i."""

        # The horizontal axis is labelled A, B, C, ... left-to-right;
        # the vertical axis is labelled 1, 2, 3, ... bottom-to-top.
        iy, ix = divmod(i, self.mapSize)
       
        return '{}{}'.format(chr(ix+65), self.mapSize-iy)

    def saveMap(self):
        """Output a list of cell coordinates, sorted by cell colour."""

        # When we save the list of coordinates with each colour it looks
        # better if we limit the number of coordinates on each line of output.
        MAX_COORDS_PER_ROW = 12

        def _get_coloured_cells_dict():
            """Return a dictionary of cell coordinates and their colours."""

            coloured_cell_cmds = {}
            for i, rect in enumerate(self.map):
                c = self.canvas.itemcget(rect.tkinterCellIndex, 'fill')
                
                if c == '#fff':
                    continue
                coloured_cell_cmds[self._get_cell_coords(i)] = c
            return coloured_cell_cmds

        def _output_coords(coords):
            """Sort the coords into column (by letter) and row (by int)."""

            coords.sort(key=lambda e: (e[0], int(e[1:])))
            nrows = len(coords) // MAX_COORDS_PER_ROW + 1
            for i in range(nrows):
                print(', '.join(
                      coords[i*MAX_COORDS_PER_ROW:(i+1)*MAX_COORDS_PER_ROW]),
                      file=fo)

        # Create a dictionary of colours (the keys) and a list of cell
        # coordinates with that colour (the value).
        coloured_cell_cmds = _get_coloured_cells_dict()
        cell_colours = {}
        for k, v in coloured_cell_cmds.items():
            cell_colours.setdefault(v, []).append(k)

        # Get a filename from the user and open a file with that name.
        with filedialog.asksaveasfile(mode='w',defaultextension=".grid") as fo:
            if not fo:
                return

            self.filename = fo.name
            print('Writing file to', fo.name)
            for colour, coords in cell_colours.items():
                print('{}\n{}'.format(colour,'-'*len(colour)), file=fo)
                _output_coords(coords)
                print('\n', file=fo)