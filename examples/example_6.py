from terra.sim import *
from terra.render import *
from terra.tess import *
from terra.randd import *
S=69; X = 500; Y = 500
large = Voronoi(X, Y, 0.00005, 1, seed=S)
large = tess_heightmap(large, (X, Y), perlin(X, Y, scale=500, octaves=3, persistence=0.35, lacunarity=2.5, seed=S))
large = warp(large, (X,Y), warp_strength=50.0, seed=S)
large = gaussian_blur(large, 4)
export(large, 'large.png', cmap="Greys_r", dpi=300)
medium = Voronoi(X, Y, 0.001, 1, seed=S)
medium = tess_heightmap(medium, (X, Y), perlin(X, Y, scale=300, octaves=4, persistence=0.35, lacunarity=2.5, seed=S))
medium = gaussian_blur(medium, 2)
export(medium, 'medium.png', cmap="Greys_r", dpi=300)
small = 0.60*large + 0.25*medium + 0.15*pointy_perlin(X, Y, scale=100, octaves=6, persistence=0.35, lacunarity=2.5, pointiness=0.5, pointilarity=0.5, seed=S)
small += 0.05*perlin(X, Y, scale=10, octaves=3, persistence=0.35, lacunarity=2.5, seed=S)
export(small, 'small.png', cmap="Greys_r", dpi=300)
export(small, 'small_color.png', cmap=terrain_cmap(), dpi=300)