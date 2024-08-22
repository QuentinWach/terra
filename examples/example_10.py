# Example usage:
from terra.sim import  pointy_perlin
from terra.render import export, terrain_cmap, import_map
from terra.fast_erosion import erode

heightmap = pointy_perlin(X=300, Y=300, scale=250)
export(heightmap, 'terrain.png', cmap='Greys_r')
export(heightmap, 'terrain_color.png', cmap=terrain_cmap())



eroded_heightmap = erode(heightmap, num_iterations=1000)
export(eroded_heightmap, 'erosion.png', cmap='Greys_r')
export(eroded_heightmap, "erosion_color.png", cmap=terrain_cmap())
#export(np.log1p(fluid), 'water_map.png', cmap='Blues')



export(eroded_heightmap-heightmap, 'diff.png', cmap='Greys_r')