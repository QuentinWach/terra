from terra.sim import  pointy_perlin, single_drop_erosion
from terra.render import export, normal_map, shadow_map, terrain_cmap

X = 300; Y = 300; S = 42
terrain_before = pointy_perlin(X, Y, scale=100, octaves=4, seed=S)
terrain = single_drop_erosion(terrain_before, iterations=300)
export(terrain, "hill_height.png", cmap="Greys_r")
export(terrain, "hill_coloured.png", cmap=terrain_cmap())

normal_map = normal_map(terrain) # calculate the normals
shadow_map = shadow_map(normal_map) # calculate the shadows
erosion_map = terrain_before - terrain # calculate the erosion map
export(erosion_map, "erosion_map.png", cmap="Greys_r")


# solar-globe dynamics
# globe kinematics (size, density, gravity, rotation, heat, etc.)
# tectonics (plates, faults, mountains, volcanoes, earthquakes, etc.)
# climate (temperature, precipitation, wind, etc.)
# hydrology and wind (erosion rivers, lakes, oceans, currents, etc.)

