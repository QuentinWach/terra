import numpy as np
import math
from tqdm import tqdm


def erode(heightmap, num_iterations=1, seed=None, erosion_radius=5, inertia=0.25, sediment_capacity_factor=20,
          min_sediment_capacity=0.01, erode_speed=0.7, deposit_speed=0.2, evaporate_speed=0.05, gravity=10,
          max_droplet_lifetime=30, initial_water_volume=2, initial_speed=1):
    """
    Simulates hydraulic erosion on a heightmap using independent water droplets.
    References:
    + https://ranmantaru.com/blog/2011/10/01/water-erosion-on-heightmap-terrain/
    + https://www.firespark.de/resources/downloads/implementation%20of%20a%20methode%20for%20hydraulic%20erosion.pdf
    + https://www.youtube.com/watch?v=eaXk97ujbPQ.

    Args:
    - heightmap (numpy.ndarray): The heightmap to erode.
    - num_iterations (int): The number of droplets to simulate.
    - seed (int): The seed for the random number generator.
    - erosion_radius (int): The radius of the erosion brush.
    - inertia (float): The inertia of the droplet.
    - sediment_capacity_factor (float): The factor that determines the sediment capacity 
      of the droplet.
    - min_sediment_capacity (float): The minimum sediment capacity of the droplet.
    - erode_speed (float): The speed at which the droplet erodes terrain.
    - deposit_speed (float): The speed at which the droplet deposits sediment.
    - evaporate_speed (float): The speed at which the droplet evaporates.
    - gravity (float): The gravity of the droplet.
    - max_droplet_lifetime (int): The maximum lifetime of the droplet.
    - initial_water_volume (float): The initial water volume of the droplet.
    - initial_speed (float): The initial speed of the droplet.

    Returns:
    - heightmap (numpy.ndarray): The eroded heightmap.
    - path_map (numpy.ndarray): The map of water droplet paths.    
    """
    mapSize = heightmap.shape[0]
    rng = np.random.default_rng(seed)
    erosion_brush_indices, erosion_brush_weights = initialize_brush_indices(mapSize, erosion_radius)
    heightmap = heightmap.copy()
    path_map = np.zeros_like(heightmap)

    for _ in tqdm(range(num_iterations)):
        pos_x = rng.uniform(0, mapSize - 1)
        pos_y = rng.uniform(0, mapSize - 1)
        dir_x, dir_y = 0, 0
        speed = initial_speed
        water = initial_water_volume
        sediment = 0

        '''     
        for lifetime in range(max_droplet_lifetime):
            node_x, node_y = int(pos_x), int(pos_y)
            droplet_index = node_y * mapSize + node_x
            cell_offset_x, cell_offset_y = pos_x - node_x, pos_y - node_y

            path_map[node_y, node_x] += 1

            height, gradient_x, gradient_y = calculate_height_and_gradient(heightmap, mapSize, pos_x, pos_y)

            dir_x = (dir_x * inertia - gradient_x * (1 - inertia))
            dir_y = (dir_y * inertia - gradient_y * (1 - inertia))
            
            length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
            if length != 0:
                dir_x /= length
                dir_y /= length
            
            pos_x += dir_x
            pos_y += dir_y

            # Implement periodic boundary conditions
            pos_x = pos_x % mapSize
            pos_y = pos_y % mapSize

            new_height, _, _ = calculate_height_and_gradient(heightmap, mapSize, pos_x, pos_y)
            delta_height = new_height - height

            sediment_capacity = max(-delta_height * speed * water * sediment_capacity_factor, min_sediment_capacity)

            """
            # CLAUDE! Please rethink this part of the code
            # so that the sediment is deposited in the correct location etc.          
            if sediment > sediment_capacity or delta_height > 0:
                amount_to_deposit = max(delta_height, sediment) if delta_height > 0 else (sediment - sediment_capacity) * deposit_speed
                sediment -= amount_to_deposit

                heightmap += deposit_to_node(heightmap, pos_x, pos_y, amount_to_deposit, mapSize)
            else:
                amount_to_erode = min((sediment_capacity - sediment) * erode_speed, -delta_height)

                for brush_point_index in range(len(erosion_brush_indices[droplet_index])):
                    node_index = erosion_brush_indices[droplet_index][brush_point_index]
                    weighed_erode_amount = amount_to_erode * erosion_brush_weights[droplet_index][brush_point_index]
                    delta_sediment = min(heightmap.flat[node_index], weighed_erode_amount)
                    heightmap.flat[node_index] -= delta_sediment
                    sediment += delta_sediment
            """

            if sediment > sediment_capacity or delta_height > 0:
                # If moving uphill or carrying too much sediment, deposit it
                amount_to_deposit = (delta_height > 0) * delta_height + (sediment - sediment_capacity) * deposit_speed
                amount_to_deposit = min(amount_to_deposit, sediment)
                sediment -= amount_to_deposit

                # Deposit sediment to the current cell and its neighbors
                heightmap = deposit_to_node(heightmap, pos_x, pos_y, amount_to_deposit, mapSize)
            else:
                # Erode the surface
                amount_to_erode = min((sediment_capacity - sediment) * erode_speed, -delta_height)
                
                # Distribute erosion across the brush
                for brush_point_index in range(len(erosion_brush_indices[droplet_index])):
                    node_index = erosion_brush_indices[droplet_index][brush_point_index]
                    weighed_erode_amount = amount_to_erode * erosion_brush_weights[droplet_index][brush_point_index]
                    delta_sediment = min(heightmap.flat[node_index], weighed_erode_amount)
                    heightmap.flat[node_index] -= delta_sediment
                    sediment += delta_sediment

            # Update water volume and sediment based on speed
            water = water * (1 - evaporate_speed)
            if speed != 0:
                sediment = min(sediment, sediment_capacity)

            #speed = math.sqrt(max(0, speed * speed + delta_height * gravity))
            #water *= (1 - evaporate_speed)'''

        for lifetime in range(max_droplet_lifetime):
            node_x, node_y = int(pos_x), int(pos_y)
            droplet_index = node_y * mapSize + node_x
            cell_offset_x, cell_offset_y = pos_x - node_x, pos_y - node_y

            path_map[node_y, node_x] += 1

            height, gradient_x, gradient_y = calculate_height_and_gradient(heightmap, mapSize, pos_x, pos_y)

            # Update droplet direction
            dir_x = (dir_x * inertia - gradient_x * (1 - inertia))
            dir_y = (dir_y * inertia - gradient_y * (1 - inertia))
            
            # Normalize direction
            length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
            if length != 0:
                dir_x /= length
                dir_y /= length
            
            # Move droplet
            new_pos_x = (pos_x + dir_x) % mapSize
            new_pos_y = (pos_y + dir_y) % mapSize

            new_height, _, _ = calculate_height_and_gradient(heightmap, mapSize, new_pos_x, new_pos_y)
            delta_height = new_height - height

            # Calculate sediment capacity
            sediment_capacity = max(-delta_height * speed * water * sediment_capacity_factor, min_sediment_capacity)

            # Erode or deposit
            if sediment > sediment_capacity or delta_height > 0:
                # Deposit sediment
                amount_to_deposit = (delta_height > 0) * delta_height + (sediment - sediment_capacity) * deposit_speed
                amount_to_deposit = min(amount_to_deposit, sediment)
                sediment -= amount_to_deposit

                # Deposit sediment to the current cell
                heightmap[node_y, node_x] += amount_to_deposit * (1 - cell_offset_x) * (1 - cell_offset_y)
                heightmap[node_y, (node_x + 1) % mapSize] += amount_to_deposit * cell_offset_x * (1 - cell_offset_y)
                heightmap[(node_y + 1) % mapSize, node_x] += amount_to_deposit * (1 - cell_offset_x) * cell_offset_y
                heightmap[(node_y + 1) % mapSize, (node_x + 1) % mapSize] += amount_to_deposit * cell_offset_x * cell_offset_y
            else:
                # Erode
                amount_to_erode = min((sediment_capacity - sediment) * erode_speed, -delta_height)
                
                # Erode from the current cell and its neighbors
                heightmap[node_y, node_x] -= amount_to_erode * (1 - cell_offset_x) * (1 - cell_offset_y)
                heightmap[node_y, (node_x + 1) % mapSize] -= amount_to_erode * cell_offset_x * (1 - cell_offset_y)
                heightmap[(node_y + 1) % mapSize, node_x] -= amount_to_erode * (1 - cell_offset_x) * cell_offset_y
                heightmap[(node_y + 1) % mapSize, (node_x + 1) % mapSize] -= amount_to_erode * cell_offset_x * cell_offset_y
                
                sediment += amount_to_erode

            # Update droplet's speed and water content
            speed = math.sqrt(max(0, speed * speed + delta_height * gravity))
            water *= (1 - evaporate_speed)

            # Move to the new position
            pos_x, pos_y = new_pos_x, new_pos_y

            # Stop simulating droplet if it's not moving or has no water
            if (dir_x == 0 and dir_y == 0) or water <= 0:
                break

    return heightmap, path_map


def deposit_to_node(heightmap, pos_x, pos_y, amount, mapSize):
    node_x, node_y = int(pos_x), int(pos_y)
    cell_offset_x, cell_offset_y = pos_x - node_x, pos_y - node_y

    # Use periodic boundary conditions for indexing
    heightmap[node_y % mapSize, node_x % mapSize] += amount * (1 - cell_offset_x) * (1 - cell_offset_y)
    heightmap[node_y % mapSize, (node_x + 1) % mapSize] += amount * cell_offset_x * (1 - cell_offset_y)
    heightmap[(node_y + 1) % mapSize, node_x % mapSize] += amount * (1 - cell_offset_x) * cell_offset_y
    heightmap[(node_y + 1) % mapSize, (node_x + 1) % mapSize] += amount * cell_offset_x * cell_offset_y

    return heightmap

def calculate_height_and_gradient(nodes, map_size, pos_x, pos_y):
    """
    Calculates the height and gradient at a given position on the heightmap.

    Args:
    - nodes (numpy.ndarray): The heightmap.
    - map_size (int): The size of the heightmap.
    - pos_x (float): The x-coordinate of the position.
    - pos_y (float): The y-coordinate of the position.
    """
    coord_x, coord_y = int(pos_x), int(pos_y)
    x, y = pos_x - coord_x, pos_y - coord_y
    # Get the heights of the four nodes of the cell
    node_index_nw = coord_y * map_size + coord_x
    height_nw = nodes.flat[node_index_nw]
    height_ne = nodes.flat[min(node_index_nw + 1, nodes.size - 1)]
    height_sw = nodes.flat[min(node_index_nw + map_size, nodes.size - 1)]
    height_se = nodes.flat[min(node_index_nw + map_size + 1, nodes.size - 1)]
    # Calculate the gradient
    gradient_x = (height_ne - height_nw) * (1 - y) + (height_se - height_sw) * y
    gradient_y = (height_sw - height_nw) * (1 - x) + (height_se - height_ne) * x
    # Calculate the height using bilinear interpolation
    height = height_nw * (1 - x) * (1 - y) + height_ne * x * (1 - y) + height_sw * (1 - x) * y + height_se * x * y
    return height, gradient_x, gradient_y

def initialize_brush_indices(map_size, radius):
    """
    This function initializes the indices and weights of the erosion brush 
    used to erode the terrain. The erosion brush is a circular area around
    the current droplet position that determines which nodes are eroded.

    Args:
    - map_size (int): The size of the heightmap.
    - radius (int): The radius of the erosion brush.
    """
    erosion_brush_indices = [[] for _ in range(map_size * map_size)]
    erosion_brush_weights = [[] for _ in range(map_size * map_size)]
    # Iterate over all nodes in the heightmap
    for i in range(map_size * map_size):
        centre_x, centre_y = i % map_size, i // map_size
        # Skip nodes near the border
        if centre_y <= radius or centre_y >= map_size - radius or centre_x <= radius + 1 or centre_x >= map_size - radius:
            weight_sum = 0
            add_index = 0
            x_offsets, y_offsets, weights = [], [], []
            # Iterate over the nodes in the erosion brush
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    sqr_dst = x * x + y * y
                    if sqr_dst < radius * radius:
                        coord_x, coord_y = centre_x + x, centre_y + y
                        # Check if the node is within the heightmap bounds
                        if 0 <= coord_x < map_size and 0 <= coord_y < map_size:
                            weight = 1 - math.sqrt(sqr_dst) / radius
                            weight_sum += weight
                            weights.append(weight)
                            x_offsets.append(x)
                            y_offsets.append(y)
                            add_index += 1
            # Normalize the weights
            for j in range(add_index):
                erosion_brush_indices[i].append((y_offsets[j] + centre_y) * map_size + x_offsets[j] + centre_x)
                erosion_brush_weights[i].append(weights[j] / weight_sum)
    return erosion_brush_indices, erosion_brush_weights

