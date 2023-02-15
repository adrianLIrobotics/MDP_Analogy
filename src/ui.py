import sys
from tkinter import *
from tkinter import filedialog
from object import objectModel
from colour import Object_Colour
from robot import robotModel
from map import Map
from policy import PolicyModel
from mdp import Mdp
from tkinter import ttk
from matplotlib import pyplot as plt
from threading import Thread
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from state import state_model
import utilities

# Thanks to:
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
        #print(event.char)
        pass

    def setNumberFeatures(self,event):
            featureNumber = self.inputFeatures.get(1.0, "end-1c")
            #print(featureNumber)

    def clearTextBox(self):
        self.debug.delete(1.0, END)

    def update_control_panel(self,num_object_detected, x_real_pose,oneD_pose_real , z_real_pose, oneD_pose_kf, x_pose_kf, z_pose_kf):
        self.z_real_pose.delete(1.0,END)
        self.robot_1d_real_pose.delete(1.0,END)
        self.z_real_pose.insert(END, str(x_real_pose))
        self.robot_1d_real_pose.insert(END, str(oneD_pose_real))
        self.num_observation_value.delete(1.0,END)
        self.num_observation_value.insert(END, str(num_object_detected))
        self.robot_real_pos_z_value.delete(1.0, END)
        self.robot_real_pos_z_value.insert(END, str(z_real_pose))
        self.kalman_1d_estimated_pose.delete(1.0, END)
        self.kalman_1d_estimated_pose.insert(END, str(oneD_pose_kf))
        self.x_pose_kf.delete(1.0, END)
        self.x_pose_kf.insert(END, str(x_pose_kf))
        self.z_pose_kf.delete(1.0, END)
        self.z_pose_kf.insert(END,z_pose_kf)

    '''
    Mathplot historical robot position
    '''
    def plot_robot_x_pose(self, robot):
        time = []
        count = 0
        for x in robot.pos_x:
            time.append(count)
            count +=1
        
        plt.plot(robot.pos_x, time)
        plt.title("Robot x pose historical data")

    '''
    Show all information about a selected cell.
    '''
    def show_cells_information(self, i):
        print("Border edge: ", self.gridMap.map[i].border_edge)
        self.writeTextBox("Border edge: "+str(self.gridMap.map[i].border_edge))
        print("first_column: ", self.gridMap.map[i].first_column)
        self.writeTextBox("first_column: "+str(self.gridMap.map[i].first_column))
        print("last_column: ", self.gridMap.map[i].last_column)
        self.writeTextBox("last_column: "+str(self.gridMap.map[i].last_column))
        print("First row: ", self.gridMap.map[i].first_row)
        self.writeTextBox("First row: "+str(self.gridMap.map[i].first_row))
        print("Last row: ", self.gridMap.map[i].last_row)
        self.writeTextBox("Last row: "+str(self.gridMap.map[i].last_row))
        print("pos_x ", self.gridMap.map[i].pos_x)
        self.writeTextBox("pos_x: "+str(self.gridMap.map[i].pos_x))
        print("pos_z ", self.gridMap.map[i].pos_z)
        self.writeTextBox("pos_z: "+str(self.gridMap.map[i].pos_z))
        print("1D Pose ", self.gridMap.map[i].tkinterCellIndex-1)
        self.writeTextBox("1D Pose: "+str(self.gridMap.map[i].tkinterCellIndex-1))
        print("colour", self.gridMap.map[i].colour)
        self.writeTextBox("colour: "+str(self.gridMap.map[i].colour))
        print("lighting_condition", self.gridMap.map[i].lighting_condition)
        self.writeTextBox("lighting_condition: "+str(self.gridMap.map[i].lighting_condition))
        print("Cell empty", self.gridMap.map[i].empty)
        self.writeTextBox("Cell empty: "+str(self.gridMap.map[i].empty))
        try:
            print("Object type", self.gridMap.map[i].object.objectType)
            self.writeTextBox("Object type: "+str(self.gridMap.map[i].object.objectType))
        except:
            pass
        #Show q values:
        #State(grid=grid, car_pos=[1, 1])
        print("Q-values for cell: ")
        state = state_model(self.grid.map, self.robot)
        r =self.markov_decision_process.learning.get_qvalues(state)
        print(f"up1={r[0]}, up2={r[1]}, donw1={r[2]}, down2={r[3]}, down2={r[3]}, moveLeft1={r[4]}, moveLeft2={r[5]}, moveRight1={r[6]}, moveRight2={r[7]}, stay={r[8]} ")
         

    '''
    Update robot reward value
    '''
    def updateRewardTextBox(self,text):
        self.t_reward.delete(1.0, END) # Clear old value
        self.t_reward.insert(END,str(text))

    '''
    Update the debug text window with inputed data.
    '''
    def writeTextBox(self,text):
        self.debug.insert(END,str(text)+"\n")

    def create_empty_figure(self):
        # Create empty matplot figure
        #self.fig, [self.ax, self.ax1] = plt.subplots(2, 1)
        fig = plt.figure()
        plt.show()

    def __init__(self, master, n, width=1000, height=1500, pad=5): # width=600, height=600
        """Initialize a grid and the Tk Frame on which it is rendered."""
        self.inspect = False
        
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

        # The canvas onto which the grid is drawn.
        self.w = Canvas(master, width=c_width, height=c_height)
        self.w.pack()

        # Add the cell rectangles to the grid canvas.
        self.gridMap = Map(n,self.w) # self.gridMap = Map(50,self.w)

        # Add the robot
        self.robot = robotModel(True,self.gridMap.mapSize,self.gridMap,self)

        # Add MDP
        self.markov_decision_process = Mdp(n, self.robot, self.gridMap)
        

        self.openPlotWindow(master, self.robot)

        self.openNewWindow(master,c_width,palette_height,frame,self.robot)

        self.ics = 9#0
        self.select_colour(self.ics)


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
                if self.inspect == False:
                    print("X pos: ",str(self.gridMap.map[i].pos_x))
                    print("Z pos: ",str(self.gridMap.map[i].pos_z))
                    print("1D pos: ", str(self.gridMap.map[i].tkinterCellIndex)) # 1

                    # If cell is empty and colour palete is black, change cell state to not empty and color to black.
                    if ((self.gridMap.map[i].empty == True) and (self.colours[self.ics]==Object_Colour.Wall.value)):#
                        self.gridMap.map[i].fill_cell(Object_Colour.Wall.name)

                    # If cell is empty and colour palete is blue, change cell state to not empty and color to blue.
                    if ((self.gridMap.map[i].empty == True) and (self.colours[self.ics]==Object_Colour.Water.value)):#
                        self.gridMap.map[i].fill_cell(Object_Colour.Water.name)

                    # If cell is empty and colour palete is red, change cell state to not empty and color to blue.
                    if ((self.gridMap.map[i].empty == True) and (self.colours[self.ics]==Object_Colour.Fire.value)):#
                        self.gridMap.map[i].fill_cell(Object_Colour.Fire.name)

                    # If cell is not empty and colour palete is white, change cell state to empty.
                    if (self.gridMap.map[i].empty == False) and (self.colours[self.ics]==UNFILLED):
                        self.gridMap.map[i].empty_cell()
                        #print(self.gridMap.map[i].empty)
                    
                    self.w.itemconfig(self.gridMap.map[i].tkinterCellIndex, fill=self.colours[self.ics])

                    print(self.gridMap.map[i].border)
                    print("Border edge: ", self.gridMap.map[i].border_edge)
                    print("first_column: ", self.gridMap.map[i].first_column)
                    print("last_column: ", self.gridMap.map[i].last_column)
                    print("First row: ", self.gridMap.map[i].first_row)
                    print("Last row: ",self.gridMap.map[i].last_row)

                if self.inspect == True:
                    self.show_cells_information(i)

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
        self.inspect = False

    def inspect_cell(self):
        print("Cell properties: ")
        if self.inspect == False:
            self.inspect = True

    '''Update graph window x plot'''
    def updateXPlot(self,x, x_noise_encoder, x_noise_camera, kalman_x_pose):
        try:
            self.plot1.clear()
            self.plot1.plot(x, color='g', label='real') #
            self.plot1.plot(x_noise_encoder, color='r', label='encoder') #
            self.plot1.plot(x_noise_camera, color='b', label='camera') #
            self.plot1.plot(kalman_x_pose, color='y', label='kalman') #
            
            #self.plot1.legend(['real', 'encoder noise', 'camera noise', 'kalman'])
            self.plot1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.8),
          fancybox=True, shadow=True, ncol=5)
            self.plot1.set_title("x-pose history")
            self.plot2.set_title("y-pose history")
            self.canvas.draw()
            
        except Exception as e:
            pass
            #print(e)

    '''Update graph window z plot'''
    def updateYPlot(self,y, Y_noise_encoder, Y_noise_camera, kalman_z_pose):
        try:
            self.plot2.clear()
            self.plot2.plot(y, color='g', label='real')
            self.plot2.plot(Y_noise_encoder, color='r', label='noise')
            self.plot2.plot(Y_noise_camera, color='b', label='noise')
            self.plot2.plot(kalman_z_pose, color='y', label='noise')
            #self.plot2.legend(['real', 'encoder noise', 'camera noise', 'kalman'])
            self.plot1.set_title("x-pose history")
            self.plot2.set_title("y-pose history")
            self.canvas.draw()
            
        except Exception as e:
            #print(e)
            pass

    '''Graphs window'''
    def openPlotWindow(self, master, robot):
        self.newPlotWindow = Toplevel(master)
        self.newPlotWindow.title("Plot window")
        self.newPlotWindow.geometry("500x500")#("500x500")
        self.fig = Figure(figsize = (5, 5), dpi = 100)
        #y = [i**2 for i in range(101)]
        #y = [1,2,3,4,5,6,7,20]
        x = []
        x_noise = []
        y = []
        Y_noise = []
        # adding the subplot
        self.plot1 = self.fig.add_subplot(311)#311
        self.plot2 = self.fig.add_subplot(313)#312
        # Add titles
        self.plot1.set_title("x-pose history")
        self.plot2.set_title("y-pose history")

        self.plot1.legend(['real', 'encoder noise'])
        self.plot2.legend(['real', 'encoder noise'])
        # plotting the graph
        self.plot1.plot(x)
        self.plot1.plot(x_noise)
        self.plot2.plot(y)
        self.plot2.plot(Y_noise)
        # creating the Tkinter canvas containing the Matplotlib figure
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.newPlotWindow)  
        self.canvas.draw()
        # placing the canvas on the Tkinter window
        self.canvas.get_tk_widget().pack()
        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.newPlotWindow)
        toolbar.update()
        # placing the toolbar on the Tkinter window
        self.canvas.get_tk_widget().pack()
  

    def openNewWindow(self, master, c_width, palette_height,frame,robot):
        newWindow = Toplevel(master)
        newWindow.title("Control Window")
        newWindow.geometry("460x500") # newWindow.geometry("400x50")  
        p_pad = 5
        pad = 5
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

        '''Robot control panel'''
        labelframe = LabelFrame(newWindow)
        labelframe.pack(side=TOP, padx=pad*2, pady=pad)

        labelframe2 = LabelFrame(labelframe, text="Robot-actions")
        labelframe2.pack(side=TOP, padx=pad*2, pady=pad)

        b_up = Button(labelframe2, text='UP', command = lambda: robot.moveUp(get_index()))
        b_up.pack(side=RIGHT, padx=pad, pady=pad)

        b_down = Button(labelframe2, text='DOWN', command = lambda: robot.moveDown(get_index()))
        b_down.pack(side=RIGHT, padx=pad, pady=pad)

        b_left = Button(labelframe2, text='LEFT', command = lambda: robot.moveLeft(get_index()))
        b_left.pack(side=RIGHT, padx=pad, pady=pad)

        b_right = Button(labelframe2, text='RIGHT', command = lambda: robot.moveRight(get_index()))
        b_right.pack(side=RIGHT, padx=pad, pady=pad)

        b_inspect = Button(labelframe2, text='INSPECT', command = self.inspect_cell)
        b_inspect.pack(side=RIGHT, padx=pad, pady=pad)

        b_reset = Button(labelframe2, text='RESET', command = robot.reset_simulation)
        b_reset.pack(side=RIGHT, padx=pad, pady=pad)

        def get_index(*arg):
            #print("combo: ", str(var.get()))
            return int(var.get())

        var = StringVar()
        combo = ttk.Combobox(labelframe2, textvariable=var)
        combo['state']="readonly",
        combo['values']=["1", "2"]
        combo.pack(side=RIGHT, padx=pad, pady=pad)
        combo.set('1') # Default number of steps per move is 1.
        var.trace('w', get_index)

        robot_info = LabelFrame(labelframe, text="Robot-real-state-info")
        robot_info.pack(side=TOP, padx=pad*2, pady=pad)

        oneDimensionPose = Label(robot_info, text='Real 1D Pose: ')
        oneDimensionPose.pack(side=LEFT, padx=pad, pady=pad)

        self.z_real_pose = Text(robot_info,height = 1.5,width = 5)
        self.z_real_pose.pack( side= RIGHT, padx=pad, pady=pad)

        self.robot_real_pos_x = Label(robot_info, text='Real Z pose: ')
        self.robot_real_pos_x.pack(side=RIGHT, padx=pad, pady=pad)

        self.robot_1d_real_pose = Text(robot_info,height = 1.5,width = 5)
        self.robot_1d_real_pose.pack( side= LEFT, padx=pad, pady=pad)

        self.robot_real_pos_z = Label(robot_info, text='Real X pose: ')
        self.robot_real_pos_z.pack(side=LEFT, padx=pad, pady=pad)

        self.robot_real_pos_z_value = Text(robot_info,height = 1.5,width = 5)
        self.robot_real_pos_z_value.pack( side= LEFT, padx=pad, pady=pad)

        robot_estimate_info = LabelFrame(labelframe, text="Robot-estimate-info")
        robot_estimate_info.pack(side=TOP, padx=pad*2, pady=pad)

        localization_label = Label(robot_estimate_info, text='Nº Observations: ')
        localization_label.pack(side=LEFT, padx=pad, pady=pad)

        self.localization_label_value = Text(robot_estimate_info,height = 1.5,width = 5)
        self.localization_label_value.pack( side= RIGHT, padx=pad, pady=pad)

        num_observation_label = Label(robot_estimate_info, text='Localization: ')
        num_observation_label.pack(side=RIGHT, padx=pad, pady=pad)

        self.num_observation_value = Text(robot_estimate_info,height = 1.5,width = 5)
        self.num_observation_value.pack( side= RIGHT, padx=pad, pady=pad)

        robot_estimate_localization = LabelFrame(labelframe, text="Robot-estimate-localization")
        robot_estimate_localization.pack(side=TOP, padx=pad*2, pady=pad)

        pose_oneD_label = Label(robot_estimate_localization, text='1D Pose: ')
        pose_oneD_label.pack(side=LEFT, padx=pad, pady=pad)

        self.z_pose_kf = Text(robot_estimate_localization,height = 1.5,width = 5)
        self.z_pose_kf.pack( side= RIGHT, padx=pad, pady=pad)

        z_pose_label = Label(robot_estimate_localization, text='Z Pose: ')
        z_pose_label.pack(side=RIGHT, padx=pad, pady=pad)

        self.x_pose_kf = Text(robot_estimate_localization,height = 1.5,width = 5)
        self.x_pose_kf.pack( side= RIGHT, padx=pad, pady=pad)

        x_pose_label = Label(robot_estimate_localization, text='X Pose: ')
        x_pose_label.pack(side=RIGHT, padx=pad, pady=pad)

        self.kalman_1d_estimated_pose = Text(robot_estimate_localization,height = 1.5,width = 5)
        self.kalman_1d_estimated_pose.pack( side= RIGHT, padx=pad, pady=pad)

        # MDP CONTROL
        mdp_map_frame = LabelFrame(labelframe, text="MDP & MAP")
        mdp_map_frame.pack(side=TOP, padx=pad*2, pady=pad)

        b_run = Button(mdp_map_frame, text='RUN', command=self.markov_decision_process.run_best_policy)
        b_run.pack(side=RIGHT, padx=pad, pady=pad)

        b_train = Button(mdp_map_frame, text='Train', command=self.markov_decision_process.train_model)
        b_train.pack(side=RIGHT, padx=pad, pady=pad)

        self.t_reward = Text(mdp_map_frame,height = 1.5,width = 5)
        self.t_reward.pack( side= RIGHT, padx=pad, pady=pad)# , expand= True

        b_random = Button(mdp_map_frame, text='random',command= lambda: self.gridMap.createRamdomMap(self.inputFeatures.get("1.0","end-1c")))
        b_random.pack(side=RIGHT, padx=pad, pady=pad)
        # Add a button to clear the grid
        b_clear = Button(mdp_map_frame, text='clear', command=self.gridMap.clearMap)
        b_clear.pack(side=RIGHT, padx=pad, pady=pad)

        # Input buttom
        self.inputFeatures = Text(mdp_map_frame,height = 1.5,width = 5)
        self.inputFeatures.pack(side=RIGHT, padx=pad, pady=pad)

        # Load, save image and ramdom map generator buttons
        b_load = Button(mdp_map_frame, text='open', command=self.gridMap.loadMap)
        b_load.pack(side=RIGHT, padx=pad, pady=pad)
        b_save = Button(mdp_map_frame, text='save', command= self.gridMap.saveMap)
        b_save.pack(side=RIGHT, padx=pad, pady=pad)

        # The Debug window.
        debugframe = LabelFrame(newWindow, text="Debug control")
        debugframe.pack( padx=pad, pady=pad)

        scroll_bar = Scrollbar(debugframe)
        scroll_bar.pack(side=RIGHT)

        #self.debug=Text(debugframe,height =palette_height/13,width = int(c_width/8),yscrollcommand=scroll_bar.set)
        self.debug=Text(debugframe,height =palette_height/10,width = int(c_width/8),yscrollcommand=scroll_bar.set)
        self.debug.pack()

        # Update control grid with initial conditions:
        self.update_control_panel(self.robot.num_objects_detected(), self.robot.pos_zt, self.robot.gridRobot1DPosition, self.robot.pos_xt, self.robot.pos_1d_kalman, self.robot.pos_xt_kalman, self.robot.pos_zt_kalman)