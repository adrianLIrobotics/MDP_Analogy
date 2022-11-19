# Importing packages
import random
import os
from object import objectModel;
from robot import robotModel;
 
# Printing the Minesweeper Layout
def print_grid():
 
    global visual_values
    global n
 
    print()
 
    st = "   "
    for i in range(n):
        if i==0:
            st = st + "     " + str(0 )
        elif i==1:
            st = st + "     " + str(1 )
        elif i==2:
            st = st + "     " + str(2 )
        elif i==3:
            st = st + "     " + str(3 )
        elif i==4:
            st = st + "     " + str(4 )
        elif i==5:
            st = st + "     " + str(5 )
        elif i==6:
            st = st + "     " + str(6 )
        elif i==7:
            st = st + "     " + str(7 )
        elif i==8:
            st = st + "     " + str(8 )
    print(st)   
 
    for r in range(n):
        st = "     "
        if r == 0:
            for col in range(n):
                st = st + "______" 
            print(st)
 
        st = "     "
        for col in range(n):
            st = st + "|     "
        print(st + "|")
         
        st = "  " + str(r ) + "  "
        for col in range(n):
            st = st + "|  " + str(visual_values[r][col]) + "  "
        print(st + "|") 
 
        st = "     "
        for col in range(n):
            st = st + "|_____"
        print(st + '|')
 
    print()  

# Function for setting up objects
def set_objects():
 
    global map
    global object_number
    global n
 
    # Track of number of objects already set up
    count = 0
    while count < object_number:
 
        # Random number from all possible grid positions 
        val = random.randint(0, n*n-1)
 
        # Generating row and column from the number
        r = val // n
        col = val % n
 
        # Place the object, if it doesn't already have one
        if map[r][col] != -1:
            count = count + 1
            map[r][col] = -1
 
# Function for setting up the other grid values
def set_values():
 
    global map
    global n
 
    # Loop for counting each cell value
    for r in range(n):
        for col in range(n):
 
            # Skip, if it contains a mine
            if map[r][col] == -1:
                continue
 
            # Check up  
            if r > 0 and map[r-1][col] == -1:
                map[r][col] = map[r][col] + 1
            # Check down    
            if r < n-1  and map[r+1][col] == -1:
                map[r][col] = map[r][col] + 1
            # Check left
            if col > 0 and map[r][col-1] == -1:
                map[r][col] = map[r][col] + 1
            # Check right
            if col < n-1 and map[r][col+1] == -1:
                map[r][col] = map[r][col] + 1
            # Check top-left    
            if r > 0 and col > 0 and map[r-1][col-1] == -1:
                map[r][col] = map[r][col] + 1
            # Check top-right
            if r > 0 and col < n-1 and map[r-1][col+1] == -1:
                map[r][col] = map[r][col] + 1
            # Check below-left  
            if r < n-1 and col > 0 and map[r+1][col-1] == -1:
                map[r][col] = map[r][col] + 1
            # Check below-right
            if r < n-1 and col < n-1 and map[r+1][col+1] == -1:
                map[r][col] = map[r][col] + 1
 
# Recursive function to display all zero-valued neighbours  
def neighbours(r, col):
     
    global visual_values
    global map
    global vis
 
    # If the cell already not visited
    if [r,col] not in vis:
 
        # Mark the cell visited
        vis.append([r,col])
 
        # If the cell is zero-valued
        if map[r][col] == 0:
 
            # Display it to the user
            visual_values[r][col] = map[r][col]
 
            # Recursive calls for the neighbouring cells
            if r > 0:
                neighbours(r-1, col)
            if r < n-1:
                neighbours(r+1, col)
            if col > 0:
                neighbours(r, col-1)
            if col < n-1:
                neighbours(r, col+1)    
            if r > 0 and col > 0:
                neighbours(r-1, col-1)
            if r > 0 and col < n-1:
                neighbours(r-1, col+1)
            if r < n-1 and col > 0:
                neighbours(r+1, col-1)
            if r < n-1 and col < n-1:
                neighbours(r+1, col+1)  
 
        # If the cell is not zero-valued            
        if map[r][col] != 0:
                visual_values[r][col] = map[r][col]
 
# Function for clearing the terminal
def clear():
    os.system("clear")      
 
 
# Function to check for completion of the game
def check_over():
    global visual_values
    global n
    global object_number
 
    # Count of all numbered values
    count = 0
 
    # Loop for checking each cell in the grid
    for r in range(n):
        for col in range(n):
 
            # If cell not empty or flagged
            if visual_values[r][col] != ' ' and visual_values[r][col] != 'F':
                count = count + 1
     
    # Count comparison          
    if count == n * n - object_number:
        return True
    else:
        return False
 
# Display all the object locations                    
def show_everything(wheeledRobotX,wheeledRobotZ):
    global visual_values
    global map
    global n
 
    visual_values[wheeledRobotX][wheeledRobotZ] = 'R'
    
    for r in range(n):
        for col in range(n):
            if map[r][col] == -1:
                visual_values[r][col] = 'O'

 
 
if __name__ == "__main__":
 
    # Size of grid
    n = 8
    # Number of objects
    object_number = 20
 
    # The actual values of the grid
    map = [[0 for y in range(n)] for x in range(n)] # each [] inside the big [] is a row
    # The apparent values of the grid
    visual_values = [[' ' for y in range(n)] for x in range(n)]
    # The positions that have been flagged
    flags = []
 
    # Set the mines
    set_objects()
 
    # Set the values
    set_values()
   
    # Create robot
    wheeledRobot = robotModel(False,n,map)
    localized = wheeledRobot.amcl(map)
    print(localized)
    print("wheeledRobot.pos_x row ",wheeledRobot.pos_xt)
    print("wheeledRobot.pos_zt column " ,wheeledRobot.pos_zt)
    print("Number of detected objects: ",wheeledRobot.detectedObjects)

    show_everything(wheeledRobot.pos_xt,wheeledRobot.pos_zt)
    print(map)
    print_grid()

