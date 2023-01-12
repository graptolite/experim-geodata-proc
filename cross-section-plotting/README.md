Plotting a cross section of units given topography and unit distribution data.

# DEM Format
The code uses a JSON file of georeferenced elevations to interpolate topography along the section.

To get this JSON format from the downloaded TIF (e.g. for `../DEM2obj`), run `process_tif_to_interp_json.py`.

# Map Format
For this code to work, the map must be in a PNG format where no antialiasing has taken place. Units must not have any line margins such that the colour of each unit is uniform throughout its body **and** margin. The SW and NE corners in OSGB36 coordinates of the page within the SVG file are set as `MAP_SW` and `MAP_NE` in `config.py`. It's easier to get an un-antialiased PNG by opening the SVG file in GIMP as a bitmap and then exporting as a PNG - make sure this PNG is set to `MAP_PNG` in `config.py`. This is so that the only colours in the image are of the units themselves and not mixtures between the colours of two units adjacent to each other.

Run `process_lithology.py`, making sure `KEEP_EVERY_N` in `config.py` has been set to preference (the code will discard everything except values in a flattened list with indices that are a multiple of `KEEP_EVERY_N`).

# "Surface" Cross Section Plotting
Run `plotting.py` with the list of desired coordinates in the `p_s` variable at the top of the file. This will produce line sections with interpolated lithologies and topographies. Be aware that this process is **very resource-intensive**.
