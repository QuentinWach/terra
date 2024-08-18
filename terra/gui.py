import pygame
import os
from PIL import Image
import numpy as np

# Initialize Pygame
pygame.init()

# Get the directory where the script is located
script_dir = os.path.dirname(__file__)
heightmap_path = os.path.join(script_dir, 'heightmap.png')

# Load the heightmap image and convert it to grayscale
heightmap_image = Image.open(heightmap_path).convert('L')
heightmap = np.array(heightmap_image)

# Set up the Pygame window
screen_size = heightmap.shape[1], heightmap.shape[0]
screen = pygame.display.set_mode(screen_size)

# Function to render the heightmap as a 2D image
def render_heightmap(screen, heightmap):
    heightmap_surface = pygame.surfarray.make_surface(np.stack((heightmap,) * 3, axis=-1))
    screen.blit(heightmap_surface, (0, 0))

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    render_heightmap(screen, heightmap)
    pygame.display.flip()

pygame.quit()
