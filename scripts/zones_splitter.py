import argparse
import json
import os
import sys
import logging
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from classes.pycasso import Pycasso

# Functions

# Main
if __name__ == "__main__":
    # Input args
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', help='configuration file')

    args = arg_parser.parse_args()
    if os.path.isfile(args.f) is False:
        print('\nATTENTION! Unable to open configuration file %s\n' % args.f)
        sys.exit(1)
    cfg = json.loads(open(args.f).read())

    polygons = json.loads(open(cfg['polygons']['jsonFile']).read())

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=logging.INFO,
                        filename=None)

    # Starting program
    logging.info('Starting program')

    pycasso = Pycasso(plt=plt, logger=logger)

    for location in polygons:
        for i in range(0, len(location['polygons'])):
            desc = '%s_poly%02d' % (location['name'], i+1)
            logging.info('Polygon %s: started analysis' % desc)

            map_file = '%s%smaps%s%s_ZONE%02d.png' % (cfg['zonesSplitter']['folder'], os.sep, os.sep, location['id'], i+1)
            data_file = '%s%sdata%s%s_ZONE%02d.json' % (cfg['zonesSplitter']['folder'], os.sep, os.sep, location['id'], i+1)
            pycasso.handle_polygon(main_polygon=location['polygons'][i], max_vertexes=cfg['zonesSplitter']['maxVertexes'],
                                   desc_title=desc, map_file=map_file, data_file=data_file)

            logging.info('Polygon %s: ended analysis' % desc)

    # Ending program
    logging.info('Ending program')
