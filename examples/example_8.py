# Example usage:
from terra.sim import  pointy_perlin
from terra.render import export, terrain_cmap, normal_map
from terra.new_erosion import erode
import matplotlib.pyplot as plt
import numpy as np

heightmap = pointy_perlin(X=600, Y=600, scale=200)
export(heightmap, 'terrain.png', cmap='Greys_r')
eroded_heightmap, path_map = erode(heightmap, num_iterations=20000)
export(eroded_heightmap, 'erosion.png', cmap='Greys_r')
export(normal_map(eroded_heightmap), 'erosion_normal.png', cmap='viridis')
export(eroded_heightmap, "erosion_color.png", cmap=terrain_cmap())
export(np.log1p(path_map), 'path_map.png', cmap='Blues')


# Visualize the results
fig, axs = plt.subplots(2, 2, figsize=(15, 15))

axs[0, 0].imshow(heightmap, cmap=terrain_cmap())
axs[0, 0].set_title('Original Heightmap')

axs[0, 1].imshow(eroded_heightmap, cmap=terrain_cmap())
axs[0, 1].set_title('Eroded Heightmap')

axs[1, 0].imshow(eroded_heightmap - heightmap, cmap='RdBu')
axs[1, 0].set_title('Difference (Eroded - Original)')

axs[1, 1].imshow(np.log1p(path_map), cmap='viridis')
axs[1, 1].set_title('Water Droplet Paths (Log Scale)')

plt.tight_layout()
plt.show()
