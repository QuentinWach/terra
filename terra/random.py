import numpy as np

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