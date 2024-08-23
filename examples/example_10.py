# Example usage:
from terra.sim import  pointy_perlin
from terra.render import export, terrain_cmap
from terra.fast_erosion import erode
import numpy as np

heightmap = pointy_perlin(X=300, Y=300, scale=150)


eroded_heightmap, rain_map = erode(heightmap, num_iterations=20, 
                                   dt=0.05, k_c=0.5, k_s=5, k_d=0.9, k_e=0.003, 
                                   erosion_flag=True) #0.8



export(heightmap, 'terrain.png', cmap='Greys_r')
export(heightmap, 'terrain_color.png', cmap=terrain_cmap())
export(eroded_heightmap, 'erosion.png', cmap='Greys_r')
export(eroded_heightmap, "erosion_color.png", cmap=terrain_cmap())
export(np.log1p(rain_map), 'water_map.png', cmap='Blues')
export(eroded_heightmap-heightmap, 'diff.png', cmap='Greys')