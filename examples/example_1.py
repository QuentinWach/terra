from terra.tess import Voronoi
from terra.random import perlin
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
plt.imshow(heightmap, cmap='terrain')
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
plt.imshow(plate_heightmap, cmap='terrain')
plt.show()

# Apply Gaussian blur to smooth the heightmap and add details with Perlin noise
heightmap = gaussian_blur(plate_heightmap, sigma=3) + 0.5*perlin(X, Y, scale=100, octaves=5, seed=S)
plt.figure(figsize=(10, 10))
plt.imshow(heightmap, cmap='terrain')
plt.show()

# Show the 3D plot of the heightmap
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(*np.meshgrid(range(X), range(Y)), heightmap, cmap='terrain')
plt.show()

# Create a linear gradient temperature map
temperaturemap = lingrad(X, Y, start=(X/2,0,40), end=(X/2,Y, -40))
plt.figure(figsize=(10, 10))
plt.imshow(temperaturemap, cmap='coolwarm')
plt.show()

# Create a noisy precipitation map
precipationmap = perlin(X, Y, scale=500, octaves=1, seed=S+3)
plt.figure(figsize=(10, 10))
plt.imshow(precipationmap, cmap='Blues')
plt.show()

#height = sim.errode(heightmap, temperaturemap, precipationmap, drops=X*Y//10, dropsize=X*Y//10)

#texture = ...

#material = ...

#render.export_to_png("example_1", height, texture, material)