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
#
#######################################################################

import argparse
import random as rn
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as cl
import matplotlib.animation as animation

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
        for food in self.food:
            self.grid[food.x, food.y] = 1

        for ind in self.species:
            if self.grid[ind.x, ind.y] == 1:
                self.grid[ind.x, ind.y] = 3
            else:
                self.grid[ind.x, ind.y] = 2
    
    def show_food(self):
        print("Food")
        for food in self.food:
            print(f"[{food.x},{food.y}]")

    def show_species(self):
        print("Species")
        for ind in self.species:
            print(f"[{ind.x},{ind.y}]")
    
    def plot(self):
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
        plt.show()


class Microbe:

    energy = 15

    def __init__(self, x, y):
        self.x = x
        self.y = y

# Functions
def plot_grid():
    ...

def updates(grid, species, food):
    ...


def init(n, num_food, num_ind):
    global grid
    grid = Grid(n=n, num_food=num_food, num_ind=num_ind)
    grid.init_placements()
    grid.set_grid_values()
    grid.plot()

# Main Function
def main():

	# parse arguments
    parser = argparse.ArgumentParser(description="Simulating Evolution")

	# add arguments
    parser.add_argument('-N', '--grid-size', type=int, dest='N', help='One Side Length of the Square Grid', required=True)
    parser.add_argument('-num', '--num-of-species', type=int, dest='ind', help='Number of Initial Species', required=True)
    parser.add_argument('-food', '--num-of-food', type=int, dest='food', help='Number of Initial food', required=True)
    parser.add_argument('-gen','--interval', type=int, dest='interval',  help='Amount of Generations to Simulate For', required=True)
    args = parser.parse_args()

    init(args.N, args.food, args.ind)

# Call Main
if __name__ == '__main__':
	main()
