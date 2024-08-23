# Example usage:
from terra.sim import  pointy_perlin
from terra.render import export, terrain_cmap
from terra.fast_erosion import erode
from terra.randd import perlin
import numpy as np

heightmap = pointy_perlin(X=300*3, Y=300*3, scale=150*3)
heightmap = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min())

eroded_heightmaps, water_maps, sediment_map, rain_maps = erode(heightmap, num_iterations=200, 
                                   dt=0.1, k_c=0.1, k_s=0.04, k_d=0.1, k_e=0.003, 
                                   erosion_flag=True)
"""
num_iterations: int = {1, inf} TIME (NUMBER OF ITERATIONS)
        1 -> barely to no erosion
        50 -> minimal erosion
        100 -> (STANDARD) typically more than enough for a good erosion simulation
        200 -> extreme
        ...
        10000 -> ultra

k_e: float = {0, 1} EVAPORATION
        0.0003 -> WETLAND: no evaporation
        0.003 -> (STANDARD) JUNGLE: smooth water flow leading to a curvy terrain
        0.03 -> FOREST: moderate water flow leading to a hilly terrain
        0.3 -> DESERT: sharp water flow leading to an edge, step-like terrain

k_s: float = {0, 0.1} DISSOLVING   --> It isn't clear what this parameters does exactly.
        0.01 -> Minimum -> Helps to keep holes at bay.
        0.04 -> (STANDARD) Maximum
        0.08 -> Maximum

k_c: float = {0, 0.1} SEDIMENT CAPACITY --> Overall lessening the erosion
        0.01 -> Minimum
        0.1 -> (STANDARD)

k_d: float = {0, 0.1} DEPOSITION
        0.001 -> Minimum barely anything happens. Keeps holes at bay
        0.01 -> Minimum
        0.1 -> (STANDARD)
        0.5 -> Heightend
        1 -> Maximum
"""

# create an animation of the water maps with matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig = plt.figure()
ims = []
for i in range(len(water_maps)):
    im = plt.imshow(water_maps[i], cmap='Blues', animated=True)
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, interval=20, blit=True, repeat_delay=1000)
plt.show()

export(heightmap, 'terrain.png', cmap='Greys_r')
export(heightmap, 'terrain_color.png', cmap=terrain_cmap())
export(eroded_heightmaps[-1], 'erosion.png', cmap='Greys_r')
export(eroded_heightmaps[-1], "erosion_color.png", cmap=terrain_cmap())
export(water_maps[-1]-(0.04*z.copy() + 0.01*perlin(300*3, 300*3, scale=0.5*max(300*3, 300*3), seed=0)), 'water_map.png', cmap='Blues')
export(sediment_map, 'sediment_map.png', cmap='Reds')
export(np.log1p(rain_maps[-1]), 'rain_map.png', cmap='Blues')
export(eroded_heightmaps[-1]-heightmap, 'diff.png', cmap='Greys')
