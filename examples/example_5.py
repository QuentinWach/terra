from terra.sim import *
from terra.render import *
S=69; X = 1000; Y = 1000
terrain = pointy_perlin(X, Y, scale=200, octaves=5, persistence=0.35, 
                        lacunarity=2.5, pointiness=0.5, pointilarity=0.5, seed=S)
terrain_normal = normal_map(terrain)
export(terrain, 'terrain.png', cmap="Greys_r", dpi=300)
export(terrain, 'terrain_color.png', cmap=terrain_cmap(), dpi=300)