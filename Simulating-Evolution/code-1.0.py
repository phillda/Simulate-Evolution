#######################################################################
# 
# Developer: Dallas Phillips
# Project: Simulating Evolution
# Version: 1.0
# Description:
#       This program is designed to simulate evolution with variability
# based on the natural occurance of life throughout the history of the
# universe. 
#
# References: 
#       1) https://www.geeksforgeeks.org/conways-game-life-python-implementation/
#       2) https://matplotlib.org/3.5.0/api/_as_gen/matplotlib.animation.FuncAnimation.html
#       3) https://beltoforion.de/en/simulated_evolution/
#       4) http://ccl.northwestern.edu/rp/beagle/index.shtml#:~:text=Simulated%20Evolution%20is%20the%20umbrella,and%20learn%20about%20evolutionary%20processes.
#       5) Look into PyGame 
#
#######################################################################

import argparse
import glob
# import matplotlib.animation as animation
import matplotlib.colors as cl
import matplotlib.pyplot as plt
import numpy as np
import os
import random as rn

from PIL import Image


# Global Variables
matr = [[-1,0],
        [1, 0],
        [0,-1],
        [0,1],
        [0,0],
        [-1,-1],
        [-1,1],
        [1,-1],
        [1,1]]

# Classes 
class Food:

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Microbe:

    energy = 15

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Grid:

    def __init__(self, n, num_food, num_ind):
        self.n = n
        self.grid = np.zeros(n*n).reshape(n, n)
        self.num_food = num_food
        self.num_ind = num_ind

    def init_placements(self):
        xys = rn.sample(range(self.n * self.n), self.num_ind)
        xys2 = rn.sample(range(self.n * self.n), self.num_food)
        points = [list(divmod(xy, self.n)) for xy in xys]           # Generate Random Points in Grid
        points2 = [list(divmod(xy, self.n)) for xy in xys2]         # Generate Random Points in Grid
        species = [Microbe(x, y) for x, y in points]                # Assign generated points to Species Class
        food = [Food(x, y) for x, y in points2]                     # Assign generated points to Food Class
        self.food = food
        self.species = species

    def set_grid_values(self):
        # Set grid values based on what is in each location 
        self.grid = np.zeros(self.n*self.n).reshape(self.n, self.n) 
        
        # Place food
        for food in self.food:
            if food.x != -1 and food.y != -1:
                self.grid[food.x, food.y] = 1

        # Place species
        for ind in self.species:
            if ind.x != -1 and ind.y != -1: 
                if self.grid[ind.x, ind.y] == 1:
                    self.grid[ind.x, ind.y] = 3
                else:
                    self.grid[ind.x, ind.y] = 2

    def delete_food(self, ind):
        # This function deletes food that has been consumed. 
        if self.grid[ind.x, ind.y] == 3:
            for food in self.food:
                if [food.x, food.y] == [ind.x, ind.y]:
                    food.x, food.y = [-1, -1]

    def update_food(self):
        # Places new food that has been consumed 
        for food in self.food:
            if [food.x, food.y] == [-1, -1]:
                temp = rn.sample(range(self.n * self.n), 1) # rn.sample returns a list, so only take the first element
                new_x, new_y = divmod(temp[0], self.n)
                while(self.grid[new_x, new_y] == 1 or self.grid[new_x, new_y] == 3):
                    temp = rn.sample(range(self.n * self.n), 1) # rn.sample returns a list, so only take the first element
                    new_x, new_y = divmod(temp[0], self.n)
                food.x, food.y = new_x, new_y

    def update_species(self):
        for ind in self.species:
            self.delete_food(ind)
            if ind.energy != 0:
                # Species moves every generation
                new_x, new_y = matr[rn.randint(0, len(matr)-1)]
                
                # Edge of Grid Conditions
                if ((ind.x + new_x) == self.n) or ((ind.x + new_x) < 0):
                    if (ind.x + new_x) == self.n:
                        ind.x = 0
                    elif (ind.x + new_x) < 0: 
                        ind.x = self.n - 1 
                        
                elif ((ind.y + new_y) == self.n) or ((ind.y + new_y) < 0):
                    if (ind.y + new_y) == self.n:
                        ind.y = 0
                    elif (ind.y + new_y) < 0: 
                        ind.y = self.n - 1 

                else: 
                    # Make a random legal move in the grid
                    ind.x, ind.y = [ind.x + new_x, ind.y + new_y]

                # Movement consumes species energy
                if new_y == 0 and new_x == 0:
                    pass
                else: 
                    ind.energy-=1
            
            else:
                ind.x, ind.y = [-1, -1]
            
    
    def show_food(self):
        print("Food")
        for food in self.food:
            print(f"[{food.x},{food.y}]")

    def show_species(self):
        print("Species")
        for ind in self.species:
            print(f"[{ind.x},{ind.y}]")
    
    def plot(self, i):
        fig, ax = plt.subplots()
        img = ax.imshow(self.grid, cmap=cl.ListedColormap(colors=['white', 'red', 'blue', 'purple']), vmin=0, vmax=3)        # 0 - black, 1 - red, 2 - blue, 3 - purple

        # Major ticks
        ax.set_xticks(np.arange(0, self.n, 1))
        ax.set_yticks(np.arange(0, self.n, 1))

        # Labels for major ticks
        ax.set_xticklabels("")
        ax.set_yticklabels("")

        # Minor ticks
        ax.set_xticks(np.arange(-.5, self.n, 1), minor=True)
        ax.set_yticks(np.arange(-.5, self.n, 1), minor=True)

        # Gridlines based on minor ticks
        ax.grid(which='minor', color='k', linestyle='-', linewidth=2)
        background = fig.canvas.copy_from_bbox(ax.bbox)
        
        # Save and close figure
        fig.savefig(f"./images/gen-{i}.png")
        plt.close('all')

    def create_gif(self):
        # Maybe need to resize images with pillow
        frames = [Image.open(image) for image in glob.glob(f"./images/*.png")]
        frame_one = frames[0]
        frame_one.save("evolution.gif", format="GIF", append_images=frames, 
                save_all=True, duration=1000, loop=0)


# Main Function
def main():

	# parse arguments
    parser = argparse.ArgumentParser(description="Simulating Evolution")

	# add arguments
    parser.add_argument('-N', '--grid-size', type=int, dest='N', 
                help='One Side Length of the Square Grid', default=5, required=False)
    parser.add_argument('-num', '--num-of-species', type=int, dest='ind', 
                help='Number of Initial Species', default=1, required=False)
    parser.add_argument('-food', '--num-of-food', type=int, dest='food', 
                help='Number of Initial food', default=5, required=False)
    parser.add_argument('-gen','--interval', type=int, dest='interval',  
                help='Amount of Generations to Simulate For', default=50, required=False)
    args = parser.parse_args()

    print("Initializing Placements...")
    grid = Grid(n=args.N, num_food=args.food, num_ind=args.ind)
    grid.init_placements()
    grid.set_grid_values()
    
    print("Simulating Evolution...")
    for i in range(args.interval):
        grid.update_food()
        grid.update_species()
        grid.set_grid_values()
        grid.plot(i)

    print("Outputting GIF...")
    grid.create_gif()
    # delete_ims()
        
def delete_ims():
    ims = glob.glob('./images/*.png')
    for i in ims:
        os.remove(i)

# Call Main
if __name__ == '__main__':
	main()

# Next Steps
# 1) Not giving energy when species consumes it
# 2) Placing of food takes an extra cycle, possible check for 
#       each grid location rather than each food

# Some ideas... 
# 1) Synch vs Asynch updates 
# 2) 
