from scipy.ndimage import gaussian_filter
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.spatial import cKDTree

def gaussian_blur(height_map, sigma=30):
    """
    Apply a Gaussian blur to a height map.

    Args:
    height_map (np.ndarray): A 2D array of shape (y, x) representing the height map.
    sigma (float): Standard deviation of the Gaussian kernel.
    """
    return gaussian_filter(height_map, sigma=sigma)

def lingrad(x, y, start, end):
    """
    Generate a linear gradient height map.
    
    Args:
    x (int): Width of the height map.
    y (int): Height of the height map.
    start (tuple): (x, y, height) of the start point.
    end (tuple): (x, y, height) of the end point.
    
    Returns:
    np.ndarray: A 2D array of shape (y, x) representing the height map.
    """
    # Create a grid of coordinates
    xv, yv = np.meshgrid(np.arange(x), np.arange(y))
    # Calculate the difference in coordinates and height
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dh = end[2] - start[2]
    # Calculate the distances from the start point
    dist_from_start_x = xv - start[0]
    dist_from_start_y = yv - start[1]
    # Calculate the projection of each point onto the gradient direction
    projection = (dist_from_start_x * dx + dist_from_start_y * dy) / (dx**2 + dy**2)
    # Interpolate the height at each point
    height_map = start[2] + projection * dh
    # Clamp the height map to the range [start[2], end[2]]
    height_map = np.clip(height_map, min(start[2], end[2]), max(start[2], end[2]))
    return height_map

def gradient(heightmap):
    """
    Calculate the gradient magnitude of a 2D heightmap.
    
    Args:
    heightmap (numpy.ndarray): 2D array representing the heightmap
    
    Returns:
    numpy.ndarray: 2D array representing the gradient magnitude
    """
    dy, dx = np.gradient(heightmap)
    return np.sqrt(dy**2 + dx**2)

#def divergence(heightmap):
    """
    Calculate the divergence of a 2D heightmap.
    This interprets the heightmap as a scalar potential field.
    
    Args:
    heightmap (numpy.ndarray): 2D array representing the heightmap
    
    Returns:
    numpy.ndarray: 2D array representing the divergence
    """
    dy, dx = np.gradient(heightmap)
    return np.gradient(dx, axis=1) + np.gradient(dy, axis=0)

#def curl(heightmap):
    """
    Calculate the curl magnitude of a 2D heightmap.
    This interprets the heightmap as a scalar potential field.
    Note: In 2D, curl is a scalar (the z-component of the 3D curl).
    
    Args:
    heightmap (numpy.ndarray): 2D array representing the heightmap
    
    Returns:
    numpy.ndarray: 2D array representing the curl magnitude
    """
    dy, dx = np.gradient(heightmap)
    return np.abs(np.gradient(dx, axis=0) - np.gradient(dy, axis=1))

def tess_heightmap(tesselation, shape, heightmap):
    """
    Takes in a Voronoi tesselation and a heightmap and returns a heightmap
    where each cell is assigned the average height of the corresponding
    region in the tesselation.

    Args:
    tesselation: Voronoi - a Voronoi tesselation object
    heightmap: numpy array - a 2D array of heights
    """
    X, Y = shape[0], shape[1]
    # Create a KD-tree for efficient nearest neighbor search
    tree = cKDTree(tesselation.points)
    # Create a grid of all points in the heightmap
    y, x = np.mgrid[0:X, 0:Y]
    grid_points = np.column_stack((x.ravel(), y.ravel()))
    # Find the nearest Voronoi point for each grid point
    _, cell_indices = tree.query(grid_points)
    # Reshape cell_indices to match the heightmap shape
    cell_map = cell_indices.reshape(Y, X)
    # Calculate average height for each cell
    unique_cells = np.unique(cell_indices)
    max_cell_index = np.max(cell_indices)
    plate_heights = np.zeros(max_cell_index + 1)
    for cell in unique_cells:
        mask = cell_map == cell
        plate_heights[cell] = np.mean(heightmap[mask])
    # Create the plate heightmap
    plate_heightmap = plate_heights[cell_map]
    return plate_heightmap

def classify_biome_cell(temperature, precipitation):
    """
    Create bioms based on the height, temperature and precipitation maps using a simple rule-based system
    Whittaker diagram: https://en.wikipedia.org/wiki/Whittaker_diagram
    """
    # Tundra
    if temperature <= 0:
        return 1
    # Temperate grassland
    elif temperature > 0 and temperature <= 20 and precipitation < 50:
        return 2
    # Subtropical desert
    elif temperature > 20 and precipitation < 50:
        return 3
    elif temperature > 25 and precipitation < 100:
        return 3
    # Boreal forest
    elif temperature > 0 and temperature <= 5 and precipitation >= 50 and precipitation < 150:
        return 4
    elif temperature > 5 and temperature <= 10 and precipitation >= 100 and precipitation < 200:
        return 4
    # Woodland / scrupland
    elif temperature > 5 and temperature <= 20 and precipitation >= 50 and precipitation < 100:
        return 5
    # Temperate seasonal forest
    elif temperature > 10 and temperature <= 20 and precipitation >= 100 and precipitation < 200:
        return 6
    # Tropical seasonal forest
    elif temperature > 20 and precipitation >= 100 and precipitation < 250:
        return 7
    elif temperature > 20 and temperature <= 25 and precipitation >= 50 and precipitation < 100:
        return 7
    elif temperature > 25 and precipitation >= 250 and precipitation < 300:
        return 7
    # Tropical rainforest
    elif temperature > 20 and temperature <= 25 and precipitation >= 250:
        return 8
    elif temperature > 25 and precipitation >= 300:
        return 8
    # Temperate rainforest
    elif temperature > 10 and temperature <= 20 and precipitation >= 200:
        return 9
    
def classify_biomes(temperaturemap, shape, precipitationmap):
    """
    Classify biomes based on temperature, and precipitation.
    """
    X, Y = shape[0], shape[1]
    # Check if the dimensions of the maps are the same.
    assert temperaturemap.shape == precipitationmap.shape
    Y, X = temperaturemap.shape
    # Create an empty biome map.
    biome_map = np.zeros((Y, X))
    # Classify biomes for each cell in the maps.
    for y in range(Y):
        for x in range(X):
            temperature = temperaturemap[y, x]
            precipitation = precipitationmap[y, x]
            biome = classify_biome_cell(temperature, precipitation)
            biome_map[y, x] = biome
    return biome_map

def export(map, filename, cmap, dpi=300):
    """
    Export a heightmap to a PNG file.
    
    Args:
    map (np.ndarray): A 2D array of shape (y, x) representing the height map.
    filename (str): The name of the file to save the height map to.
    """
    plt.imsave(filename, map, cmap=cmap, dpi=dpi)

# Create the biomes class colormap
biome_colors = {
    1: (148/255, 168/255, 174/255),  # Tundra
    2: (147/255, 127/255, 44/255),   # Temperate grassland/cold desert
    3: (201/255, 114/255, 52/255),   # Subtropical desert
    4: (91/255, 144/255, 81/255),    # Boreal forest
    5: (180/255, 125/255, 1/255),    # Woodland/shrubland
    6: (40/255, 138/255, 161/255),   # Temperate seasonal forest
    7: (152/255, 166/255, 34/255),   # Tropical seasonal forest
    8: (1/255, 82/255, 44/255),      # Tropical rainforest
    9: (3/255, 83/255, 109/255)      # Temperate rainforest
}
sorted_biome_colors = [biome_colors[i] for i in sorted(biome_colors.keys())]
biome_cmap = ListedColormap(sorted_biome_colors)