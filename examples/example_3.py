from terra.rand import perlin, warp
from terra.render import export
from terra.sim import wet

# Create a Perlin noise heightmap
S = 42; X = 500; Y = 500
wideterrain = perlin(X, Y, scale=1000, octaves=1, seed=S)
terrain = wideterrain*perlin(X, Y, scale=100, octaves=3, seed=S)
# Save the Perlin noise map
export(terrain, 'before_wet.png', cmap='Greys_r', dpi=300)
# Erode the Perlin noise map by wetting it
eroded = wet(terrain, strength=5)
# Save the eroded map
export(eroded, 'after_wet.png', cmap='Greys_r', dpi=300)
# Save the difference
export(eroded - terrain, 'diff_wet.png', cmap='Greys_r', dpi=300)   