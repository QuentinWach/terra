import numpy as np
from scipy.ndimage import map_coordinates

def generate_permutation(n):
    perm = np.arange(n, dtype=np.int32)
    np.random.shuffle(perm)
    return np.concatenate((perm, perm))

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(t, a, b):
    return a + t * (b - a)

def grad(hash, x, y):
    h = hash & 15
    u = x if h < 8 else y
    v = y if h < 4 else (x if h in [12, 14] else 0)
    return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)

def perlin(X, Y, scale=10, octaves=1, persistence=0.5, lacunarity=2.0, seed=None):
    """
    Generate a Perlin noise heightmap.
    
    Args:
    X, Y: int - dimensions of the heightmap
    scale: float - initial scale of the noise
    octaves: int - number of octaves for fBm
    persistence: float - amplitude decrease factor for each octave
    lacunarity: float - frequency increase factor for each octave
    seed: int - random seed for reproducibility
    
    Returns:
    numpy array of the heightmap
    """
    if seed is not None:
        np.random.seed(seed)
    
    p = generate_permutation(256)
    
    def noise2d(x, y):
        X = int(x) & 255
        Y = int(y) & 255
        x -= int(x)
        y -= int(y)
        u = fade(x)
        v = fade(y)
        A = p[X] + Y
        B = p[X + 1] + Y
        return lerp(v, 
                    lerp(u, grad(p[A], x, y), grad(p[B], x - 1, y)),
                    lerp(u, grad(p[A + 1], x, y - 1), grad(p[B + 1], x - 1, y - 1)))
    
    noise = np.zeros((Y, X))
    amplitude = 1.0
    freq = 1.0 / scale
    for _ in range(octaves):
        for y in range(Y):
            for x in range(X):
                noise[y, x] += amplitude * noise2d(x * freq, y * freq)
        amplitude *= persistence
        freq *= lacunarity
    
    # Normalize to [0, 1]
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    
    return noise

"""
def warp(heightmap, shape, warp_strength=100.0, seed=0):
    #Warp the input heightmap to create a more organic look.
    height, width = shape[0], shape[1]
    y, x = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    
    # Generate warping noise
    qx = perlin(width, height, scale=int(shape[1]//5), octaves=3, seed=seed)
    qy = perlin(width, height, scale=int(shape[0]//5), octaves=3, seed=seed+1)
    
    rx = perlin(width, height, scale=int(shape[1]//10), octaves=3, seed=seed+2)
    ry = perlin(width, height, scale=int(shape[0]//10), octaves=3, seed=seed+3)
    
    # Apply warping
    x_warped = x + warp_strength * (qx + rx)
    y_warped = y + warp_strength * (qy + ry)
    
    # Clip coordinates to ensure they're within the valid range
    x_warped = np.clip(x_warped, 0, width - 1)
    y_warped = np.clip(y_warped, 0, height - 1)
    
    # Use cubic interpolation with "reflect" mode to sample the warped heightmap
    warped_heightmap = map_coordinates(heightmap, [y_warped, x_warped], order=3, mode="reflect")
    
    return warped_heightmap
"""

def warp(heightmap, shape, warp_strength=2.0, seed=0):
    """
    Warp the input heightmap to create a more organic look.
    Works with heightmaps containing arbitrary values.
    """
    height, width = shape[0], shape[1]
    y, x = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    # Store original min and max for denormalization later
    original_min = np.min(heightmap)
    original_max = np.max(heightmap)
    # Handle NaN values before normalization
    mask = np.isnan(heightmap)
    heightmap_filled = np.where(mask, np.nanmean(heightmap), heightmap)
    # Normalize heightmap to [0, 1] range
    original_min = np.nanmin(heightmap_filled)
    original_max = np.nanmax(heightmap_filled)
    heightmap_normalized = (heightmap_filled - original_min) / (original_max - original_min)
    # Generate warping noise
    # First warp
    qx = perlin(width, height, scale=20, octaves=4, seed=seed)
    qy = perlin(width, height, scale=20, octaves=4, seed=seed+1)
    # Second warp
    rx = perlin(width, height, scale=10, octaves=4, seed=seed+2)
    ry = perlin(width, height, scale=10, octaves=4, seed=seed+3)
    # Apply warping
    x_warped = x + warp_strength * (qx + rx)
    y_warped = y + warp_strength * (qy + ry)
    # Clip coordinates to ensure they're within the valid range
    x_warped = np.clip(x_warped, 0, width - 1)
    y_warped = np.clip(y_warped, 0, height - 1)
    # Use cubic interpolation with "reflect" mode to sample the warped heightmap
    warped_heightmap = map_coordinates(heightmap_normalized, [y_warped, x_warped], order=3, mode="reflect")
    # Denormalize the warped heightmap back to the original value range
    warped_heightmap = warped_heightmap * (original_max - original_min) + original_min
    # Reapply the mask after warping
    warped_heightmap = np.where(mask, np.nan, warped_heightmap)    
    return warped_heightmap