Transforming an SVG of a map of known scale with associated .obj DEM (created by `../DEM2obj/process_tif_create_obj_and_json.py`) so that it is suitable for import into Blender such that the map and DEM line up. Also projecting the map onto the DEM surface.

# Manual Resizing and Rotating
Within the map SVG file, there should be two circles placed at the north-west and south-east corners just outside the bounding rectangle than encloses the map. These two circles must have their locations within the OSGB36 coordinate system recorded in a "gref" attribute. For example, for a circle whose centre is at (6100,0800) may have an XML that looks like this (cx and cy refers to its position relative to the document's coordinate system and should be automatically generated when the circle is created; style, id and r are arbitrary).
```
<circle
       style="display:inline;fill:#000000;fill-opacity:1;stroke-width:1676.68;stroke-linejoin:bevel;stroke-dasharray:1676.68, 1676.68"
       id="61-08"
       gref="6100 800"
       cx="1011320.4"
       cy="987922.75"
       r="10813.43"/>
```

Select all of the mapped units as well as the corner circles and copy them over to a new SVG file, which will be the working SVG file. Save this working SVG file as a plain SVG. Group everything and change the document units to inches (or any other unit with large intervals between integer). Assuming mapping was done on a 1:10k scale, scale the group up (with aspect ratio locked) by 10 000. Rotate the group 90 degrees clockwise and then ungroup. For these later steps it is likely nothing will be visible.

Make sure the working SVG filename is set to the `INPUT_SVG_FILE` variable in `config.py`.

# Translation
To find the necessary transform that will line up the SVG map with the .obj DEM when imported into Blender, run `process_svg.py`. Assuming `../DEM2obj/process_tif_create_obj_and_json.py` had been previously run to create the corners data file alongside the .obj DEM, this will apply  the necessary translation as well as remove all text and circles (comment these out if this is not desired behaviour) and save the output to the file specified by `OUTPUT_SVG_FILE` in `config.py`.

# Projecting onto Topography in Blender
Import the SVG into the Blender project - it should line up with the topography object.

Note: in order for the print output to be visible, it must be launched from a system console/command prompt.

A separate python script saved in the Blender file is run to project the map onto the topography.

```python
# Tested on Blender 2.83 LTS, scipy 1.7.3
# code yet to be refactored
import bpy
import numpy as np
import bmesh

site_group = "boundaries.svg.001" # replace this with the name of the *group* (of objects) that represents the import of output_svg_file in config.py

def deg2rad(deg):
    return deg/360 * 2 * np.pi

topography_object = bpy.data.objects["TOPOGRAPHY"] # replace TOPOGRAPHY with the name of the topography *object*

for item in bpy.data.collections[site_group].all_objects.values():
    if item.type == "CURVE" and "path" in item.name:
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except RuntimeError:
            pass
        bpy.ops.object.select_all(action='DESELECT')

        bpy.context.view_layer.objects.active = item
        sel = bpy.context.selected_objects
        act_obj = bpy.context.active_object
        act_obj.select_set(True)

        print("\n" + act_obj.name + " Started")

        print("\tConverting to mesh")
        bpy.ops.object.convert(target='MESH')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.dissolve_limited(angle_limit=deg2rad(1))
        bpy.ops.mesh.quads_convert_to_tris(quad_method="BEAUTY",ngon_method="BEAUTY")
        n_cuts = 3
        n_pokes = 3
        for i in range(n_pokes):
            bpy.ops.mesh.poke(center_mode="MEDIAN")
            bpy.ops.mesh.beautify_fill(angle_limit=deg2rad(180))
        bpy.ops.mesh.beautify_fill(angle_limit=deg2rad(180))

        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.quads_convert_to_tris()

        print("\tShade smooth")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.faces_shade_smooth()

        print("\tShrinkwrapping")
        if "Shrinkwrap" not in bpy.context.object.modifiers:
            bpy.ops.object.modifier_add(type="SHRINKWRAP")
        bpy.context.object.modifiers["Shrinkwrap"].target = topography_object
        bpy.context.object.modifiers["Shrinkwrap"].offset = -25
        bpy.context.object.modifiers["Shrinkwrap"].wrap_method = "PROJECT"
        bpy.context.object.modifiers["Shrinkwrap"].use_project_z = True
        print(act_obj.name + " Finished")

bpy.ops.object.mode_set(mode='OBJECT')
print("FINISHED ALL")
```
