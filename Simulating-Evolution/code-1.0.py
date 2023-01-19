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

def sort_func(x, y):
    return(np.sqrt(np.square(y) - np.square(x)))

# Classes 
class Food:

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Species:

    energy = 30

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Grid:

    def __init__(self, n, num_food, num_ind, sync):
        self.n = n
        self.grid = np.zeros(n*n).reshape(n, n)
        self.num_food = num_food
        self.num_ind = num_ind
        self.sync = sync

    def init_placements(self):
        self.plant_trees()
        points = self.random_coords(self.num_ind)           # Generate Random Points in Grid
        points2 = self.random_coords(self.num_food)         # Generate Random Points in Grid
        species = [Species(x, y) for x, y in points]        # Assign generated points to Species Class
        food = [Food(x, y) for x, y in points2]             # Assign generated points to Food Class
        self.food = food
        self.species = species
        self.check_for_bad_placement()

    def set_grid_values(self):
        # Set grid values based on what is in each location 
        self.grid = np.zeros(self.n*self.n).reshape(self.n, self.n) 
        for x,y in self.trees:
            self.grid[x,y] = 4
            self.grid[x+1,y] = 4
            self.grid[x,y+1] = 4
            self.grid[x+1,y+1] = 4

        # Place food
        for food in self.food:
            if food.x != -1 and food.y != -1:
                self.grid[food.x, food.y] = 1

        # Place species
        for ind in self.species:
            if ind.x != -1 and ind.y != -1:  # species not dead 
                if self.grid[ind.x, ind.y] == 1:
                    self.grid[ind.x, ind.y] = 3
                else:
                    self.grid[ind.x, ind.y] = 2
            else: 
                self.grid[ind.x, ind.y] = 1

    def tree_overlap_check(self, border_pts):
        for pts in border_pts:
            if pts in self.trees:
                return True
            else:
                return False

    def overlap_check(self, x, y):
        if [x,y] in self.trees:
            return True
        elif [x-1,y] in self.trees:
            return True
        elif [x,y-1] in self.trees:
            return True
        elif [x-1,y-1] in self.trees:
            return True
        else:
            return False

    def check_for_bad_placement(self):
        for food in self.food:
            while(self.overlap_check(food.x, food.y)):
                [food.x, food.y] = self.random_coords(1)

        for ind in self.species:
            while(self.overlap_check(ind.x, ind.y)):
                [ind.x, ind.y] = self.random_coords(1)

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
                new_x, new_y = self.random_coords(1)
                while(self.grid[new_x, new_y] == 1 or self.grid[new_x, new_y] == 3):
                    new_x, new_y = self.random_coords(1)
                food.x, food.y = new_x, new_y

    def update_species(self):
        for ind in self.species:
            # delete and replace "eaten" food
            self.delete_food(ind)

            if ind.energy != 0:
                # Species moves every generation
                new_x, new_y = matr[rn.randint(0, len(matr)-1)]
                
                # Edge of Grid Conditions
                if ((ind.x + new_x) == self.n) or ((ind.x + new_x) < 0) or ((ind.y + new_y) == self.n) or ((ind.y + new_y) < 0):
                    # if cur x pos + new x is "off the grid", adjust to other side
                    if (ind.x + new_x) == self.n:
                        ind.x = 0
                    elif (ind.x + new_x) < 0: 
                        ind.x = self.n - 1 
                    
                    # if cur y pos + new y is "off the grid", adjust to other side
                    if (ind.y + new_y) == self.n:
                        ind.y = 0
                    elif (ind.y + new_y) < 0: 
                        ind.y = self.n - 1 
                else: 
                    # Make a random legal move in the grid
                    ind.x, ind.y = [ind.x + new_x, ind.y + new_y]

                # Check for food at updated location (give energy)
                for food in self.food:
                    if [ind.x, ind.y] == [food.x, food.y]:
                        ind.energy += 5

                # Movement consumes species energy
                if new_y == 0 and new_x == 0:
                    pass
                else: 
                    ind.energy-=1
            
            # Run out of energy, species dies
            else:
                ind.x, ind.y = [-1, -1]

            if not self.sync:
                self.update_food()

    def plant_trees(self):
        points = self.random_coords(round(round(0.2*self.n**2)/4))
        self.trees = sorted(points)
        ls = [*matr[0:4], *matr[5:8]] # Matr Values without [0,0] - Avoid overlaps with self
        for i, [x,y] in enumerate(self.trees):
            # Check the border of each tree for another to detect overlaps
            border_pts = [[x+mat_x, y+mat_y] for mat_x, mat_y in ls] # Calc border pts
            while ((x==self.n-1) or (y==self.n-1) or self.tree_overlap_check(border_pts)): # Tree on edge or has border overlap
                x,y = self.random_coords(1)
                self.trees[i] = [x,y]
                border_pts = [[x+mat_x, y+mat_y] for mat_x, mat_y in ls] # Calc new border pts


    def random_coords(self, n):
        temp = rn.sample(range(self.n * self.n), n) # rn.sample returns a list, so only take the first element
        if n == 1:
            x, y = divmod(temp[0], self.n)
            return(x, y)
        else:
            points = [list(divmod(xy, self.n)) for xy in temp]  
            return(points)

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
        img = ax.imshow(self.grid, cmap=cl.ListedColormap(colors=['black', 'red', 'blue', 'purple', 'green']), vmin=0, vmax=4)

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
        fig.savefig(f"../images/gen-{i}.png")
        plt.close('all')

    def create_gif(self):
        # Maybe need to resize images with pillow
        frames = [Image.open(image) for image in glob.glob(f"../images/*.png")]
        frame_one = frames[0]
        frame_one.save("evolution.gif", format="GIF", append_images=frames, 
                save_all=True, duration=1000, loop=0)
        delete_ims()

    def delete_ims():
        files = glob.glob('../images/*.png', recursive=True)

        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                print("Error: %s : %s" % (f, e.strerror))

# Main Function
def main():

	# parse arguments
    parser = argparse.ArgumentParser(description="Simulating Evolution")

	# add arguments
    # Grid
    parser.add_argument('-N', '--grid-size', type=int, dest='N', 
                help='One Side Length of the Square Grid', default=50, required=False)
    # Species
    parser.add_argument('-num', '--num-of-species', type=int, dest='ind', 
                help='Number of Initial Species', default=30, required=False)
    # Food
    parser.add_argument('-food', '--num-of-food', type=int, dest='food', 
                help='Number of Initial food', default=20, required=False)
    # Generations
    parser.add_argument('-gen','--interval', type=int, dest='interval',  
                help='Amount of Generations to Simulate For', default=100, required=False)
    # Sync/Async
    parser.add_argument('-sync', type=bool, dest='sync',  
                help='Synchronous or Asynchronous Updates', default=0, required=False)

    args = parser.parse_args()

    print("Initializing Placements...")
    grid = Grid(n=args.N, num_food=args.food, num_ind=args.ind, sync=args.sync)
    grid.init_placements()
    grid.set_grid_values()
    
    print(f"Simulating {args.interval} Generations...")
    for i in range(args.interval):
        if grid.sync: 
            grid.update_food()
        grid.update_species()
        grid.check_for_bad_placement()
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
# 1) Random Species Location Jumping???
# 2) Add Species Attributes that help/hinder

# Some ideas... 
# 1) 
# 2) Make species into NN
# 3)  
