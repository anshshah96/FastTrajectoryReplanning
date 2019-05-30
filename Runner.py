import numpy as np
import matplotlib as plt
import pygame
from random import *
import heapq
import operator
import collections
i = 20
j = 20
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (i,j) #Sets position of window


BLACK = (0,0,0) #BLOCKED
WHITE = (255,255,255) #UNBLOCKED
GREEN = (0, 255, 0) #OPENTLIST
RED = (255, 0 , 0) #CLOSEDLIST
BLUE = (0, 0 , 255) #CURRENTPATH

#Dims of Cell and space between them
WIDTH = 7
HEIGHT = 7
MARGIN = 1

class Cell:
    def __init__(self, x ,y, visited, blocked):
        #Coordinates
        self.x = x
        self.y = y

        self.visited = visited
        self.blocked = blocked

        #Values for A*
        self.f = 0
        self.g = float("inf")
        self.h = 0

        #Neighbors of Cell
        self.neighbors = []

        #Parent of Cell
        self.tree = None


    def display(self):
        if(self.blocked):
            #blocked
            print("x", end = "")
        else:
            #unblocked
            print(" ", end = "")

    #Finds the neighbors of Cell
    def addNeighbors(self, grid, rows, cols):
        if(self.x < cols - 1):
            self.neighbors.append(grid[self.x + 1][ self.y])
        if(self.x > 0):
            self.neighbors.append(grid[self.x - 1][ self.y])
        if(self.y < rows - 1):
            self.neighbors.append(grid[self.x][ self.y + 1])
        if(self.y > 0):
            self.neighbors.append(grid[self.x][self.y - 1])

    #The compare function that the heap uses to transform a list into a heap
    def __lt__(self, other):
        if self.f == other.f:
            if self.h == other.h:
                return self.h > other.h
            else:
                return self.g > other.g
        else:
            return self.f < other.f

def heuristic(start, target):
    return abs(start.x - target.x) + abs(start.y - target.y)

#Creates the cell objects and puts it into the grid list
def genGrid(grid,rows, cols):
    blocked = False
    for x in range(rows):
        grid.append([])
    for x in range(rows):
        for y in range(cols):
            if ((x == 0 and y == 0)):
                grid[x].append(Cell(x, y, True, False))
            elif (x == rows - 1 and y == cols - 1):
                grid[x].append(Cell(x, y, False, False))
            else:
                blockProb = (int)(random() * 10)
                if (blockProb < 2):
                    blocked = True
                grid[x].append(Cell(x, y, False, blocked))
                blocked = False


def displayGrid(grid, rows, cols):
    for x in range(rows):
        for y in range(cols):
            grid[x][y].display()
        print()
def drawGrid(screen, rows, cols, grid):
    # This draws the grid initially
    screen.fill(BLACK)
    for row in range(rows):
        for column in range(cols):
            color = WHITE
            if grid[row][column].blocked:
                color = BLACK
            pygame.draw.rect(screen, color, [(MARGIN + WIDTH) * column + MARGIN,
                                             (MARGIN + HEIGHT) * row + MARGIN,
                                             WIDTH,
                                             HEIGHT])

    # updates display
    pygame.display.flip()


#Updated the color of a cell
def updateCell(color, row, column, screen):
    pygame.draw.rect(screen, color, [(MARGIN + WIDTH) * column + MARGIN,
                                     (MARGIN + HEIGHT) * row + MARGIN,
                                     WIDTH,
                                     HEIGHT])

#Finds the next best path
def aStar(openList, closedList, grid, start,  target, path, screen):
    #pop the cell with the least f value
    current = heapq.heappop(openList)

    if current == target:
        #Then done, add cells to solution path
        temp = current
        path.append(temp)
        while temp.tree is not None:
            path.append(temp.tree)
            temp = temp.tree
        return True

    #Add processed cell to the closedList
    closedList.append(current)

    #Neighbors of current cell
    neighbors = current.neighbors

    #Check whether the neighbor has been processed and update f,g values accordingly
    for n in neighbors:
        if n not in closedList and (not n.blocked):
            tempG = current.g + 1
            newPath = False
            if n not in openList:
                heapq.heappush(openList, n)
                updateCell(GREEN, n.x, n.y, screen)
                pygame.display.flip()
            elif tempG >= n.g:
                continue
            n.h = heuristic(n, target)
            n.g = tempG
            n.f = n.g + n.h
            n.tree = current
            heapq.heapify(openList)

    #update grid
    for c in openList:
        updateCell(GREEN, c.x, c.y,screen)
    currPath = []
    t = current
    currPath.append(t)
    while t.tree is not None:
        currPath.append(t.tree)
        t = t.tree
    for c in currPath:
        updateCell(BLUE, c.x, c.y, screen)
    for c in closedList:
        if c not in currPath:
            updateCell(RED, c.x, c.y, screen)
    pygame.display.flip()

def adaptiveAstar(openList, closedList, grid, start,  target, path, screen):
    backwards = False
    # Keep calling A* while there are cells to be processed
    while len(openList) > 0:
        if backwards:
            found = aStar(openList, closedList, grid, target, start, path, screen)
            # update h values in the closed list
            for c in closedList:
                c.h = target.g - c.g

        else:
            found = aStar(openList, closedList, grid, start, target, path, screen)
            # update h values in the closed list
            for c in closedList:
                c.h = target.g - c.g
        if found:
            print("found")
            break

    #run astar again


def main():
    #setting up grid with Cells
    grid = []
    rows = 101
    cols = 101
    genGrid(grid, rows, cols)
    backwards = False
    adapt = True

    #openList as a heap, closedList as a linked list
    closedList = collections.deque([])
    openList = []


    #starting position and target for A*
    start = grid[0][0]
    target = grid[rows - 1][cols - 1]


    path = [] #Holds the list cells that is part of the optimal path


    if backwards:
        target.g = 0
        target.f = target.h + target.g
        openList.append(target)
    else:
        start.g = 0
        start.f = start.g + start.h
        openList.append(start)
    heapq.heapify(openList)#turn the openList into a heap


    #Adds the neighbors of a cell into its neighbors field
    for x in range(rows):
        for y in range(cols):
            grid[x][y].addNeighbors(grid, rows, cols)

    #Setting up the display
    pygame.init()
    WINDOW_SIZE = [900, 900]
    screen = pygame.display.set_mode(WINDOW_SIZE)
    screen2 = pygame.display.set_mode(WINDOW_SIZE)
    done = False

    #draws the grid
    drawGrid(screen, rows, cols, grid)



    #Keep calling A* while there are cells to be processed
    while len(openList) > 0:
        if backwards:
            found = aStar(openList, closedList, grid, target, start, path, screen)
        else:
            found = aStar(openList, closedList, grid, start, target, path, screen)
        if found:
            print("found")
            break

    if adapt:
        # openList as a heap, closedList as a linked list
        closedList = collections.deque([])
        openList = []

        start.g = 0
        start.f = start.g + start.h
        openList.append(start)
        heapq.heapify(openList)  # turn the openList into a heap

        path = []
        drawGrid(screen2, rows, cols, grid)
        adaptiveAstar(openList, closedList, grid, start, target, path, screen2)
    if len(openList) == 0:
        print("no solution")


    #Keeps the window from closing
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

if __name__== "__main__":
    main()