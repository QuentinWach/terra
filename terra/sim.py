import numpy as np
from rand import perlin
from render import export, calculate_normal_map, terrain_cmap
from tqdm import tqdm

def wet(heightmap, strength=50, spread=True):
    """
    Creates an more smooth, yet detailed erosion effect.
    It erodes all local pixel instead of moving sediment via droplets across large distances.

    Args:
    heightmap: numpy array - the heightmap to erode
    strength: int - the number of steps to simulate
    spread: bool - whether to erode all surrounding lower pixels at once or only the lowest one

    Todo:
    - Add sparse erosion which only erodes certain areas (improving performance and creating more realistic erosion patterns).
    - Speed of the technique could be improved by using a GPU as it is highly parallelizable.
    """
    print("Starting erosion simulation...")
    erosion_strength = 1
    if spread: erosion_strength = erosion_strength / 4
    eroded = np.copy(heightmap)
    for step in tqdm(range(strength)):
        for i in range(len(eroded[0])):
            for j in range(len(eroded[1])):
                if spread: 
                    # Erode all surrounding lower pixels 
                    for k in range(-1, 1):
                        for l in range(-1, 1):
                            if eroded[i+k][j+l] < eroded[i][j]:
                                # Calculate the slope between the current pixel and the smallest neighbour
                                slope = (eroded[i][j] - eroded[i+k][j+l])
                                # Take away mass from the current pixel
                                eroded[i][j] -= abs(erosion_strength*slope)
                                # Add mass to the smallest neighbour
                                eroded[i+k][j+l] += abs(erosion_strength*slope)
                else:
                    # If there is a neighbour that is lower than the current pixel...
                    smallest_neighbour = eroded[i][j]
                    smallest_neighbour_coords = (i, j)
                    for k in range(-1, 1):
                        for l in range(-1, 1):
                            if eroded[i+k][j+l] < smallest_neighbour:
                                smallest_neighbour = eroded[i+k][j+l]
                                smallest_neighbour_coords = (i+k, j+l)
                    if smallest_neighbour < eroded[i][j]:
                        # Calculate the slope between the current pixel and the smallest neighbour
                        slope = (eroded[i][j] - smallest_neighbour)
                        # Take away mass from the current pixel
                        eroded[i][j] -= abs(erosion_strength*slope)
                        # Add mass to the smallest neighbour
                        eroded[smallest_neighbour_coords[0]][smallest_neighbour_coords[1]] += abs(erosion_strength*slope)
    return eroded    

def pointify(height_map, strength=0.5, get_gradient=False):
    # Calculate gradients
    dy, dx = np.gradient(height_map)
    # Calculate gradient magnitude
    gradient_magnitude = np.sqrt(dx**2 + dy**2)
    # Normalize gradient magnitude
    gradient_magnitude = gradient_magnitude / np.max(gradient_magnitude)
    # Apply exponential function to gradient magnitude
    terrain =  height_map * np.exp(-(strength*gradient_magnitude)**2)
    # Return the terrain and gradient magnitude if requested
    if get_gradient: return terrain, gradient_magnitude
    return terrain

def pointy_perlin(X, Y, scale, octaves=4, persistence=0.35, lacunarity=2.5, pointiness=0.5, pointilarity=0.5, seed=42):
    terrain = np.zeros((Y, X))
    p = 1
    scale = scale
    pointiness = pointiness
    for i in range(octaves):
        terrain += p*pointify(perlin(X=X, Y=Y, scale=scale, lacunarity=lacunarity, octaves=1, seed=seed+i), strength=pointiness)
        p *= persistence
        scale /= lacunarity
        pointiness += pointilarity
    return terrain

def radial_mask(X, Y, max_value=255):
    # Create coordinate grids
    x = np.linspace(-1, 1, X)
    y = np.linspace(-1, 1, Y)
    x_grid, y_grid = np.meshgrid(x, y)
    # Calculate the distance from the center for each pixel
    distance = np.sqrt(x_grid**2 + y_grid**2)
    # Normalize the distance so that the center is 0 and edges approach 1
    distance = np.clip(distance, 0, 1)
    # Invert and scale the distance to get the height values
    heightmap = (1 - distance)**2 * max_value
    return heightmap

def hill(X, Y, seed=42):
    return radial_mask(X,Y)*pointy_perlin(X=X, Y=Y, octaves=4, scale=np.sqrt(X*Y)*0.85, pointiness=0.7, pointilarity=0.2, seed=seed)



terrain = hill(500, 500) # create the island heightmap
normal_map = calculate_normal_map(terrain) # calculate the normals
export(terrain, "hill.png", cmap="Greys_r")
export(terrain, "hill_coloured.png", cmap=terrain_cmap())
export(normal_map, "hill_normal.png", cmap="viridis")
