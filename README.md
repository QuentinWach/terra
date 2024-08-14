<div align="center">

**Your digital terraforming toolkit.**
<picture>
  <img class=head src="docs/terra_header.png">
</picture>
Maintained by [Quentin Wach](https://www.x.com/QuentinWach).
<h3>

[Examples](#-examples) ▪ [Features](#-features)
</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/QuentinWach/meteor)](https://github.com/QuentinWach/meteor/stargazers)
[![GitHub latest commit](https://badgen.net/github/last-commit/QuentinWach/meteor)](https://github.com/QuentinWach/meteor/commits/main)
<!--[![Discord](https://img.shields.io/discord/1068976834382925865)](https://discord.gg/ZjZadyC7PK)-->
</div>

**Terra provides you with various physics simulations, heuristics, filters, presets, assets, neural networks and more to generate realistic terrains.**
Get started with:
```
pip install terra
```

|![alt text](docs/workflow.png)|
| :--: |
| Example workflow of creating a terrain. |

## 🎁 Examples
### 1. Map of a Continent with Various Biomes
| |
| :--: |
| **Figure 1. Map of a Continent with Various Biomes.** Tesselate the space using Voronoi cells. Create a heightmap using fractal Brownian noise. Create a temperature map using a slightly warped gradient with added Perlin noise, a precipation map created using Perlin noise. Classify the areas into biomes using a Whittaker diagram. Inspired by [Pvigier's Vagabond Map Generation](https://pvigier.github.io/2019/05/12/vagabond-map-generation.html). Generated height, texture, and material maps with [Terra](), rendered in [Blender]().|

```python
from terra import *
S = 42; np.random.seed(42)
X = 5000; Y = 5000
tesselation = relax(tesselate(space=(X, Y), density=0.001), iterate=3)
heightmap = fbn(X, Y, seed=S+1)
temperaturemap = lingrad(X, Y, start=(X/2,0,40), end=(X/2,Y, -40))
precipationmap = fbn(X, Y, seed=S+2)
height = errode(heightmap, temperaturemap, precipationmap, drops=X*Y//10, dropsize=X*Y//10)
texture = 
material =
export_to_png("example_1", height, texture, material)
```

<!--
---
### 2. The Great Mountain
| |
| :--: |
| **Figure 2. The Great Mountain.** |

```python
from terra import *
np.random.seed(42)
WIDTH = 500; HEIGHT = 500

tesselate

```
---
### 3. River Networks
| |
| :--: |
| **Figure 3. River Networks.** |

```python
from terra import *
np.random.seed(42)
WIDTH = 500; HEIGHT = 500

tesselate

```
|![alt text](docs/biomes.png)|
| :--: |
| **Climate Influence On Terrestrial Biome** by Navarras - Own work, CC0, https://commons.wikimedia.org/w/index.php?curid=61120531 |
-->

## 📝 Features
### Randomness `random`
+ [X] Normal Distribution
+ [X] Perlin Noise
+ [X] Fractal Perlin Noise
### Tesselation `tess`
+ [X] Voronoi Tesselation + Fortune's Algorithm for Even Spacing
+ [X] Whittaker diagram
+ [ ] Meshing to create 3D objects
### Rendering `render`
+ [X] Linear Gradient
+ [ ] Radial Gradient
+ [ ] Masks
+ [X] Colormaps
+ [ ] Materials (i.e. stone, sand, snow, water, grass, ...)
+ [ ] 2D Cartography Map Generator
+ [ ] Import (i.e. to import images to be used as height maps, filters, assets etc.)
+ [ ] 2D Map Export (i.e. to generate a 3D file and render it in Blender)
### 2D/3D Assets `assets`
+ [ ] Crators
+ [ ] Mountains
+ [ ] Rocks
+ [ ] Canions
+ [ ] Rivers
+ [ ] Lakes
### Simulation `sim`
+ [X] Stone Levels
+ [X] Brownian Mountains
+ [ ] TODO: Domain Warping
+ [ ] TODO: Hydraulic Terrain Erosion
+ [ ] Object Scattering (e.g. rocks)
+ [ ] River Networks
+ [ ] River Dynamics Simulation & Erosion
+ [ ] Snow Deposition

---
## 🤝🏻 Contribute
There is much to do! I think, making a cheap if not entirely free terrain generator with a great GUI would be nice. Leave your mark and add to this Python library! You know how it goes. You found a bug? Add an issue. Any ideas for improvement or feeling the need to add more features? Clone the repository, make the changes, and submit a pull request!