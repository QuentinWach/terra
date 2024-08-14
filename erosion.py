# Take in terrain and simulate water droplets randomly placed on the terrain, 
# walking down the gradient, and shifting the terrain as they go. 
# The water droplets should erode the terrain as they move, 
# and the terrain should settle over time. The terrain should be displayed as a 3D plot.

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
import time


def erosion(terrain, droplets=50000, erosion_rate=0.4, drop_steps=100, gravity=9.81, 
            inertia=0.9, min_slope=0.01, print_prog=False):
    height, width = terrain.shape
    erosion_lines = []  # Collect erosion lines for plotting

    for drop in tqdm(range(droplets)):
        if print_prog: print("Droplet", drop, "...")
        
        # Initialize droplet
        x, y = np.random.randint(1, height-1), np.random.randint(1, width-1)
        velocity_x, velocity_y = 0.0, 0.0
        drop_line = [[x], [y]]
        step_count = 0
        xs, ys = [], []
        
        while step_count < drop_steps:
            # Ensure the droplet is within bounds for a 3x3 neighborhood
            x_start, x_end = max(x-1, 0), min(x+2, height)
            y_start, y_end = max(y-1, 0), min(y+2, width)
            
            # Extract the 3x3 neighborhood
            neighborhood = terrain[x_start:x_end, y_start:y_end]
            
            # Calculate the gradient across the 3x3 neighborhood
            gx = (np.mean(neighborhood[1:, 1]) - np.mean(neighborhood[:-1, 1]))
            gy = (np.mean(neighborhood[1, 1:]) - np.mean(neighborhood[1, :-1]))
            
            # Update velocity based on gravity, slope, and inertia
            slope_x = gx * gravity
            slope_y = gy * gravity
            velocity_x = inertia * velocity_x - slope_x
            velocity_y = inertia * velocity_y - slope_y
            
            # Calculate new position with increased step size proportional to velocity
            dx = velocity_x
            dy = velocity_y
            
            # Check if the movement is too small (to avoid zero movement)
            directions = [[0,1],[1,0],[1,1], [0,-1],[-1,0],[-1,-1], [-1, 1], [1, -1]]
            if np.abs(dx) < min_slope and np.abs(dy) < min_slope:
                # Randomly perturb direction if movement is too small
                dx, dy = directions[np.random.randint(0, 8)][:]

            # Compute new position, allowing for larger movements
            new_x = x + dx
            new_y = y + dy
            
            # Ensure new position is within bounds
            if not (0 < new_x < height-1 and 0 < new_y < width-1): break
            
            # Convert to integer grid indices for terrain manipulation
            new_x_idx = int(new_x)
            new_y_idx = int(new_y)
            
            if new_x_idx in xs and new_y_idx in ys:
                #print("...stuck at", x, y, "with gradient", gx, gy)
                break
            
            #print("...dripping", step_count, "->", dx, dy, "from", x, y, "to", new_x_idx, new_y_idx)
            
            # Erode terrain over the 3x3 neighborhood
            if terrain[x, y] > terrain[new_x_idx, new_y_idx]:
                # Calculate the material eroded based on the distance travelled
                distance = np.sqrt((new_x - x)**2 + (new_y - y)**2)
                material = erosion_rate * 0.5 * distance
                
                # Apply erosion to the 3x3 neighborhood
                erosion_distribution = np.array([[0.1, 0.2, 0.1],
                                                 [0.2, 0.4, 0.2],
                                                 [0.1, 0.2, 0.1]]) * material
                
                # Apply the erosion distribution to the valid neighborhood area
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        xi, yj = x + i, y + j
                        if 0 <= xi < height and 0 <= yj < width:
                            terrain[xi, yj] -= erosion_distribution[i+1, j+1]
                            terrain[new_x_idx+i, new_y_idx+j] += erosion_distribution[i+1, j+1] / 2  # Deposit half of the material
            
            # Move droplet
            drop_line[0].append(new_x_idx)
            drop_line[1].append(new_y_idx)
            x, y = new_x_idx, new_y_idx
            xs.append(x)
            ys.append(y)
            
            step_count += 1
        
        erosion_lines.append(drop_line)
    
    return terrain, erosion_lines



def erosion_line_plot(erosion_lines):
    fig, ax = plt.subplots(figsize=(10, 10))
    for line in erosion_lines:
        ax.plot(line[1], line[0], color='blue', alpha=0.5)
    ax.set_aspect('equal')


if __name__ == '__main__':
    from base import *
    from perlin import *

    np.random.seed(69)
    shape = (1024//2, 1024//2)
    n_plates = 6 # 15  # number of plates

    # 1) Create tectonic plates with varying heights
    print("Creating tectonic plates...")
    vor, plate_heights = create_tectonic_plates(shape, n_plates)
    plot_voronoi_grid(vor, shape)

    # 2) Create terrain with mountains at plate boundaries
    print("Shaking things up...")
    #terrain = create_tectonic_mountains(vor, plate_heights, shape)
    #plot_terrain(terrain)

    # 3) Add perlin noise to the terrain
    #print("Roughing it all up...")
    #noise = generate_fractal_noise_2d(shape, (16, 16), octaves=4, persistence=0.5)
    #plot_terrain(0.1*noise)
    #terrain = terrain + 0.2*noise
    #plot_terrain(terrain)

    # 4) Erode the terrain
    #print("Splashing some water...")
    #terrain, erosion_lines = erosion(terrain)
    #plot_terrain(terrain)
    #erosion_line_plot(erosion_lines)

    # Show final 3D plot
    #plot3d_terrain(terrain)

