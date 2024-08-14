from terra.tess import Voronoi
from terra.random import perlin, warp
from terra.render import gaussian_blur, lingrad
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree

# Define the parameters of the landscape.
S = 42
X = 500; Y = 500

# Generate a randomly tessellated grid of Voronoi cells and relax it 
# so that the dots are more evenly distributed.
tesselation = Voronoi(X, Y, density=0.001, relax=3, seed=S)
tesselation.show()

# Generate a basic fBm heightmap using Perlin noise.
heightmap = perlin(X, Y, scale=250, octaves=1, seed=S)
plt.figure(figsize=(10, 10))
plt.imshow(heightmap, cmap='Greys_r')
plt.show()

def tess_heightmap(tesselation, heightmap):
    """
    Takes in a Voronoi tesselation and a heightmap and returns a heightmap
    where each cell is assigned the average height of the corresponding
    region in the tesselation.

    Args:
    tesselation: Voronoi - a Voronoi tesselation object
    heightmap: numpy array - a 2D array of heights
    """
    # Create a KD-tree for efficient nearest neighbor search
    tree = cKDTree(tesselation.points)
    # Create a grid of all points in the heightmap
    y, x = np.mgrid[0:Y, 0:X]
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

# Create a heightmap where each cell is assigned the average height of the corresponding region
plate_heightmap = tess_heightmap(tesselation, heightmap)
plt.figure(figsize=(10, 10))
plt.imshow(plate_heightmap, cmap='Greys_r')
plt.show()

# Apply Gaussian blur to smooth the heightmap and add details with Perlin noise
heightmap = gaussian_blur(plate_heightmap, sigma=3) + 0.5*perlin(X, Y, scale=100, octaves=5, seed=S)
plt.figure(figsize=(10, 10))
plt.imshow(heightmap, cmap='Greys_r')
plt.show()

# Warp the height map
heightmap = warp(heightmap, shape=(X, Y), warp_strength=2.0, seed=S+3)
plt.figure(figsize=(10, 10))
plt.imshow(heightmap, cmap='Greys_r')
plt.show()


# Show the 3D plot of the heightmap
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(*np.meshgrid(range(X), range(Y)), heightmap, cmap='Greys_r')
plt.show()
"""
# Create a linear gradient temperature map.
linear_tempmap = lingrad(X, Y, start=(X/2,0,30), end=(X/2,Y, -10))
# The greater the height, the colder the temperature.
# Adjust the temperature by subtracting a fraction of the heightmap
# This models the temperature decrease with altitude.
temperaturemap = 30 - 25*heightmap

plt.figure(figsize=(10, 10))
plt.imshow(temperaturemap, cmap='coolwarm')
plt.colorbar()
plt.show()

# Create a noisy precipitation map
precipationmap = 400 * perlin(X, Y, scale=500, octaves=1, seed=S+3)
plt.figure(figsize=(10, 10))
plt.imshow(precipationmap, cmap='Blues')
plt.show()

"""
# Define biome classification based on Whittaker diagram
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
    
# Classify biomes based on temperature, and precipitation.
def classify_biomes(temperaturemap, precipitationmap):
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
"""

# Define the colormap for the biomes
from matplotlib.colors import ListedColormap
# Define the RGB values for each biome and normalize them to [0, 1]
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
# Create a list of colors sorted by biome ID
sorted_biome_colors = [biome_colors[i] for i in sorted(biome_colors.keys())]
# Create the colormap
biome_cmap = ListedColormap(sorted_biome_colors)
# Createa a biome cmap
biome_map = classify_biomes(temperaturemap, precipationmap)
plt.figure(figsize=(10, 10))
plt.imshow(biome_map, cmap=biome_cmap)
plt.show()

# Warp the biome map
biome_map = warp(biome_map, shape=(X, Y), warp_strength=2.0, seed=S+4)
plt.figure(figsize=(10, 10))
plt.imshow(biome_map, cmap=biome_cmap)
plt.show()

"""





# Erode the heightmap using the thermal and hydraulic erosion algorithms
#height = sim.errode(heightmap, temperaturemap, precipationmap, drops=X*Y//10, dropsize=X*Y//10)


# Create snow map and apply it with slight elevation to the heightmap

#texture = ...

#material = ...

#render.export_to_png("example_1", height, texture, material)