from terra.tess import Voronoi
#random, tess, sim, render
# import terra as tr

# Define the parameters of the landscape.
S = 42
X = 5000; Y = 5000

# Generate a randomly tessellated grid of voronoi cells and relax it 
# so that the dots are more evenly distributed.
tesselation = Voronoi(X, Y, density=0.001, relax=3, seed=S)
tesselation.show()

# Generate a basic heightmap
#heightmap = random.fbn(X, Y, seed=S+1)

#temperaturemap = render.lingrad(X, Y, start=(X/2,0,40), end=(X/2,Y, -40))

#precipationmap = random.fbn(X, Y, seed=S+2)

#height = sim.errode(heightmap, temperaturemap, precipationmap, drops=X*Y//10, dropsize=X*Y//10)

#texture = ...

#material = ...

#render.export_to_png("example_1", height, texture, material)