"""
This code was more or less copied from:
https://github.com/keepitwiel/hydraulic-erosion-simulator
Original paper:
https://hal.inria.fr/inria-00402079/document
Original implementation:
https://github.com/Huw-man/Interactive-Erosion-Simulator-on-GPU
Other implementation:
https://github.com/karhu/terrain-erosion/blob/master/Simulation/FluidSimulation.cpp
"""
import numpy as np
from numba import njit, prange
from tqdm import tqdm
from terra.randd import perlin

@njit
def _update(z, h, r, s, fL, fR, fT, fB, dt=0.1, k_c=0.1, k_s=0.1, k_d=0.1, k_e=0.003, erosion_flag=True):
    """
    Updates the terrain height, water height, suspended sediment amount,
    and other fields for one time step.

    Args:
    - z: 2D numpy array representing the terrain height
    - h: 2D numpy array representing the water height 
    - r: 2D numpy array representing the rainfall
    - s: 2D numpy array representing the suspended sediment amount
    - fL: 2D numpy array representing the flux towards the left neighbor
    - fR: 2D numpy array representing the flux towards the right neighbor
    - fT: 2D numpy array representing the flux towards the top neighbor
    - fB: 2D numpy array representing the flux towards the bottom neighbor
    - dt: time step
    - k_c: sediment capacity constant
    - k_s: dissolving constant
    - k_d: deposition constant
    - k_e: evaporation constant
    - erosion_flag: flag to enable/disable erosion
    """
    #####################################################
    # Simulation constants
    A_PIPE = 0.6  # virtual pipe cross section
    G = 9.81      # gravitational acceleration
    L_PIPE = 1    # virtual pipe length
    LX = 1        # horizontal distance between grid points
    LY = 1        # vertical distance between grid points
    #####################################################
    # get dimensions
    n_x = z.shape[1]
    n_y = z.shape[0]
    H = z + h  # surface height
    # auxiliary arrays - should be buffers to speed up things?
    h2 = np.zeros_like(z)
    u = np.zeros_like(z)
    v = np.zeros_like(z)
    s1 = np.zeros_like(z)
    g = np.zeros_like(z)
    #####################################################
    # the following section titles and equation numbers #
    # were taken from the original paper.               #
    # the implementation here differs somewhat from the #
    # original code.                                    #
    # ------------------------------------------------- #
    # Practical notes:                                  #
    # 1) We follow numpy matrix coordinate convention.  #
    # j = horizontal coordinate. low/high = left/right  #
    # i = vertical coordinate. low/high = top/bottom    #
    #                                                   #
    # 2) We don't update the edge tiles for most        #
    # fields.                                           #
    #####################################################
    # 3.1 Water Increment
    # ========================================================================
    h1 = h + dt * r  # rainfall increment (eqn 1)
    # we put this in a separate loop because we need all
    # fluxes calculated before proceeding with calculating
    # water and sediment transportation
    for i in range(1, n_x - 1):
        for j in range(1, n_y - 1):

            # 3.2.1 outflow flux computation
            # ================================================================
            # eqn 3
            # ----------------------------------------------------------------
            # difference in height between tile (j, i) and its neighbors.
            # this drives the initial flux calculations
            dhL = H[j, i] - H[j, i - 1]
            dhR = H[j, i] - H[j, i + 1]
            dhT = H[j, i] - H[j - 1, i]
            dhB = H[j, i] - H[j + 1, i]
            # eqn 2
            # ----------------------------------------------------------------
            # update flux from tile (j, i) to each neighbor.
            # we don't allow negative flux
            flux_factor = dt * A_PIPE / L_PIPE * G
            fL[j, i] = max(0, fL[j, i] + dhL * flux_factor)
            fR[j, i] = max(0, fR[j, i] + dhR * flux_factor)
            fT[j, i] = max(0, fT[j, i] + dhT * flux_factor)
            fB[j, i] = max(0, fB[j, i] + dhB * flux_factor)
            # eqn 4
            # ----------------------------------------------------------------
            # calculate adjustment factor.
            # this is to make sure that the outflow does not lead to a
            # negative water level in the tile.
            sum_f = fL[j, i] + fR[j, i] + fT[j, i] + fB[j, i]
            if sum_f > 0:
                adjustment_factor = min(1, h1[j, i] * LX * LY / (sum_f * dt))
                # eqn 5. We only need to calculate this step when sum_f > 0
                # ------------------------------------------------------------
                fL[j, i] *= adjustment_factor
                fR[j, i] *= adjustment_factor
                fT[j, i] *= adjustment_factor
                fB[j, i] *= adjustment_factor

    # setting edge fluxes to 0 to prevent leaking.
    # TODO: find out if this needs to be done before eqn 5!
    fL[0, :] = 0
    fR[-1, :] = 0
    fT[:, 0] = 0
    fB[:, -1] = 0
    for i in range(1, n_x - 1):
        for j in range(1, n_y - 1):
            # 3.2.2 water surface and velocity field update
            # ================================================================
            # flux coming into (j, i)
            sum_f_in = (
                fR[j, i - 1] + fT[j + 1, i] + fL[j, i + 1] + fB[j - 1, i]
            )
            # flux going out of (j, i)
            sum_f_out = (
                fL[j, i] + fR[j, i] + fT[j, i] + fB[j, i]
            )
            # eqn 6: delta volume
            # ----------------------------------------------------------------
            dvol = dt * (sum_f_in - sum_f_out)
            # eqn 7: update water height
            # ----------------------------------------------------------------
            dh = dvol / (LX * LY)
            h2[j, i] = h1[j, i] + dh
            # mean water level between rainfall and outflow.
            # TODO: do we really need mean? can't we just use h2?
            h_mean = h1[j, i] + 0.5 * dh
            if h_mean > 0:
                # we only calculate velocity if there is water, otherwise
                # velocity should be 0
                # eqn 8
                # ----------------------------------------------------------------
                dwx = fR[j, i - 1] - fL[j, i] + fR[j, i] - fL[j, i + 1]
                dwy = fB[j - 1, i] - fT[j, i] + fB[j, i] - fT[j + 1, i]
                # eqn 9
                # ----------------------------------------------------------------
                u[j, i] = dwx / LY / h_mean
                v[j, i] = dwy / LX / h_mean
            else:
                u[j, i] = 0
                v[j, i] = 0
            if erosion_flag:
                # 3.3 erosion and deposition
                # ================================================================
                # first, calculate (approximate) gradient
                dzdy = 0.5 * (z[j + 1, i] - z[j - 1, i])
                dzdx = 0.5 * (z[j, i + 1] - z[j, i - 1])
                # dot product will give the grade (slope magnitude per unit length)
                # in the direction of the gradient
                g[j, i] = min(max(dzdx**2 + dzdy**2, -10), 10)
                # Now we want to calculate the sine of the local tilt angle.
                # this follows from Pythagoras:
                sin_local_tilt = np.sqrt(g[j, i] / (g[j, i] + 1))
                # eqn 10
                # ----------------------------------------------------------------
                # calculate sediment transport capacity C
                # we use a minimum of 0.15 for the slope to keep things "interesting"
                capacity = k_c * max(0.15, sin_local_tilt) * np.sqrt(u[j, i] ** 2 + v[j, i] ** 2)
                if capacity > s[j, i]:
                    # if capacity exceeds suspended sediment,
                    # erode soil and add it to sediment
                    delta_soil = min(0.1, k_s * (capacity - s[j, i]))
                    # eqn 11a
                    z[j, i] -= delta_soil
                    # eqn 11b
                    s1[j, i] = max(0, s[j, i] + delta_soil)
                else:
                    # if suspended sediment exceeds capacity,
                    # deposit sediment and substract it from sediment.
                    # TODO: this can be probably be simplified so we don't need a conditional!
                    # -> would only work if K_S == K_D
                    delta_soil = min(0.1, k_d * (s[j, i] - capacity))
                    # eqn 12a
                    z[j, i] += delta_soil
                    # eqn 12b
                    s1[j, i] = max(0, s[j, i] - delta_soil)

                # 3.4 sediment transportation
                # ================================================================
                # now that we've absorbed or deposited the suspended sediment,
                # we can transport it.
                # eqn 14
                # ----------------------------------------------------------------
                # in short, s[j, i] = s1[j - u[j, i] * dt, i - v[j, i] * dt]
                # calculate coordinates "from where the sediment is coming from".
                # the sediment at that coordinate is the new value for
                # sediment at (j, i).
                j1 = j - dt * u[j, i]
                i1 = i - dt * v[j, i]
                # because j1 and i1 are not integer, we need to interpolate.
                # to do so, we calculate weights from j1, i1 to nearest neighbors.
                #
                #  j_lb, --------------- j_lb,
                #  i_lb                  i_ub
                #   |                     |
                #   |                     |
                #   |   x     j1, i1      |
                #   | ----- o             |
                #   |       |             |
                #   |       |             |
                #   |       | y           |
                #   |       |             |
                #  j_ub,    |            j_ub,
                #  i_lb  --------------- i_ub
                #
                # calculte corner coordinates
                j_lb = max(0, min(int(j1), n_x - 1))
                j_ub = j_lb + 1
                i_lb = max(0, min(int(i1), n_y - 1))
                i_ub = i_lb + 1
                # calculate coordinates for interpolation
                x = j1 % 1
                y = i1 % 1
                # simple bilinear interpolation
                s[j, i] = min(
                    1.0,
                    (
                        s1[j_lb, i_lb] * (1 - x) * (1 - y) +
                        s1[j_ub, i_lb] * x * (1 - y) +
                        s1[j_lb, i_ub] * (1 - x) * y +
                        s1[j_ub, i_ub] * x * y
                    )
                )
                # 3.5 evaporation [OLD]
                # ================================================================
                # eqn 15
                # ----------------------------------------------------------------
                h[j, i] = h2[j, i] * (1 - k_e * dt)
                # 3.5 evaporation [NEW]
                # ================================================================
                # Instead of evaporating proportionally to the amount of water
                # in a tile, it's probably more realistic to evaporate at a constant
                # rate. After all, evaporation only occurs at the surface, and
                # having more water below the surface doesn't increase evaporation.
                # In the future, we should also take into account air humidity and
                # air/water temperature.
                #h[j, i] = max(0, h2[j, i] - k_e * dt)
        
            # Not in original paper, it is however present in the code:
            # 3.6 Heuristic to remove sharp peaks/valleys
            # ================================================================
            # ... TODO: implement

    return z, h, s, fL, fR, fT, fB, u, v, g

def erode(heightmap, num_iterations=2, dt=0.1, k_c=0.1, k_s=0.1, k_d=0.1, 
          k_e=0.003, erosion_flag=True, R=5, num_droplets=10):
    """
    Hydraulically erode a heightmap.
    
    Args:
    - heightmap: 2D numpy array representing the terrain height
    - num_iterations: number of erosion iterations to perform
    - dt: time step for each iteration
    - k_c: sediment capacity constant
    - k_s: dissolving constant
    - k_d: deposition constant
    - k_e: evaporation constant
    - erosion_flag: flag to enable/disable erosion
    
    Returns:
    - eroded_heightmap: 2D numpy array of the eroded terrain
    """
    # import and normalize the heightmap
    z = heightmap.copy()
    z = (z - z.min()) / (z.max() - z.min())
    x, y = z.shape

    h = np.zeros_like(z)  # water height
    s = np.zeros_like(z)  # suspended sediment amount
    fL = np.zeros_like(z)  # flux towards left neighbor
    fR = np.zeros_like(z)  # flux towards right neighbor
    fT = np.zeros_like(z)  # flux towards top neighbor
    fB = np.zeros_like(z)  # flux towards bottom neighbor
    
    saved_z = []
    saved_h = []
    saved_r = []


    # Add a erosion source over the mountains
    #r = 0.04*z.copy() + 0.01*perlin(x, y, scale=0.5*max(x, y), seed=0)
    # When eroding the entire terrain, randomly change the rainfall pattern.
    # This helps a lot against hole formation.

    # Precompute rainfall patterns
    r_base = 0.04 * z + 0.01 * perlin(x, y, scale=0.5*max(x, y), seed=0)
    r_patterns = [rotate_array(r_base, k) for k in range(4)]

    # Precompute droplets
    droplet_positions, droplet_mask = precompute_droplets((x, y), num_droplets, R)

    for i in tqdm(range(num_iterations)):

        # Rotate rainfall pattern
        r = r_patterns[i % 4]

        # Add random water droplets
        #h = add_water_droplets(h, droplet_positions, droplet_mask)

        saved_h.append(h.copy())
        saved_r.append(r.copy())
        saved_z.append(z.copy())
        z, h, s, fL, fR, fT, fB, _, _, _ = _update(z, h, r, s, fL, fR, fT, fB, dt, 
                                                   k_c=k_c, k_s=k_s, k_d=k_d, k_e=k_e, erosion_flag=erosion_flag)
        if i % 100 == 0:
            print(f"Iteration {i}: Max height change: {np.max(np.abs(z - heightmap))}")

    # Normalize and convert back to image
    #eroded_heightmap = (eroded_heightmap - eroded_heightmap.min()) / (eroded_heightmap.max() - eroded_heightmap.min())
    #eroded_img = Image.fromarray((eroded_heightmap * 255).astype(np.uint8))
    
    return saved_z, saved_h, s, saved_r

@njit(parallel=True)
def add_water_droplets(h, droplet_positions, droplet_mask):
    for i in prange(len(droplet_positions)):
        cx, cy = droplet_positions[i]
        h[cx:cx+droplet_mask.shape[0], cy:cy+droplet_mask.shape[1]] += droplet_mask
    return h

@njit
def rotate_array(arr, k):
    return np.rot90(arr, k)

def precompute_droplets(shape, num_droplets, R):
    x, y = shape
    droplet_positions = np.array([(np.random.randint(0, x-2*R), np.random.randint(0, y-2*R)) for _ in range(num_droplets)])
    y_grid, x_grid = np.ogrid[-R:R+1, -R:R+1]
    droplet_mask = np.where(x_grid**2 + y_grid**2 <= R**2, 0.1, 0).astype(np.float32)
    return droplet_positions, droplet_mask