import argparse
import logging
import json
import os
import numpy as np
import geopandas as gpd
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon


# Functions
def get_polygon_string(geometry):
    coords = np.asarray(list(geometry.exterior.coords))
    str_polygon = ''
    for coord in coords:
        str_polygon = '%s%f,%f;' % (str_polygon, coord[0], coord[1])
    str_polygon = '%s:' % str_polygon[0:-1]
    return str_polygon


# Main
if __name__ == "__main__":
    # Input args
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', help='configuration file')

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=logging.INFO,
                        filename=None)

    args = arg_parser.parse_args()
    input_csv_file = args.f
    cfg = json.loads(open(args.f).read())

    # Starting program
    logger.info('Starting program')

    # Read the shp file and decode the Geopandas dataframe using the Swiss coordinates (epsg code: 21781)
    logger.info('Read polygons coordinates from file %s' % cfg['inputShpFile'])
    raw_limes = gpd.read_file(cfg['inputShpFile'])
    limes = raw_limes.to_crs(epsg=21781)

    # Create the CSV file
    fw = open(cfg['polygons']['csvFile'], 'w')

    # Header
    fw.write('Region:Polygon_n:Polygon_P1:Polygon_P2:Polygon_P3:Polygon_P4:Polygon_P5:Polygon_P6:Polygon_P7:Polygon_P8:Polygon_P9:Polygon_P10:Polygon_P11\n')
    for i in range(0, len(limes)):
        logger.info('Create polygons string for region n. %i (id=%s)' % (i+1, limes['OBJECTID'][i]))
        if type(limes['geometry'][i]) is MultiPolygon:
            str_polygons = ''
            for j in range(0, len(limes['geometry'][i])):
                str_polygon = get_polygon_string(limes['geometry'][i][j])
                str_polygons += str_polygon
            str_polygons = '%s_%02d:%s:%i:%s' % (cfg['label'], limes['OBJECTID'][i], limes['OBJECTID'][i],
                                               len(limes['geometry'][i]), str_polygons)
            fw.write('%s\n' % str_polygons)
        else:
            str_polygons = get_polygon_string(limes['geometry'][i])
            str_polygons = '%s_%02d:%s:1:%s' % (cfg['label'], limes['OBJECTID'][i], limes['OBJECTID'][i], str_polygons)
            fw.write('%s\n' % str_polygons)
    fw.close()

    logger.info('Data saved in file %s' % cfg['polygons']['csvFile'])

    # Ending program
    logger.info('Ending program')
