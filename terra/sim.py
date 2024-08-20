import numpy as np
from terra.randd import perlin

def pointify(height_map, strength=0.5, get_gradient=False):
    dy, dx = np.gradient(height_map)
    gradient_magnitude = np.sqrt(dx**2 + dy**2)
    gradient_magnitude = gradient_magnitude / np.max(gradient_magnitude)
    terrain =  height_map * np.exp(-(strength*gradient_magnitude)**2)
    if get_gradient: return terrain, gradient_magnitude
    return terrain

def pointy_perlin(X, Y, scale, octaves=4, persistence=0.35, lacunarity=2.5, 
                  pointiness=0.5, pointilarity=0.5, seed=42):
    terrain = np.zeros((Y, X))
    p = 1
    scale = scale
    pointiness = pointiness
    for i in range(octaves):
        terrain += p*pointify(perlin(X=X, Y=Y, scale=scale, lacunarity=lacunarity, 
                                     octaves=1, seed=seed+i), strength=pointiness)
        p *= persistence
        scale /= lacunarity
        pointiness += pointilarity
    return terrain

def radial_mask(X, Y, max_value=255):
    x = np.linspace(-1, 1, X); y = np.linspace(-1, 1, Y)
    x_grid, y_grid = np.meshgrid(x, y)
    distance = np.sqrt(x_grid**2 + y_grid**2)
    distance = np.clip(distance, 0, 1)
    heightmap = (1 - distance)**2 * max_value
    return heightmap

def hill(X, Y, seed=42):
    return radial_mask(X,Y)*pointy_perlin(X=X, Y=Y, octaves=4, scale=np.sqrt(X*Y)*0.85, 
                                          pointiness=0.7, pointilarity=0.2, seed=seed)

