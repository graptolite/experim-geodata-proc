from scipy.interpolate import griddata
import numpy as np
import json

from osgb import wgs2gref
from processing_functions import process_topo_tiff,nearest_neighbour_avg_2d,height_matrix2obj

import config

tiff_data = process_topo_tiff(config.TIF_FILE)
lons = tiff_data["longitudes"]
lats = tiff_data["latitudes"]
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

SW_corner = wgs2gref(lats[0],lons[0],topo[0][0])
NE_corner = wgs2gref(lats[-1],lons[-1],topo[-1][-1])
n_lat_points = topo.shape[0]
n_lon_points = topo.shape[1]
dX = abs(SW_corner[1] - NE_corner[1])/n_lat_points
dY = abs(SW_corner[0] - NE_corner[0])/n_lon_points

x_interval = dX
y_interval = dY
z_interval = 1

# scale 1 = 1m

obj = height_matrix2obj(topo,x_interval,y_interval,z_interval)

with open(config.OUTPUT_OBJ_FILE,"w") as outfile:
    outfile.write(obj)

# Saving corners
with open(config.CORNERS_JSON_FILE,"w") as outfile:
    json.dump({"SW":SW_corner[:2],
               "NE":NE_corner[:2]},
              outfile)
