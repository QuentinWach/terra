import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def terrain_cmap():
    colors = [
        (0, 0.2, 0.5),     # Deep water
        (0, 0.5, 1),       # Shallow water
        (0.9, 0.8, 0.6),   # Sand
        (0.5, 0.7, 0.3),   # Grass
        (0.2, 0.5, 0.2),   # Forest
        (0.6, 0.6, 0.6),   # Mountains
        (1, 1, 1)          # Snow
    ]
    
    # Create a continuous colormap
    cmap = LinearSegmentedColormap.from_list("terrain", colors, N=256)
    
    return cmap

# Example usage:
height_data = np.random.rand(100, 100)  # Replace with your actual heightmap data
plt.imshow(height_data, cmap=terrain_cmap())
plt.colorbar()
plt.title("Continuous Terrain Heightmap")
plt.show()