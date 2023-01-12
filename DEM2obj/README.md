Converting a .tif file (specifically from GLO-30) into a .obj format suitable for import into Blender.

# Method
Download a DEM from GLO-30. `TIF_FILE` in `config.py` set to the path/filename of this downloaded DEM. `OUTPUT_OBJ_FILE` and `CORNERS_JSON_FILE` in `config.py` set to desired path/filename.

Run `process_tif_create_obj_and_json.py`, which performs some interpolation and smoothing of the topography data (as the data appears slightly streaky along lines of longitude).

The `OUTPUT_OBJ_FILE` contains a transformed DEM whose south-west corner lies at the origin. `CORNERS_JSON_FILE` stores the OSGB36 position of the south-west corner so the topography is not completely without georeference.

# Viewing the OBJ File into Blender
Since real scale is used, it is likely the dimensions of the OBJ file are much greater than can be seen using the default viewing options in Blender - the viewport clip end may need to be increased by quite a bit, and there may be quite a bit of zooming out required too.

Once loaded, positive X appears to be North, positive Y West and positive Z Up.
