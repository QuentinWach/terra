import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d
from scipy.ndimage import gaussian_filter
from scipy.ndimage import map_coordinates

def voronoi_grid(shape, n_points):
    points = np.random.rand(n_points, 2) * shape
    vor = Voronoi(points)
    return vor

def plot_voronoi_grid(vor, shape):
    _, ax = plt.subplots(figsize=(10, 10))
    voronoi_plot_2d(vor, ax=ax, show_vertices=False, line_colors='k', line_width=2, line_alpha=0.6, point_size=0)
    ax.set_xlim(0, shape[0])
    ax.set_ylim(0, shape[1])
    plt.show()

def create_tectonic_plates(shape, n_plates):
    vor = voronoi_grid(shape, n_plates)
    plate_heights = np.random.uniform(0.2, 1.0, n_plates)
    return vor, plate_heights

def create_tectonic_mountains(vor, plate_heights, shape):
    height_map = np.zeros(shape)
    for y in range(shape[1]):
        for x in range(shape[0]):
            distances = np.sum((vor.points - [x, y])**2, axis=1)
            nearest_plate = np.argmin(distances)
            height_map[y, x] = plate_heights[nearest_plate]
    return height_map

def gaussian_blur(height_map, sigma=30):
    # Apply Gaussian filter to smooth the height map
    return gaussian_filter(height_map, sigma=sigma)

def warp_terrain(height_map, warp_factor=0.1):
    # Warp the terrain based on the height map using the warper function
    pass

"""
def perlin(x, y, seed=0):
    np.random.seed(seed)
    p = np.arange(256, dtype=int)
    np.random.shuffle(p)
    p = np.stack([p, p]).flatten()
    
    x, y = x.astype(float), y.astype(float)
    xi, yi = x.astype(int) & 255, y.astype(int) & 255
    xf, yf = x - xi, y - yi
    u, v = 6 * xf**5 - 15 * xf**4 + 10 * xf**3, 6 * yf**5 - 15 * yf**4 + 10 * yf**3
    
    a, b = p[xi], p[yi]
    aa, ab, ba, bb = p[a], p[a + 1], p[b], p[b + 1]
    
    def grad(h, x, y):
        vectors = np.array([[0, 1], [0, -1], [1, 0], [-1, 0]])
        g = vectors[h % 4]
        return g[:, :, 0] * x + g[:, :, 1] * y
    
    g1 = grad(p[aa + yi], xf, yf)
    g2 = grad(p[ba + yi], xf - 1, yf)
    g3 = grad(p[ab + yi], xf, yf - 1)
    g4 = grad(p[bb + yi], xf - 1, yf - 1)
    
    return (g1 * (1 - u) * (1 - v) + 
            g2 * u * (1 - v) + 
            g3 * (1 - u) * v + 
            g4 * u * v)
"""


"""
def perlin(x, y, seed=0):
    np.random.seed(seed)
    p = np.arange(256, dtype=int)
    np.random.shuffle(p)
    p = np.stack([p, p]).flatten()

    xi, yi = x.astype(int) & 255, y.astype(int) & 255
    xf, yf = x - xi, y - yi
    u, v = 6 * xf**5 - 15 * xf**4 + 10 * xf**3, 6 * yf**5 - 15 * yf**4 + 10 * yf**3
    
    def grad(h, x, y):
        # Improved gradient vectors for better results
        vectors = np.array([[1,1],[-1,1],[1,-1],[-1,-1],
                            [1,0],[-1,0],[0,1],[0,-1]])
        g = vectors[h % 8]
        return g[0] * x + g[1] * y

    aa, ab = p[xi] + yi, p[xi] + yi + 1
    ba, bb = p[xi + 1] + yi, p[xi + 1] + yi + 1

    g1 = grad(p[aa], xf, yf)
    g2 = grad(p[ba], xf - 1, yf)
    g3 = grad(p[ab], xf, yf - 1)
    g4 = grad(p[bb], xf - 1, yf - 1)

    return ((1 - u) * (1 - v) * g1 +
            u * (1 - v) * g2 +
            (1 - u) * v * g3 +
            u * v * g4)
"""


def fbm(x, y, frequency=2, octaves=6, persistence=0.5, lacunarity=2.0, seed=0):
    """Generate fractal Brownian motion at (x, y)."""
    value = np.zeros_like(x)
    amplitude = 0.5
    from perlin import generate_perlin_noise_2d
    for i in range(octaves):
        value += amplitude * generate_perlin_noise_2d(x * frequency, y * frequency, seed + i)
        amplitude *= persistence
        frequency *= lacunarity
    return value

def warp_heightmap(heightmap, shape, warp_strength=2.0, seed=0):
    """Warp the input heightmap to create a more organic look."""
    height, width = shape[0], shape[1]
    y, x = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    
    # Normalize coordinates to [0, 1] range
    x = x / width
    y = y / height
    
    # First warping
    qx = fbm(x + 0.0, y + 0.0, seed=seed)
    qy = fbm(x + 5.2, y + 1.3, seed=seed+1)
    
    # Second warping
    rx = fbm(x + 4.0 * qx + 1.7, y + 4.0 * qy + 9.2, seed=seed+2)
    ry = fbm(x + 4.0 * qx + 8.3, y + 4.0 * qy + 2.8, seed=seed+3)
    
    # Final warping
    warped_x = x + warp_strength * rx
    warped_y = y + warp_strength * ry
    
    # Clip coordinates to ensure they're within the valid range
    #warped_x = np.clip(warped_x * width, 0, width - 1)
    #warped_y = np.clip(warped_y * height, 0, height - 1)

    # Scale coordinates back to image size without clipping
    warped_x *= width
    warped_y *= height

    # Use cubic interpolation with "reflect" mode to sample the warped heightmap
    warped_heightmap = map_coordinates(heightmap, [warped_y, warped_x], order=3, 
                                       mode="reflect")
  

    return warped_heightmap

def tec_plate_map(shape, vor, plate_heights, sigma=30):
    # Create a height map based on the Voronoi diagram
    height_map = np.zeros(shape)
    # Iterate over all pixels in the height map
    for y in range(shape[1]):
        for x in range(shape[0]):
            # Find the nearest tectonic plate
            distances = np.sum((vor.points - [x, y])**2, axis=1)
            nearest_plate = np.argmin(distances)
            height_map[y, x] = plate_heights[nearest_plate]
    # Add more mountains at plate boundaries
    mountains = create_tectonic_mountains(vor, plate_heights, shape)
    height_map = height_map + mountains
    # Warp the terrain based on the height map
    #height_map = warp_terrain(height_map, warp_factor=0.9)
    # Apply Gaussian filter to smooth the height map
    height_map = gaussian_blur(height_map, sigma=30)
    return height_map


def plot_terrain(height_map):
    plt.figure(figsize=(12, 10))
    plt.imshow(height_map, cmap='terrain', interpolation=None)
    plt.colorbar(label='Elevation')
    plt.title('Tectonic Plate Terrain')
    plt.show()


if __name__ == '__main__':
    # Create a sample heightmap
    np.random.seed(42)
    shape = (256, 256)
    n_plates = 25
    size = 512
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    x, y = np.meshgrid(np.linspace(0, 1, size), np.linspace(0, 1, size))
    heightmap = fbm(x, y)
    ax2.imshow(heightmap, cmap='terrain')

    # 1) Create tectonic plates with mountains with varying heights
    print("Creating tectonic plates...")
    vor, plate_heights = create_tectonic_plates(shape, 15)

    # 2) Create terrain with mountains at plate boundaries
    print("Shaking things up...")
    heightmap = tec_plate_map(shape, vor, plate_heights)
    
    # Warp the heightmap
    warped_heightmap = warp_heightmap(heightmap, shape, warp_strength=0.25)
    
    # Plot the results
    #fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    #ax1.imshow(heightmap, cmap='terrain')
    #ax1.set_title("Original Heightmap")
    #ax2.imshow(warped_heightmap, cmap='terrain')
    #ax2.set_title("Warped Heightmap")
    plt.show()
