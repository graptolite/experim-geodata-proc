import json
import numpy as np

from scipy.interpolate import griddata
from scipy.spatial import KDTree

import matplotlib.pyplot as plt

# MUST BE 10 FIGURE GRID REFS
p_s = [[(63660,10510),(65800,10600)],
       ] # list of coordinates to get sections between
for n in range(len(p_s)):
    p0,p1 = p_s[n]

    with open("topography.json") as infile:
        topo_data = json.load(infile)

    with open("lithology.json") as infile:
        lithology_data = json.load(infile)

    n_points = 500
    ## extraodinarily inefficient - should strip the data into just a buffer zone around the section, not the whole dataset
    E_interp = np.linspace(p0[0],p1[0],n_points)
    N_interp = np.linspace(p0[1],p1[1],n_points)
    interp_coords = (E_interp,N_interp)
    two_d_distance = lambda p1,p2 : ((p2[1]-p1[1])**2 + (p2[0]-p1[0])**2)**0.5
    distances = [two_d_distance(p0,coord) for coord in zip(*interp_coords)]

    Es,Ns = np.meshgrid(topo_data["e"],topo_data["n"])
    heights = np.array(topo_data["h"])
    z = griddata((Es.ravel(),Ns.ravel()),heights.ravel(),interp_coords)

    cmap = lithology_data["cmap"]
    unit_colours = list(cmap.values())

    Exs,Nxs = np.meshgrid(lithology_data["e"],lithology_data["n"])
    lithologies = np.array(lithology_data["c"])

    interp_colour_coords = (E_interp,max(lithology_data["n"]) - (N_interp - min(lithology_data["n"]))) ## found this out using the lithology map plot; the map plot of lithologies doesn't require flipud whereas the topography does
    remapped_cmap = {str(i):x for i,x in enumerate(np.identity(len(cmap)))}
    c_tree = KDTree(list(remapped_cmap.values()))

    remapped_lithologies = np.array([[remapped_cmap[str(x)] for x in y] for y in lithologies])
    component_interp = []
    for i in range(len(remapped_lithologies[0][0])):
        component_interp_lithologies = remapped_lithologies[:,:,i]
        cs = griddata((Exs.ravel(),Nxs.ravel()),component_interp_lithologies.ravel(),interp_colour_coords)
        component_interp.append(cs)

    colours_interp = list(zip(*component_interp))
    for i,c in enumerate(colours_interp):
        c_idx = np.nonzero(c)[0] if sum(c) == 1 else c_tree.query([c])[1]
        try:
            colours_interp[i] = (lambda x : x if sum(x) else [0,0,0,255])(unit_colours[c_idx[0]])
        except IndexError:
            colours_interp[i] = [0,0,0,225]

    def plot_lith(colours_interp,save_file=None,solid_colour=True):
        fig,ax = plt.subplots()
        colours_interp = [c[:3] for c in colours_interp] if solid_colour else colours_interp
        prev_i = 0
        for i in range(len(colours_interp)-1):
            l0 = colours_interp[i]
            l1 = colours_interp[i+1]
            d_half = lambda i : (distances[i] + distances[i+1])/2
            z_half = lambda i : (z[i] + z[i+1])/2
            if l0 != l1:
                x = list(distances[prev_i:i]) + [d_half(i)]
                y = list(z[prev_i:i]) + [z_half(i)]
                if prev_i != 0:
                    x = [d_half(prev_i-1)] + x
                    y = [z_half(prev_i-1)] + y
                ax.plot(x,y,c=np.array(colours_interp[i])/255)
                prev_i = i+1
        ax.plot([d_half(prev_i-1)]+list(distances[prev_i:]),[z_half(prev_i-1)]+list(z[prev_i:]),c=np.array(colours_interp[i])/255)
        vmargin = 0.3
        try:
            z0 = min(z)
            z1 = max(z)
            dz = z1-z0
            ax.set_ylim(0,z1+vmargin*dz)
        except ValueError:
            ax.set_ylim(-100,1000)
        ax.set_xlabel("Distance along section /m")
        ax.set_ylabel("Altitude /m")
        ax.set_aspect("equal")
        if save_file:
            fig.savefig(save_file,bbox_inches="tight")
        return fig

    # with open("test_section.json","w") as outfile:
    #     json.dump({"data":colours_interp,"heights":z.tolist(),"locations":list(zip(E_interp.tolist(),N_interp.tolist()))},outfile)

    plt.figure()
    coloured_lithologies = np.array([[cmap[str(x)] for x in y] for y in lithologies])
    plt.imshow(coloured_lithologies,extent=[min(lithology_data["e"]),max(lithology_data["e"]),min(lithology_data["n"]),max(lithology_data["n"])])
    plt.plot(*list(zip(p0,p1)))
    plt.scatter(*list(zip(p0,p1)))
    plt.text(*p0,"p0")
    plt.text(*p1,"p1")
    plt.savefig("line_of_%s-%s.pdf" % (p0,p1),bbox_inches="tight")

    # plt.figure()
    # plt.imshow(np.flipud(heights),extent=[min(topo_data["e"]),max(topo_data["e"]),min(topo_data["n"]),max(topo_data["n"])])
    # plt.plot(*list(zip(p0,p1)))
    # plt.scatter(*list(zip(p0,p1)))
    # plt.text(*p0,"p0")
    # plt.text(*p1,"p1")

    fig = plot_lith(colours_interp)
    ax = fig.axes[0]
    ax.text(0,1.1,str(p0),ha="center",zorder=100,transform=ax.transAxes)
    ax.text(1,1.1,str(p1),ha="center",zorder=100,transform=ax.transAxes)
    fig.savefig("%s-%s.pdf" % (p0,p1),bbox_inches="tight")

    #    plt.show()
