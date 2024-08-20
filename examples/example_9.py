# Example usage:
from terra.sim import  pointy_perlin
from terra.render import export, terrain_cmap, gras_gradient, snow_gradient
from terra.new_erosion import erode
import matplotlib.pyplot as plt
import numpy as np

#heightmap = pointy_perlin(X=300*3, Y=300*3, scale=250*3)
#export(heightmap, 'terrain.png', cmap='Greys_r')
#eroded_heightmap, path_map = erode(heightmap, num_iterations=5000*4, max_droplet_lifetime=100)
#export(eroded_heightmap, 'erosion.png', cmap='Greys_r')


path_map = import_map('path_map.png')
eroded_heightmap = import_map('erosion.png')

gras = gras_gradient(eroded_heightmap, strength=3, cutoff=0.003, blur=2.2)
export(-gras, 'gras.png', cmap='Greens')
snow = snow_gradient(eroded_heightmap, strength=10, cutoff=0.02)
export(-snow, 'snow.png', cmap='Greys')

export(eroded_heightmap, "erosion_color.png", cmap=terrain_cmap())



export(np.log1p(path_map), 'path_map.png', cmap='Blues')
