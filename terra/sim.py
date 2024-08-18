import numpy as np
from terra.randd import perlin
from scipy.ndimage import convolve
from tqdm import tqdm

# TODO: Replace or delete! Currently simply smoothing out in a very inefficient way...
"""
def wet(heightmap, strength=50, spread=True):
    '''
    Creates an more smooth, yet detailed erosion effect.
    It erodes all local pixel instead of moving sediment via droplets across 
    large distances.

    Args:
    heightmap: numpy array - the heightmap to erode
    strength: int - the number of steps to simulate
    spread: bool - whether to erode all surrounding lower pixels at once or only
      the lowest one

    Todo:
    - Add sparse erosion which only erodes certain areas (improving performance 
      and creating more realistic erosion patterns).
    - Speed of the technique could be improved by using a GPU as it is 
      highly parallelizable.
    '''
    print("Starting erosion simulation...")
    erosion_strength = 1
    if spread: erosion_strength = erosion_strength / 4
    eroded = np.copy(heightmap)
    for step in tqdm(range(strength)):
        for i in range(1, len(eroded[0])-1):
            for j in range(1, len(eroded[1])-1):
                if spread: 
                    # Erode all surrounding lower pixels 
                    for k in range(-1, 2):
                        for l in range(-1, 2):
                            if eroded[i+k][j+l] < eroded[i][j]:
                                # Calculate the slope between the current pixel 
                                # and the smallest neighbour
                                slope = (eroded[i][j] - eroded[i+k][j+l])
                                # Take away mass from the current pixel
                                eroded[i][j] -= abs(erosion_strength*slope)
                                # Add mass to the smallest neighbour
                                eroded[i+k][j+l] += abs(erosion_strength*slope)
                else:
                    # If there is a neighbour that is lower than the current pixel...
                    smallest_neighbour = eroded[i][j]
                    smallest_neighbour_coords = (i, j)
                    for k in range(-1, 2):
                        for l in range(-1, 2):
                            if eroded[i+k][j+l] < smallest_neighbour:
                                smallest_neighbour = eroded[i+k][j+l]
                                smallest_neighbour_coords = (i+k, j+l)
                    if smallest_neighbour < eroded[i][j]:
                        # Calculate the slope between the current pixel
                        # and the smallest neighbour
                        slope = (eroded[i][j] - smallest_neighbour)
                        # Take away mass from the current pixel
                        eroded[i][j] -= abs(erosion_strength*slope)
                        # Add mass to the smallest neighbour
                        eroded[smallest_neighbour_coords[0]][smallest_neighbour_coords[1]] += abs(erosion_strength*slope)
    return eroded    
"""

def emboss(heightmap, strength=1.0):
    """
    Apply a Gaussian blur to a height map.
    """
     # Define a sharpening kernel
    kernel = np.array([[-2, -1,  0],
                    [-1,  1,  1],
                    [ 0,  1,  2]])
    # Apply the sharpening filter to the heightmap
    hm = convolve(heightmap, kernel)
    # Adjust the sharpening effect by mixing the original and sharpened maps
    hm = heightmap + strength * (hm - heightmap)
    # Clip the values to ensure they remain in a valid range
    hm = np.clip(hm, 0, 1)
    return hm

def sharpen(heightmap, strength=1.0):
    """
    Sharpens the heightmap to create a more stone-like appearance.

    Args:
    heightmap: numpy array - the heightmap to sharpen
    strength: float - the amount of sharpening to apply

    Returns:
    numpy array - the sharpened heightmap
    """
    # Define a sharpening kernel
    kernel = np.array([[0, -1,  0],
                       [-1,  5, -1],
                       [0, -1,  0]])
    # Apply the sharpening filter to the heightmap
    sharpened = convolve(heightmap, kernel)
    # Adjust the sharpening effect by mixing the original and sharpened maps
    sharpened = heightmap + strength * (sharpened - heightmap)
    # Clip the values to ensure they remain in a valid range
    sharpened = np.clip(sharpened, 0, 1)
    return sharpened

def pointify(height_map, strength=0.5, get_gradient=False):
    dy, dx = np.gradient(height_map)
    gradient_magnitude = np.sqrt(dx**2 + dy**2)
    gradient_magnitude = gradient_magnitude / np.max(gradient_magnitude)
    terrain =  height_map * np.exp(-(strength*gradient_magnitude)**2)
    if get_gradient: return terrain, gradient_magnitude
    return terrain

def pointy_perlin(X, Y, scale, octaves=4, persistence=0.35, lacunarity=2.5, 
                  pointiness=0.5, pointilarity=0.5, seed=42):
    terrain = np.zeros((Y, X))
    p = 1
    scale = scale
    pointiness = pointiness
    for i in range(octaves):
        terrain += p*pointify(perlin(X=X, Y=Y, scale=scale, lacunarity=lacunarity, 
                                     octaves=1, seed=seed+i), strength=pointiness)
        p *= persistence
        scale /= lacunarity
        pointiness += pointilarity
    return terrain

def radial_mask(X, Y, max_value=255):
    x = np.linspace(-1, 1, X); y = np.linspace(-1, 1, Y)
    x_grid, y_grid = np.meshgrid(x, y)
    distance = np.sqrt(x_grid**2 + y_grid**2)
    distance = np.clip(distance, 0, 1)
    heightmap = (1 - distance)**2 * max_value
    return heightmap

def hill(X, Y, seed=42):
    return radial_mask(X,Y)*pointy_perlin(X=X, Y=Y, octaves=4, scale=np.sqrt(X*Y)*0.85, 
                                          pointiness=0.7, pointilarity=0.2, seed=seed)
