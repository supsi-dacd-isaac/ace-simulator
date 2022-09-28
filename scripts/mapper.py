import argparse
import json
import sys
import logging
import os
import geopandas as gpd
import contextily as ctx
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Main
if __name__ == "__main__":
    # Input args
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-f', help='configuration file')
    arg_parser.add_argument('-l', help='log file (optional, if empty log redirected on stdout)')

    args = arg_parser.parse_args()
    if os.path.isfile(args.f) is False:
        print('\nATTENTION! Unable to open configuration file %s\n' % args.f)
        sys.exit(1)
    cfg = json.loads(open(args.f).read())

    # Set the logging object
    if not args.l:
        log_file = None
    else:
        log_file = args.l

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=logging.INFO,
                        filename=log_file)

    # Starting program
    logger.info('Starting program')

    ticino_borders = gpd.read_file(cfg['inputShpFile'])
    ticino_borders = ticino_borders.to_crs(epsg=cfg['mapper']['background']['epsg'])

    ax = None
    ax = ticino_borders.plot(alpha=0.33, edgecolor='k', color='red', ax=ax)
    # ctx.add_basemap(ax, crs='epsg:%s' % cfg['mapper']['background']['epsg'], source=cfg['mapper']['background']['file'])
    ax.set_axis_off()
    plt.tight_layout()

    plt.show()

    # Ending program
    logger.info('Ending program')

