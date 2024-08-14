import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

class Voronoi:
    """
    x, y: int - the dimensions of the grid
    density: float - the density of the points in the grid
    relax: int - the number of iterations to space out the points more evenly
    """
    def __init__(self, x=500, y=500, density=0.01, relax=3, seed=None):
        np.random.seed(seed)
        self.x = x
        self.y = y
        self.density = density
        self.n_points = x * y * density
        self.points = np.random.rand(self.n_points, 2) * np.array([self.x, self.y])
        self.vor = Voronoi(self.points)
        if relax > 0:
            for _ in range(relax):
                self.points = self.relax(self.points)

    def relax(self, points):
        """
        Use 
        """
        new_points = np.zeros_like(points)
        for i, point in enumerate(points):
            region = self.vor.regions[self.vor.point_region[i]]
            if -1 in region:
                new_points[i] = point
            else:
                new_points[i] = np.mean([self.vor.vertices[j] for j in region], axis=0)
        return new_points
    
    def show(self):
        _, ax = plt.subplots(figsize=(10, 10))
        voronoi_plot_2d(self.vor, ax=ax, show_vertices=False, line_colors='k', line_width=2, line_alpha=0.6, point_size=0)
        ax.set_xlim(0, self.x)
        ax.set_ylim(0, self.y)
        plt.show()