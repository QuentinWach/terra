import numpy as np
from rand import perlin
from render import export
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
    Add sparse erosion which only erodes certain areas (improving performance and creating more realistic erosion patterns).
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

# Create a Perlin noise heightmap
S = 42; X = 500; Y = 500
print("Creating perlin noise...")
hm = perlin(X, Y, scale=1000, octaves=1, seed=S)
perlin = hm*perlin(X, Y, scale=100, octaves=3, seed=S)
# Save the Perlin noise map
export(perlin, 'before.png', cmap='Greys_r', dpi=300)
# Erode the Perlin noise map by wetting it
eroded = wet(perlin, strength=5)
# Save the eroded map
export(eroded, 'after5.png', cmap='Greys_r', dpi=300)
# Save the difference
export(eroded - perlin, 'diff5.png', cmap='Greys_r', dpi=300)     