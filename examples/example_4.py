from terra.sim import hill
from terra.render import export, normal_map, shadow_map, terrain_cmap

terrain = hill(500, 500) # create the island heightmap
normal_map = normal_map(terrain) # calculate the normals
shadow_map = shadow_map(normal_map) # calculate the shadows
export(terrain, "hill.png", cmap="Greys_r")
export(terrain, "hill_coloured.png", cmap=terrain_cmap())
export(normal_map, "hill_normal.png", cmap="viridis")
export(shadow_map, "hill_shadow.png", cmap="gray")