from PIL import Image
import numpy as np
import json

import config

img = np.asarray(Image.open(config.MAP_PNG))
NE = config.MAP_NE
SW = config.MAP_SW
dE = NE[0] - SW[0]
dN = NE[1] - SW[1]

px_northings,px_eastings,_ = img.shape

scale_N = dN/px_northings
scale_E = dE/px_eastings

eastings = np.arange(SW[0],NE[0],step=scale_E) + 1
northings = np.arange(SW[1],NE[1],step=scale_N) + 1

def ncimate(l,n=10):
    l = list(l)
    for i in reversed(range(len(l))):
        if i%n != 0:
            del l[i]
    return np.array(l).tolist()

n = config.KEEP_EVERY_N
eastings = ncimate(eastings,n)
northings = ncimate(northings,n)

img = ncimate(img,n)
for i in range(len(img)):
    img[i] = ncimate(img[i],n)

colours = []
for i in range(len(northings)):
    for j in range(len(eastings)):
        c = img[i][j]
        if c not in colours:
            colours.append(c)

keymap = {str(colours[i]):i for i in range(len(colours))}
cmap = {i:colours[i] for i in range(len(colours))}

for i in range(len(northings)):
    for j in range(len(eastings)):
        img[i][j] = keymap[str(img[i][j])]

data = {"e":eastings,
        "n":northings,
        "c":img,
        "cmap":cmap}

with open("lithology.json","w") as outfile:
    json.dump(data,outfile)
