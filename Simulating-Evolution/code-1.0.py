import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
from math import dist

class Species:
    def __init__(
            self, 
            speed:int, 
            energy:int, 
            sense_area:int, 
            memory_input_size:int, 
            memory_hidden_units:int, 
            position:list[int, int], 
            ):
        self.speed = speed
        self.energy = energy
        self.sense_area = sense_area
        self.memory = self.initialize_memory(6, memory_hidden_units)
        # self.memory = self.initialize_memory(memory_input_size, memory_hidden_units)
        self.position = position
        self.alive = True

    def initialize_memory(self, input_size:int, hidden_units:int):
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Input(shape=(input_size,)))

        for units in hidden_units:
            model.add(tf.keras.layers.Dense(units, activation='relu'))

        model.add(tf.keras.layers.Dense(2, activation='linear'))  # Output layer

        return model

    def feed(self, food_energy:int):
        self.energy += food_energy

    def move(self, new_position:list[int,int]):
        self.energy -= self.speed
        self.position = new_position

    def sense_and_remember(self, sensory_input:list):
        # sensory input - current position, nearest predator position
        # sensory output - ideal position

        sensory_input = np.array(sensory_input)
        sensory_input = sensory_input.reshape((1, -1))

        # new_memory = self.memory(sensory_input)
        # self.memory.set_weights(new_memory.get_weights())

        return(self.memory.predict(sensory_input))

    def check_energy(self):
        if self.energy <= 0:
            self.alive = False

    def direction_mapping(self): # not currently implemented
        '''
        
        Description: Converts position of species into an integer representing the relative direction.
                    Zero represents current position of an individual. 
        
        Ex:
            1   2   3
            8   0   4
            7   6   5
        '''
        position = [x / abs(x) for x in self.position] # normalize [-1,1]
        match position:
            case [0,0]:
                return(0)
            case [-1,1]:
                return(1)
            case [0,1]:
                return(2)
            case [1,1]:
                return(3)
            case [1,0]:
                return(4)
            case [1,-1]:
                return(5)
            case [0,-1]:
                return(6)
            case [-1,-1]:
                return(7)
            case [-1,0]:
                return(8)
            case _:
                return(0)

    def normalize_position(self, position:list[int,int]):
        # min-max scaling
        return(np.divide(position, 5)) # map size        

class Predator(Species):
    def __init__(self, speed, energy, sense_area, memory_input_size, memory_hidden_units, position):
        super().__init__(speed, energy, sense_area, memory_input_size, memory_hidden_units, position)
        # add pred specification information here

class Prey(Species):
    def __init__(self, speed, energy, sense_area, memory_input_size, memory_hidden_units, position):
        super().__init__(speed, energy, sense_area, memory_input_size, memory_hidden_units, position)
        # add prey specification information here

    def get_consumed(self):
        self.alive = False

class Food:
    def __init__(self, energy:int, position:list[int,int]):
        self.energy = energy
        self.position = position

    def get_consumed(self):
        self.energy = 0
        self.new_position()

    def new_position(self):
        new_position = self.generate_new_position(map_size) # fix 
        self.position = new_position

    def generate_new_position(self, max:tuple):
        # not working? 
        return(np.random.rand(2) * np.array(max))

def distance(position1, position2): 
    return(np.linalg.norm(position1 - position2))

def pdf(array):
    # population density to serve as input to NN
    ...

def get_closest_position(array, pos:list[int,int]):
    # dictionary for position and distance
    pos_dist_dict = dict([(distance(p.position, pos), p.position) for p in array]) # only need if statement if same species (i.e. reproduction) 
    return(sorted(pos_dist_dict[0]))

def update(frame):
    # update position
    for p in prey + predators:
        if p.alive:
            new_position = p.position + (np.random.rand(2) - 0.5) * 2
            p.move(np.clip(new_position, [0, 0], map_size))
            p.check_energy()

    # update position of prey and predators
    for p in prey + predators:
        # predators_in_sense_area = [prey for pr in prey if (dist(p.position, pr.position) < p.sense_area)]
        norm_curr_position = p.normalize_position(p.position)
        
        pos_closest_food = get_closest_position(food_items, p.position)
        norm_pos_closest_food = p.normalize_position(pos_closest_food)

        if type(p) is Prey:
            pos_closest_pred = get_closest_position(predators, p.position)
            norm_pos_closest_pred = p.normalize_position(pos_closest_pred)
            new_position = p.sense_and_remember(norm_curr_position + norm_pos_closest_pred + norm_pos_closest_food) # doesnt output anything
        elif type(p) is Predator:
            pos_closest_prey = get_closest_position(prey, p.position)
            norm_pos_closest_prey = p.normalize_position(pos_closest_pred)
            new_position = p.sense_and_remember(norm_curr_position + norm_pos_closest_pred + norm_pos_closest_food) # doesnt output anything
        
        p.move(new_position)

        p.check_energy()

    # Check for consumed food
    for f in food_items:
        for p in prey:
            if p.alive:
                dist_f_p = distance(f.position, p.position)
                if dist_f_p <= p.sense_area:
                    p.feed(f.energy)
                    f.get_consumed()

    # Check for consumed prey
    for p in prey:
        for pred in predators:
            if pred.alive:
                dist_p_pred = distance(p.position, pred.position)
                if dist_p_pred <= pred.sense_area:
                    pred.feed(p.energy)
                    p.get_consumed()

    # Remove dead species
    prey[:] = [p for p in prey if p.alive]
    predators[:] = [p for p in predators if p.alive]

    # # Reproduction
    # for p in predators:
    #     for pred in [pred for pred in predators if pred != p]:
    #         if p.energy >= 10 and pred.energy >= 10:
    #             predators.append(Predator(5, 50, 10, 6, [12, 12], np.random.rand(2) * np.array(map_size)))

    # for p in prey:
    #     for p2 in [prey2 for prey2 in prey if prey2!= p]:
    #         if p.energy >= 5 and p2.energy >= 5:
    #             prey.append(Prey(2, 40, 8, 4, [8, 8], np.random.rand(2) * np.array(map_size)))

    scatter_predators.set_offsets(np.array([[p.position[0] for p in predators], [p.position[1] for p in predators]]).T)
    scatter_prey.set_offsets(np.array([[p.position[0] for p in prey], [p.position[1] for p in prey]]).T)
    scatter_food.set_offsets(np.array([[f.position[0] for f in food_items], [f.position[1] for f in food_items]]).T)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Predator-Prey Simulation")
    parser.add_argument("--num_predators", type=int, default=2, help="Number of predators")
    parser.add_argument("--num_prey", type=int, default=5, help="Number of prey")
    parser.add_argument("--num_food", type=int, default=3, help="Number of food items")
    parser.add_argument("--num_generations", type=int, default=100, help="Total number of updates")
    return parser.parse_args()

if __name__ == "__main__":
    # parse arguments
    args = parse_arguments()

    num_predators = args.num_predators
    num_prey = args.num_prey
    num_food = args.num_food
    generations = args.num_generations

    # add as argument?
    map_size = (5, 5)

    # initialize simulation variables (randomize)
    # def __init__(self, speed, energy, sense_area, memory_input_size, memory_hidden_units, position):
    predators = [Predator(5, 50, 2, 4, [12, 12], np.random.rand(2) * np.array(map_size)) for _ in range(num_predators)]
    prey = [Prey(2, 40, 8, 6, [8, 8], np.random.rand(2) * np.array(map_size)) for _ in range(num_prey)]
    food_items = [Food(20, np.random.rand(2) * np.array(map_size)) for _ in range(num_food)]

    # plotting
    fig, ax = plt.subplots()
    ax.set_xlim(0, map_size[0])
    ax.set_ylim(0, map_size[1])

    scatter_predators = ax.scatter([p.position[0] for p in predators], [p.position[1] for p in predators], color='red', marker='^', label='Predator')
    scatter_prey = ax.scatter([p.position[0] for p in prey], [p.position[1] for p in prey], color='blue', marker='o', label='Prey')
    scatter_food = ax.scatter([f.position[0] for f in food_items], [f.position[1] for f in food_items], color='green', marker='*', label='Food')

    ax.legend()

    ani = FuncAnimation(fig, update, frames=range(generations), repeat=False, interval=500)
    plt.show()

    # Next Steps: 
    # 1. Test and debug shit 
    # 2. Fix Reproduction of Predators and Prey
    # 3. 