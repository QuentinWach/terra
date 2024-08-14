from scipy.ndimage import gaussian_filter
import numpy as np

def gaussian_blur(height_map, sigma=30):
    """
    Apply a Gaussian blur to a height map.

    Args:
    height_map (np.ndarray): A 2D array of shape (y, x) representing the height map.
    sigma (float): Standard deviation of the Gaussian kernel.
    """
    return gaussian_filter(height_map, sigma=sigma)

def lingrad(x, y, start, end):
    """
    Generate a linear gradient height map.
    
    Args:
    x (int): Width of the height map.
    y (int): Height of the height map.
    start (tuple): (x, y, height) of the start point.
    end (tuple): (x, y, height) of the end point.
    
    Returns:
    np.ndarray: A 2D array of shape (y, x) representing the height map.
    """
    # Create a grid of coordinates
    xv, yv = np.meshgrid(np.arange(x), np.arange(y))
    # Calculate the difference in coordinates and height
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dh = end[2] - start[2]
    # Calculate the distances from the start point
    dist_from_start_x = xv - start[0]
    dist_from_start_y = yv - start[1]
    # Calculate the projection of each point onto the gradient direction
    projection = (dist_from_start_x * dx + dist_from_start_y * dy) / (dx**2 + dy**2)
    # Interpolate the height at each point
    height_map = start[2] + projection * dh
    # Clamp the height map to the range [start[2], end[2]]
    height_map = np.clip(height_map, min(start[2], end[2]), max(start[2], end[2]))
    return height_map
