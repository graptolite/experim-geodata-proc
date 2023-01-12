# REFERENCE FOR MATHS: A Guide to Coordinate Systems in Great Britain
# V3.6 © OS 2020 (original Copyright Ordnance Survey 2018)
# https://www.ordnancesurvey.co.uk/documents/resources/guide-coordinate-systems-great-britain.pdf

import string
import math
import numpy as np
from math import sin,cos,tan,atan
import decimal

def sigfig_rounding(n,sig_figs): ###requires decimal
    text_n = str(n)
    if "." in text_n:
        for a in range(0,len(text_n)):
            if text_n[a] == ".":
                decimal_pos=a
                break
        if decimal_pos <= sig_figs:
            n = n*10**(1+sig_figs-decimal_pos)
    new_text_n = str(n)[:sig_figs+1]
    try:
        n_new = round(decimal.Decimal(new_text_n)/10)
    except NameError:
        n_new = round(float(new_text_n)/10)
        print("Warning: decimal module not imported, float types will be used instead")
    return n_new

def time2decimal(deg_min_sec_array):
    dec_deg = deg_min_sec_array[0] + deg_min_sec_array[1]/60 + deg_min_sec_array[2]/60**2
    return dec_deg

def decimal2time(deg_dec):
    d = int(deg_dec)
    m = int(60*(deg_dec-d))
    s = 3600*(deg_dec-d-(m/60))
    return [d,m,s]

def radians_latlong(lat,long):
    try:
        if len(lat) > 1:
            lat = math.radians(time2decimal(lat))
        if len(long) > 1:
            long = math.radians(time2decimal(long))
    except TypeError:
        lat = math.radians(lat)
        long = math.radians(long)
    return lat,long

uk_ellipsoid_data = {
    "Airy1830" : {
        "semi_maj_axis" : 6377563.396,
        "semi_min_axis" : 6356256.909,
        "implementations" : ["OSGB36","National Grid"]
        },
    "Airy1830mod" : {
        "semi_maj_axis" : 6377340.189,
        "semi_min_axis" : 6356034.447,
        "implementations" : ["Ireland 65","Irish National Grid"]
        },
    "Hayford1909" : {
        "semi_maj_axis" : 6378388.000,
        "semi_min_axis" : 6356911.946,
        "implementations" : ["ED50","UTM"]
        },
    "WGS84" : {
        "semi_maj_axis" : 6378137.000,
        "semi_min_axis" : 6356752.3141,
        "implementations" : ["WGS84","ITRS","ETRS89"]
        }
    }

def polar2cartesian(lat,long,H,source="WGS84"):
    a = uk_ellipsoid_data[source]["semi_maj_axis"]
    b = uk_ellipsoid_data[source]["semi_min_axis"]
    epow2 = (a**2-b**2)/(a**2)
    v = a/(1-epow2*sin(lat)**2)**0.5
    x = (v+H)*cos(lat)*cos(long)
    y = -(v+H)*cos(lat)*sin(long)
    z = ((1-epow2)*v+H)*sin(lat)
    return x,y,z

def cartesian2polar(x,y,z,iter_range=1000,source="Airy1830"):
    a = uk_ellipsoid_data[source]["semi_maj_axis"]
    b = uk_ellipsoid_data[source]["semi_min_axis"]
    epow2 = (a**2-b**2)/(a**2)
    long = atan(y/x)
    p = (x**2+y**2)**0.5
    lat = atan(z/p*(1-epow2))
    for n in range(0,iter_range):
        v = a/(1-epow2*sin(lat)**2)**0.5
        lat = atan((z+epow2*v*sin(lat))/p)
    H = p/cos(lat) - v
    lat = math.degrees(lat)
    long = math.degrees(long)
    return lat,long,H

def latlong2grid(lat,long,source="Airy1830"):
    a = uk_ellipsoid_data[source]["semi_maj_axis"]
    b = uk_ellipsoid_data[source]["semi_min_axis"]
    epow2 = (a**2-b**2)/(a**2)

    F_0 = 0.9996012717
    lat_0 = math.radians(49)
    long_0 = math.radians(-2)
    E_0 = 400000
    N_0 = -100000

    n = (a-b)/(a+b)
    nu = a*F_0*(1-epow2*sin(lat)**2)**-0.5
    rho = a*F_0*(1-epow2)*(1-epow2*sin(lat)**2)**-1.5
    etapow2 = nu/rho-1

    latminus = lat-lat_0
    latplus = lat+lat_0
    M_0 = (1 + n + (5/4)*n**2 + (5/4)*n**3)*latminus
    M_1 = (3*n + 3*n**2 + (21/8)*n**3)*sin(latminus)*cos(latplus)
    M_2 = ((15/8)*n**2 + (15/8)*n**3)*sin(2*latminus)*cos(2*latplus)
    M_3 = ((35/24)*n**3)*sin(3*latminus)*cos(3*latplus)

    M = b*F_0*(M_0-M_1+M_2-M_3)

    I = M + N_0
    II = (nu/2)*sin(lat)*cos(lat)
    III = ((nu/24)*sin(lat)*cos(lat)**3)*((5-tan(lat)**2)+9*etapow2)
    IIIA = ((nu/720)*sin(lat)*cos(lat)**5)*((61-58*tan(lat)**2)+tan(lat)**4)
    IV = nu*cos(lat)
    V = ((nu/6)*cos(lat)**3)*((nu/rho)-tan(lat)**2)
    VI = ((nu/120)*cos(lat)**5)*(5-(18*tan(lat)**2)+(tan(lat)**4)+14*etapow2-58*etapow2*tan(lat)**2)

    longminus = long-long_0
    N = I + II*longminus**2 + III*longminus**4 + IIIA*longminus**6
    E = E_0 + IV*longminus + V*longminus**3 + VI*longminus**5
    return E,N

def wgs2osgb(x,y,z):
    system_in = np.array([[x],[y],[z]])
    s = 20.4894/10**6
    t_x = -446.448
    t_y = +125.157
    t_z = -542.060
    val_sectodeg = 3600
    r_x = math.radians(-0.1502/val_sectodeg)
    r_y = math.radians(-0.2470/val_sectodeg)
    r_z = math.radians(-0.8421/val_sectodeg)
    transformation_array = np.array([[t_x],[t_y],[t_z]])
    rotation_array = np.array([[1+s,-r_z,r_y],[r_z,1+s,-r_x],[-r_y,r_x,1+s]])
    ans = transformation_array + np.matmul(rotation_array,system_in)
    x = ans[0][0]
    y = ans[1][0]
    z = ans[2][0]
    return x,y,z

def gridify(x,y):
    ab_list = list(string.ascii_uppercase)
    del(ab_list[8])
    test_x = (x * 100)/500
    test_y = (y * 100)/500
    if math.ceil(test_x) == test_x:
        test_x = test_x + 1
    else:
        test_x = math.ceil(test_x)
    if math.ceil(test_y) == test_y:
        test_y = test_y + 1
    else:
        test_y = math.ceil(test_y)
    a = test_x + 2
    b = test_y + 1 ##account for false origin
    index_0 = 5*(5-b) + (a-1) #for 5 by 5 grid

    new_x = x*100 - (test_x-1)*500
    new_y = y*100 - (test_y-1)*500
    new_a = int(new_x/100) + 1
    new_b = int(new_y/100) + 1 ##account for human vs computer indexing methods
    index_1 = 5*(5-new_b) + (new_a-1) #for 5 by 5 grid

    letter = ab_list[int(index_0)] + ab_list[int(index_1)]

    return letter

def num2letter(Easting,Northing,figures=4,seperator=" "):
    E_sigfigs = len(str(Easting))
    N_sigfigs = len(str(Northing))
    min_sigfigs = min(E_sigfigs,N_sigfigs)

    try:
        if figures < 0:
            precision_index = 0
            print("Warning: grid reference figures cannot be negative. A letter grid will be returned.")
        elif int(figures/2) != figures/2:
            print("Warning: grid reference figures must be even, changing to one lower: " + str(figures) + " -> " + str(figures-1))
            precision_index = (figures - 1)/2
        else:
            precision_index = figures/2
    except OverflowError:
        precision_index = min_sigfigs
        print("Warning: requested grid reference figure too large. The maximum possible figure grid reference will be returned.")
    precision_index = int(precision_index)
    #print(str(Easting))
    #print(str(Northing))
    x_0 = int(str(Easting)[0])
    y_0 = int(str(Northing)[0])

    if int(min_sigfigs/2) != min_sigfigs/2:
        min_sigfigs = min_sigfigs - 1

    if min_sigfigs < precision_index:
        new_Easting = str(Easting).replace(".","")
        new_Northing = str(Northing).replace(".","")
        x_accu = new_Easting[1:min_sigfigs]
        y_accu = new_Northing[1:min_sigfigs]
        accu_ans = gridify(x_0,y_0) + seperator + str(x_accu) + seperator + str(y_accu)
        print("Warning: precision requested higher than precision of data. Result only useful as a "
              + str(min_sigfigs*2) + " figure grid reference: \n"
              + accu_ans)
    x_new = sigfig_rounding(Easting,precision_index+1)
    y_new = sigfig_rounding(Northing,precision_index+1)
    answer = gridify(x_0,y_0) + seperator + str(x_new)[1:] + seperator + str(y_new)[1:]
    return answer

def wgs2gref(lat,long,H=0):
    NEW_DATA = "WGS84"
    OLD_DATA = "Airy1830"
    ilat,ilong = radians_latlong(lat,long)
    x,y,z = polar2cartesian(ilat,ilong,H,source=NEW_DATA)
    y=-y
    nx,ny,nz = wgs2osgb(x,y,z)
    nlat,nlong,Hnew = cartesian2polar(nx,ny,nz,source=OLD_DATA)
    rlat,rlong = radians_latlong(nlat,nlong)
    a,b = latlong2grid(rlat,rlong,source=OLD_DATA)
    return a,b,Hnew

def wgs2letter_gref(lat,long,H=0,gref_figures=8):
    a,b,_ = wgs2gref(lat,long,H)
    grid_reference = num2letter(a,b,figures=gref_figures)
    return grid_reference
