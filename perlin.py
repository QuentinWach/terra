# Create perlin noise terrain
import numpy as np
"""
def perlin(x, y, seed=0):
    np.random.seed(seed)
    p = np.arange(256, dtype=int)
    np.random.shuffle(p)
    p = np.stack([p, p]).flatten()
    xi = x.astype(int)
    yi = y.astype(int)
    xf = x - xi
    yf = y - yi
    u = fade(xf)
    v = fade(yf)
    n00 = gradient(p[p[xi] + yi], xf, yf)
    n01 = gradient(p[p[xi] + yi + 1], xf, yf - 1)
    n11 = gradient(p[p[xi + 1] + yi + 1], xf - 1, yf - 1)
    n10 = gradient(p[p[xi + 1] + yi], xf - 1, yf)
    x1 = lerp(n00, n10, u)
    x2 = lerp(n01, n11, u)
    return lerp(x1, x2, v)

def lerp(a, b, x):
    return a + x * (b-a)

def fade(t):
    return 6 * t**5 - 15 * t**4 + 10 * t**3

def gradient(h,x,y):
    vectors = np.array([[0,1],[0,-1],[1,0],[-1,0]])
    g = vectors[h % 4]
    return g[:,:,0] * x + g[:,:,1] * y

def generate_perlin_noise_2d(shape, res):
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    grid = np.mgrid[0:res[0]:delta[0],0:res[1]:delta[1]].transpose(1,2,0) % 1
    # Gradients
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    g00 = gradients[0:-1,0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:,0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1,1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:,1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps
    n00 = np.sum(np.dstack((grid[:,:,0] - 0, grid[:,:,1] - 0)) * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0] - 1, grid[:,:,1] - 0)) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0] - 0, grid[:,:,1] - 1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0] - 1, grid[:,:,1] - 1)) * g11, 2)
    # Interpolation
    t = fade(grid)
    n0 = n00 * (1-t[:,:,0]) + t[:,:,0] * n10
    n1 = n01 * (1-t[:,:,0]) + t[:,:,0] * n11
    return np.sqrt(2) * ((1-t[:,:,1]) * n0 + t[:,:,1] * n1)
"""

def interpolant(t):
    return t*t*t*(t*(t*6 - 15) + 10)


def generate_perlin_noise_2d(
        shape, res, tileable=(False, False), interpolant=interpolant):
    """Generate a 2D numpy array of Perlin noise.

    Args:
        shape: The shape of the generated array (tuple of two ints).
            This must be a multiple of res.
        res: The number of periods of noise to generate along each
            axis (tuple of two ints). Note shape must be a multiple of
            res.
        tileable: If the noise should be tileable along each axis
            (tuple of two bools). Defaults to (False, False).
        interpolant: The interpolation function, defaults to
            t*t*t*(t*(t*6 - 15) + 10).

    Returns:
        A numpy array of shape shape with the generated noise.

    Raises:
        ValueError: If shape is not a multiple of res.
    """
    # Ensure shape and res are tuples
    if isinstance(shape, np.ndarray):
        shape = tuple(shape)
    if isinstance(res, np.ndarray):
        res = tuple(res)

    # Ensure shape and res are tuples of two integers
    if not (isinstance(shape, tuple) and len(shape) == 2 and all(isinstance(x, int) for x in shape)):
        raise ValueError("shape must be a tuple of two integers")
    if not (isinstance(res, tuple) and len(res) == 2 and all(isinstance(x, int) for x in res)):
        raise ValueError("res must be a tuple of two integers")

    # Check if shape is a multiple of res
    if (shape[0] % res[0] != 0) or (shape[1] % res[1] != 0):
        raise ValueError("shape must be a multiple of res")
    
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    
    # Create a grid of coordinates
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    
    # Gradients
    angles = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    
    if tileable[0]:
        gradients[-1, :] = gradients[0, :]
    if tileable[1]:
        gradients[:, -1] = gradients[:, 0]
    
    gradients = gradients.repeat(d[0], axis=0).repeat(d[1], axis=1)
    
    g00 = gradients[:-d[0], :-d[1]]
    g10 = gradients[d[0]:, :-d[1]]
    g01 = gradients[:-d[0], d[1]:]
    g11 = gradients[d[0]:, d[1]:]
    
    # Ramps
    n00 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1])) * g00, axis=2)
    n10 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1])) * g10, axis=2)
    n01 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1] - 1)) * g01, axis=2)
    n11 = np.sum(np.dstack((grid[:, :, 0] - 1, grid[:, :, 1] - 1)) * g11, axis=2)
    
    # Interpolation
    t = interpolant(grid)
    n0 = n00 * (1 - t[:, :, 0]) + t[:, :, 0] * n10
    n1 = n01 * (1 - t[:, :, 0]) + t[:, :, 0] * n11
    
    return np.sqrt(2) * ((1 - t[:, :, 1]) * n0 + t[:, :, 1] * n1)



def generate_fractal_noise_2d(
        shape, res, octaves=1, persistence=0.5,
        lacunarity=2, tileable=(False, False),
        interpolant=interpolant
):
    """Generate a 2D numpy array of fractal noise.

    Args:
        shape: The shape of the generated array (tuple of two ints).
            This must be a multiple of lacunarity**(octaves-1)*res.
        res: The number of periods of noise to generate along each
            axis (tuple of two ints). Note shape must be a multiple of
            (lacunarity**(octaves-1)*res).
        octaves: The number of octaves in the noise. Defaults to 1.
        persistence: The scaling factor between two octaves.
        lacunarity: The frequency factor between two octaves.
        tileable: If the noise should be tileable along each axis
            (tuple of two bools). Defaults to (False, False).
        interpolant: The, interpolation function, defaults to
            t*t*t*(t*(t*6 - 15) + 10).

    Returns:
        A numpy array of fractal noise and of shape shape generated by
        combining several octaves of perlin noise.

    Raises:
        ValueError: If shape is not a multiple of
            (lacunarity**(octaves-1)*res).
    """
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    for _ in range(octaves):
        noise += amplitude * generate_perlin_noise_2d(
            shape, (frequency*res[0], frequency*res[1]), tileable, interpolant
        )
        frequency *= lacunarity
        amplitude *= persistence
    return noise

def generate_fractal_terrain(shape, res, octaves=4, persistence=0.5):
    noise = generate_fractal_noise_2d(shape, res, octaves, persistence)
    return 10 * noise

def generate_terrain(shape, res):
    noise = generate_perlin_noise_2d(shape, res)
    return 10 * noise

def plot_terrain(terrain):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.imshow(terrain, cmap='terrain', interpolation=None)
    plt.colorbar()
    plt.show()
"""
def plot3d_terrain(terrain):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    x = np.arange(0, terrain.shape[0], 1)
    y = np.arange(0, terrain.shape[1], 1)
    x, y = np.meshgrid(x, y)
    
    surf = ax.plot_surface(x, y, terrain, cmap='terrain', edgecolor='none', antialiased=True)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Elevation')
    
    fig.colorbar(surf, shrink=0.5, aspect=5)
    
    # Set an initial view
    ax.view_init(elev=30, azim=45)
    
    plt.show()

"""
def plot3d_terrain(terrain):
    import matplotlib.pyplot as plt
    from matplotlib import cm

    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    x = np.arange(0, terrain.shape[0], 1)
    y = np.arange(0, terrain.shape[1], 1)
    x, y = np.meshgrid(x, y)

    # Plot the surface with improved parameters
    surf = ax.plot_surface(x, y, terrain, cmap=cm.terrain,
                           linewidth=0.0, antialiased=True, shade=True, 
                           rstride=8, cstride=8,
                           edgecolor='none', rasterized=True)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Elevation')

    # Add a color bar
    fig.colorbar(surf, shrink=0.1, aspect=5)

    # Set an initial view
    ax.view_init(elev=30, azim=45)

    # Remove the background color
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

    # Make the grid lines transparent
    ax.xaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.yaxis._axinfo["grid"]['color'] =  (1,1,1,0)
    ax.zaxis._axinfo["grid"]['color'] =  (1,1,1,0)

    plt.tight_layout()
    plt.show()

#if __name__ == '__main__':
#    shape = (1024, 1024)
#    res = (4, 4)
#    terrain = generate_terrain(shape, res)
#    plot3d_terrain(terrain)
#    terrain = generate_fractal_terrain(shape, res)
#    plot3d_terrain(terrain)