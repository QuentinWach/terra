import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
# Define the RGB values for each biome and normalize them to [0, 1]
biome_colors = {
    1: (148/255, 168/255, 174/255),  # Tundra
    2: (147/255, 127/255, 44/255),   # Temperate grassland/cold desert
    3: (201/255, 114/255, 52/255),   # Subtropical desert
    4: (91/255, 144/255, 81/255),    # Boreal forest
    5: (180/255, 125/255, 1/255),    # Woodland/shrubland
    6: (40/255, 138/255, 161/255),   # Temperate seasonal forest
    7: (152/255, 166/255, 34/255),   # Tropical seasonal forest
    8: (1/255, 82/255, 44/255),      # Tropical rainforest
    9: (3/255, 83/255, 109/255)      # Temperate rainforest
}
# Create a list of colors sorted by biome ID
sorted_biome_colors = [biome_colors[i] for i in sorted(biome_colors.keys())]
# Create the colormap
biome_cmap = ListedColormap(sorted_biome_colors)

# Example usage: Visualize the colormap
plt.figure(figsize=(8, 2))
plt.imshow([list(range(len(sorted_biome_colors)))], cmap=biome_cmap, aspect='auto')

# Label the axis with the names of the biomes
plt.yticks([])
plt.xticks(range(len(sorted_biome_colors)), sorted(biome_colors.keys()), rotation=0)

plt.title('Biome Types')
plt.tight_layout()
plt.show()