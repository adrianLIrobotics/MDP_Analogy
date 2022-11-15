# https://www.askpython.com/python/examples/create-minesweeper-using-python

# Printing the Minesweeper Layout
def print_mines_layout(n):
          
    # The actual values of the grid
    numbers = [[0 for y in range(n)] for x in range(n)] 
    print(numbers)
    # The apparent values of the grid
    mine_values = [[' ' for y in range(n)] for x in range(n)]
    # The positions that have been flagged
    flags = [] 

    print()

    #Guia indice superior
    st = "   "
    for i in range(n):
        st = st + "     " + str(i + 1)
    print(st)   
 
    #Dibujado de la matriz
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
         
        st = "  " + str(r + 1) + "  "
        for col in range(n):
            st = st + "|  " + str(mine_values[r][col]) + "  "
        print(st + "|") 
 
        st = "     "
        for col in range(n):
            st = st + "|_____"
        print(st + '|')
 
    print()

        
# Size of grid
sizeGrid = 8

print_mines_layout(sizeGrid)  
