# ace-simulator

### Polygons creation and data downloading/handling:
1. `scripts/csvpolygons_creator.py`: Create a csv file given a shp
2. `scripts/jsonpolygons_creator.py`: Create a set json files with of all the polygons settings given a csv created at point 1)
3. `scripts/zones_splitter.py`: For each polygon created at point 2) (98 zones <-> 105 polygons, 7 zones have 2 polygons) split it in triangles (concave case) or subpolygons (convex case) if the vertexes are >= 250 (GeoAdmin API limit). Map png files and new json files related to the zones splitting are created.
4. `scripts/geoadmin_data_downloader.py`: Download the configured datasets given the polygons defined at point 2) and 3) 
5. `scripts/geoadmin_data_handler.py`: Given a set of jsons file downloaded from GeoAdmin (point 4), for each zone configured data are handled to avoid repetitions and summed up to have the zone total.

The following picture summarizes the dataflow:

![data_management_schema](draw.io/data_management_schema.png)
