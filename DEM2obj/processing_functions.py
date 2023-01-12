from tifffile import TiffFile
import numpy as np

# also requires pip install imagecodecs but no import needed

def process_topo_tiff(input_file):
    ''' read the tif files produced by OpenTopography
    '''
    # requires very specific data format to work
    with TiffFile(input_file) as tif:
        topo_data = tif.pages[0]
        topo = topo_data.asarray()
        tags = {v.name:v.value for _,v in enumerate(topo_data.tags)}
        top_left = np.array([tags["ModelTiepointTag"][3],tags["ModelTiepointTag"][4]])
        n_lon = tags["ImageWidth"]
        n_lat = tags["ImageLength"]
        lon_width = n_lon * tags["ModelPixelScaleTag"][0]
        lat_width = n_lat * tags["ModelPixelScaleTag"][1]
        bottom_right = top_left + np.array([lon_width,-lat_width])
        min_lon,max_lat = top_left
        max_lon,min_lat = bottom_right
        lon_points = np.linspace(min_lon,max_lon,n_lon)
        lat_points = np.linspace(min_lat,max_lat,n_lat)
        topo = np.flipud(topo) # orient topography
    return {"topography":topo, "longitudes":lon_points, "latitudes":lat_points}

def height_matrix2obj(height_matrix,x_interval=1,y_interval=1,height_interval=1,object_name="TOPOGRAPHY"):
    ''' convert matrix of heights/altitudes into a very basic .obj format
    '''
    n_rows = len(height_matrix)
    const_cols = len(set([len(row) for row in height_matrix])) == 1
    if const_cols:
        n_cols = len(height_matrix[0])
    else:
        print("Error: non-constant number of columns for the rows of the matrix")

    vertices = ""
    for i,row in enumerate(height_matrix):
        for j,z in enumerate(row):
            coords = [i*x_interval,z*height_interval,j*y_interval]
            vertices += "\nv " + " ".join([str(c) for c in coords])

    faces = ""
    for i in range(n_rows-1):
        for j in range(n_cols-1):
            c = i*n_cols+1 + j
            face = [c,c+1,c+n_cols,c+1+n_cols]
            faces += "\nf " + " ".join([str(c) for c in face[:-1]])
            faces += "\nf " + " ".join([str(c) for c in face[1:]])

    obj = "o {name:s}{vertices:s}{faces:s}".format(name=object_name,vertices=vertices,faces=faces)
    return obj

def nearest_neighbour_avg_2d(matrix,n_iters=1,weight=0.5):
    ''' averaging the 8 nearest neighbours to a point and modifying the value at that point by a given weight to return a new value for the point.
    '''
    for _ in range(n_iters):
        for i in range(1,len(matrix)-1):
            for n in range(1,len(matrix[i])-1):
                try:
                    nearest_neighbours = (matrix[i-1][n-1] + matrix[i-1][n] + matrix[i-1][n+1] +
                                      matrix[i][n-1] + matrix[i][n+1] +
                                      matrix[i+1][n-1] + matrix[i+1][n] + matrix[i+1][n+1]
                                      )/8
                    matrix[i][n] = matrix[i][n] * (1-weight) + weight*nearest_neighbours
                except IndexError:
                    # reached end of row
                    pass
    return matrix
