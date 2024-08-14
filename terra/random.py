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


def warp(heightmap, shape, warp_strength=2.0, seed=0):
    """Warp the input heightmap to create a more organic look."""
    height, width = shape[0], shape[1]
    y, x = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    
    # Normalize coordinates to [0, 1] range
    x = x / width
    y = y / height
    
    # First warping
    qx = perlin(width, height, scale=100, seed=seed)
    qy = perlin(width, height, scale=100, seed=seed+1)
    
    # Second warping
    rx = perlin(width, height, scale=50, seed=seed+2) * 4.0 * qx + 1.7
    ry = perlin(width, height, scale=50, seed=seed+3) * 4.0 * qy + 9.2
    
    # Final warping
    warped_x = x + warp_strength * rx
    warped_y = y + warp_strength * ry
    
    # Clip coordinates to ensure they're within the valid range
    warped_x = np.clip(warped_x * (width - 1), 0, width - 1)
    warped_y = np.clip(warped_y * (height - 1), 0, height - 1)

    # Use cubic interpolation with "reflect" mode to sample the warped heightmap
    warped_heightmap = map_coordinates(heightmap, [warped_y, warped_x], order=3, mode="reflect")
    
    return warped_heightmap