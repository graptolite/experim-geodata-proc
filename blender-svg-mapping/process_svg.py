import re
import json
import numpy as np

import config

find_attrib = lambda attrib,xml : (lambda m : m.group(1) if m else "")(re.search(" {attrib:s}=\"(.*?)\"".format(attrib=attrib),xml))

with open(config.INPUT_SVG_FILE) as infile:
    svg = infile.read()

## Find offset required to align x,y of svg elements with the processed topography

with open(config.CORNER_DATA) as infile:
    corners = json.load(infile)
base_SW_corner = corners["SW"]
base_W,base_S = (float(str(base_SW_corner[i])[1:]) for i in range(len(base_SW_corner)))

circles = [m for m in re.findall("<circle[\s\S]*?/>",svg) if "gref" in m]
circle_locs = []
for circle in circles:
    gref,x,y = (find_attrib(attrib,circle) for attrib in ["gref","cx","cy"])
    E,N = gref.split(" ")
    circle_locs.append(np.array([[float(x),float(y)],[int(E),int(N)]]))

# recorded locations of SVG (rlSVG)
svg_NW = circle_locs[0]
svg_SE = circle_locs[1]
svg_S = svg_SE[1][1] * 10
svg_W = svg_NW[1][0] * 10
svg_E_px,svg_S_px = (svg_SE[0] * 10)
svg_W_px,svg_N_px = (svg_NW[0] * 10)

# offset of rlSVG's SW corner
base_dE = svg_W - base_W
base_dN = svg_S - base_S

# offset of rlSVG to equivalent SW corner in SVG from blender
# multiply by 1000 for km -> m
dE = (-svg_W_px/10**4 + base_dE) * 1000
dN = (svg_S_px/10**4 + base_dN) * 1000

translate = str((dN,dE)).replace(" ","")

primary_group = re.search("<g[\s\S]*?>",svg).group()
transform_re = re.search("transform=\".*?\"",primary_group)
if transform_re:
    transform = transform_re.group()
    new_primary_group = primary_group.replace(transform,"transform=\"translate{translate:s}\"".format(translate=translate))
else:
    new_primary_group = primary_group.replace("<g","<g\ntransform=\"translate{translate:s}\"".format(translate=translate))
svg = svg.replace(primary_group,new_primary_group)

## Remove unnecessary elements

svg = re.sub("<text>[\s\S]*?</text>","",svg)

circles = re.findall("<circle[\s\S]*?/>",svg)
for circle in circles:
    if "gref=" in circle:
        svg = svg.replace(circle,"")
    style = find_attrib("style",circle)
    fill = re.search("fill:#",style)
    if not fill:
        print(style)
        svg = svg.replace(circle,"")

with open(config.OUTPUT_SVG_FILE,"w") as outfile:
    outfile.write(svg)
