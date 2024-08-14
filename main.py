from terra.base import *
from terra.perlin import *
from terra.erosion import *
from terra.colormaps import *

if __name__ == '__main__':
    np.random.seed(42)
    shape = (256, 256)
    n_plates = 25
    fig, axs = plt.subplots(1, 5, figsize=(9, 2.5), dpi=150)

    # 1) Create tectonic plates with mountains with varying heights
    print("Creating tectonic plates...")
    vor, plate_heights = create_tectonic_plates(shape, n_plates)

    # 2) Create terrain with mountains at plate boundaries
    print("Shaking things up...")
    terrain_1 = tec_plate_map(shape, vor, plate_heights)
    axs[0].imshow(terrain_1, cmap="Greys_r")
    axs[0].set_title('Tectonic plates')

    # 3) Add perlin noise to the terrain
    print("Roughing it all up...")
    noise = generate_fractal_noise_2d(shape, (int(shape[0]/64), int(shape[0]/64)), octaves=4, persistence=0.5)
    terrain_2 = terrain_1 + 0.5*noise
    axs[1].imshow(terrain_2, cmap="Greys_r")
    axs[1].set_title('Perlin noise added')

    # 4) Warp terrain
    print("Warping terrain...")
    terrain_3 = warp_terrain(terrain_2, warp_factor=0.5)
    axs[2].imshow(terrain_3, cmap="Greys_r")
    axs[2].set_title('Terrain warped')
    
    # 5) Erode the terrain
    print("Splashing some water...")
    terrain_4, erosion_lines = erosion(terrain_3, droplets=20000)
    for line in erosion_lines: axs[3].plot(line[1], line[0], color='black', alpha=0.05)
    axs[3].set_aspect('equal'); axs[3].invert_yaxis()
    axs[3].set_xlim(0, shape[0]); axs[3].set_ylim(shape[1],0)
    axs[3].set_title('Erosion lines')
    axs[4].imshow(terrain_4, cmap="Greys_r")
    axs[4].set_title('Erosion applied')


    # Show everything
    plt.tight_layout()
    plt.show()

    # Show final 3D plot
    #plot3d_terrain(terrain_3)
