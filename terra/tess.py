import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi as ScipyVoronoi, voronoi_plot_2d

def roundup(x, n):
    return math.ceil(x / n) * n

class Voronoi:
    """
    A class to create and manipulate Voronoi diagrams.

    Attributes:
    x, y: int - the dimensions of the grid
    density: float - the density of the points in the grid
    relax: int - the number of iterations to space out the points more evenly
    seed: int - the seed for the random number generator
    """
    def __init__(self, x=500, y=500, density=0.01, relax=0, seed=None):
        np.random.seed(seed)
        self.x = x
        self.y = y
        self.density = density
        self.n_points = int(roundup(x * y * density, 1))
        self.points = np.random.rand(self.n_points, 2) * np.array([self.x, self.y])
        self._update_voronoi()
        
        if relax > 0:
            self.relax(iterations=relax)

    def _update_voronoi(self):
        """Update the Voronoi diagram based on current points."""
        self.vor = ScipyVoronoi(self.points)

    def relax(self, iterations=1):
        """
        Use Lloyd's relaxation algorithm to space out the points more evenly.
        
        Args:
        iterations: int - number of relaxation iterations
        """
        for _ in range(iterations):
            new_points = np.zeros_like(self.points)
            for i, point in enumerate(self.points):
                region = self.vor.regions[self.vor.point_region[i]]
                if -1 not in region:
                    new_points[i] = np.mean([self.vor.vertices[j] for j in region], axis=0)
                else:
                    new_points[i] = point
            self.points = new_points
            self._update_voronoi()

    def show(self, figsize=(10, 10)):
        """
        Display the Voronoi diagram with matplotlib.
        
        Args:
        figsize: tuple - size of the figure (width, height)
        """
        fig, ax = plt.subplots(figsize=figsize)
        voronoi_plot_2d(self.vor, ax=ax, show_vertices=False, line_colors='k', 
                        line_width=2, line_alpha=0.6, point_size=0)
        ax.set_xlim(0, self.x)
        ax.set_ylim(0, self.y)
        plt.show()

    def add_points(self, new_points):
        """
        Add new points to the Voronoi diagram.
        
        Args:
        new_points: array-like - new points to add
        """
        self.points = np.vstack([self.points, new_points])
        self.n_points = len(self.points)
        self._update_voronoi()

    def remove_points(self, indices):
        """
        Remove points from the Voronoi diagram by their indices.
        
        Args:
        indices: array-like - indices of points to remove
        """
        self.points = np.delete(self.points, indices, axis=0)
        self.n_points = len(self.points)
        self._update_voronoi()

    def get_cell_areas(self):
        """
        Calculate the areas of all Voronoi cells.
        
        Returns:
        numpy array of cell areas
        """
        areas = []
        for region in self.vor.regions:
            if not -1 in region:
                polygon = [self.vor.vertices[i] for i in region]
                area = self._polygon_area(polygon)
                areas.append(area)
        return np.array(areas)

    def _polygon_area(self, vertices):
        """Helper method to calculate the area of a polygon."""
        x = [vertex[0] for vertex in vertices]
        y = [vertex[1] for vertex in vertices]
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    def get_neighbor_indices(self):
        """
        Get the indices of neighboring points for each point.
        
        Returns:
        list of lists, where each sublist contains the indices of neighboring points
        """
        return [self.vor.regions[self.vor.point_region[i]] for i in range(self.n_points)]

    def save(self, filename):
        """
        Save the Voronoi diagram points to a file.
        
        Args:
        filename: str - name of the file to save the points
        """
        np.savetxt(filename, self.points, delimiter=',')

    @classmethod
    def load(cls, filename, x, y):
        """
        Load Voronoi diagram points from a file.
        
        Args:
        filename: str - name of the file to load the points from
        x, y: int - the dimensions of the grid

        Returns:
        VoronoiDiagram object
        """
        points = np.loadtxt(filename, delimiter=',')
        voronoi = cls(x, y, density=len(points) / (x * y))
        voronoi.points = points
        voronoi._update_voronoi()
        return voronoi