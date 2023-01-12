from scipy.interpolate import griddata
import numpy as np
import json

from osgb import wgs2gref
from processing_functions import process_topo_tiff,nearest_neighbour_avg_2d

tiff_data = process_topo_tiff("output_COP30.tif")
lons = tiff_data["longitudes"]
lats = tiff_data["latitudes"]

WS = wgs2gref(lats[0],lons[0])
EN = wgs2gref(lats[-1],lons[-1])
eastings = [float(str(x)[1:]) for x in np.linspace(WS[0],EN[0],len(lons)).tolist()]
northings = [float(str(x)[1:]) for x in np.linspace(WS[1],EN[1],len(lats)).tolist()]

topo = tiff_data["topography"]

# find the first bad data col out of the first 3 columns
if topo[0][0] == topo[0][1]:
    # 0,0,1,2,2,3,4,4,5 ...
    offset = 0
elif topo[0][1] == topo[0][2]:
    # 0,1,1,2,3,3,4 ...
    offset = 2
else:
    # 0,1,2,2,3,4,4,5 ...
    offset = 1

# linear interpolating for every 3*n-1 point as points progress like 0,1,1,2,3,3,4,5,5,6,7,7,8 ...
for i in range(len(topo)):
    for n in range(1,int(len(topo[i])/3)):
        try:
            topo[i][3*n-offset] = (topo[i][3*n-offset-1] + topo[i][3*n-offset+1])/2
        except IndexError:
            # reached end of row
            pass

n_iters = 5
for _ in range(n_iters):
    i = 0
    for n in range(int(len(topo[i])/3)):
        topo[i][3*n-offset] = (topo[i][3*n-offset-1] + topo[i][3*n-offset+1] +
                                  topo[i+1][3*n-offset-1] + topo[i+1][3*n-offset] + topo[i+1][3*n-offset+1]
                                  )/5
    i = len(topo)-1
    for n in range(int(len(topo[i])/3)):
        topo[i][3*n-offset] = (topo[i-1][3*n-offset-1] + topo[i-1][3*n-offset] + topo[i-1][3*n-offset+1] +
                                  topo[i][3*n-offset-1] + topo[i][3*n-offset+1]
                                  )/5
    for i in range(1,len(topo)-1):
        for n in range(int(len(topo[i])/3)):
            try:
                topo[i][3*n-offset] = (topo[i-1][3*n-offset-1] + topo[i-1][3*n-offset] + topo[i-1][3*n-offset+1] +
                                  topo[i][3*n-offset-1] + topo[i][3*n-offset+1] +
                                  topo[i+1][3*n-offset-1] + topo[i+1][3*n-offset] + topo[i+1][3*n-offset+1]
                                  )/8
            except IndexError:
                # reached end of row
                pass

# all nearest neightboor averaging
topo = nearest_neighbour_avg_2d(topo,2,0.5)

data = {"e":eastings,
        "n":northings,
        "h":topo.tolist()}

with open("topography.json","w") as outfile:
    json.dump(data,outfile,indent=0)
