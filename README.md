# ace-simulator!

Polygons creation and data downloading/handling:
scripts/csvpolygons_creator.py: Create a csv file given a shp
scripts/jsonpolygons_creator.py: Create a set json files with of all the polygons settings given a csv created at point 1)
scripts/zones_splitter.py: For each polygon created at point 2) (98 zones <-> 105 polygons, 7 zones have 2 polygons) split it in triangles (concave case) or subpolygons (convex case) if the vertexes are >= 250 (GeoAdmin API limit). Map png files and new json files related to the zones splitting are created.
scripts/geoadmin_data_downloader.py: Download the configured datasets given the polygons defined at point 2) and 3)
scripts/geoadmin_data_handler.py: Given a set of jsons file downloaded from GeoAdmin (point 4), for each zone configured data are handled to avoid repetitions and summed up to have the zone total.
The following picture summarizes the dataflow:
[data_management_schema](https://user-images.githubusercontent.com/56017319/217249077-540b9ca7-e813-4188-af5e-b16d2d174dc1.png)
