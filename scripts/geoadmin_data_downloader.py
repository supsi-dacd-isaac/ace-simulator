import argparse
import time
import logging
import requests
import json
import glob
import os
import sys
from http import HTTPStatus
from pathlib import Path


# Functions
def download_zone_data(data_source, zone_file):
    logger.info('Download data related to file %s' % zone_file)
    zone_data = json.loads(open(zone_file).read())

    # Check if the zone is not split
    if zone_data['polygons_coords'] is None:
        request_data_single_polygon(data_source, zone_file.split(os.sep)[-1].split('.')[0], '0',
                                    zone_data['main_polygon_coords'])
    else:
        # Cycle over the polygons in which they are split
        for k in zone_data['polygons_coords'].keys():
            # print(k, ' -> ', zone_data['polygons_coords'][k])
            request_data_single_polygon(data_source, zone_file.split(os.sep)[-1].split('.')[0], k,
                                        zone_data['polygons_coords'][k])
    return


def save_dataset(location_id, poly_id, offset, dataset, output_folder):
    out_folder = '%s%s%s%s' % (output_folder, os.sep, location_id, os.sep)
    Path(out_folder).mkdir(parents=True, exist_ok=True)
    out_file = '%sPOLY%04i_OFFSET%05i.json' % (out_folder, int(poly_id)+1, offset)
    # logger.info('Save data on file %s' % out_file)
    with open(out_file, 'w') as json_file:
        json.dump(dataset, json_file, indent=2)


def save_polygons_data(location_id, poly_id, str_poly, data_source, output_folder):
    flag_finished = False

    offset = 0
    while flag_finished is False:
        url = "%s/identify?geometry={%%22rings%%22:[%s]}&%s:%s&offset=%i" % (cfg['downloader']['geoAdmin']['url'],
                                                                             str_poly,
                                                                             cfg['downloader']['geoAdmin']['suffix'],
                                                                             data_source,
                                                                             offset)
        # Perform the GET request
        # logger.info('Request %s' % url)
        res = requests.get(url)

        if res.status_code != HTTPStatus.OK:
            logger.error('Error performing the request (status: %i): %s' % (res.status_code, res.text))
        else:
            data = json.loads(res.text)

            save_dataset(location_id, poly_id, offset, data, output_folder)
            logger.info('Saved data about %i boxes referred to polygon n. %04d, belonging to zone %s' % (len(data['results']), int(poly_id)+1, location_id))

            if len(data['results']) > 200:
                offset += 200
                logger.warning('More than 200 data points, go ahead with the offset=%i' % offset)
            else:
                logger.info('Less than 200 data points, save and exit the cycle')
                flag_finished = True
        logger.info('Wait 0.5 seconds')
        time.sleep(0.5)


def request_data_single_polygon(data_source, location_id, poly_id, vertexes):
    # Build the polygon string
    str_poly = '['
    for point in vertexes:
        str_poly = '%s[%s,%s],' % (str_poly, point[0], point[1])
    str_poly = '%s]' % str_poly[:-1]

    # Save data
    save_polygons_data(location_id, poly_id, str_poly, data_source, '%s/%s' % (cfg['downloader']['outputFolder'], data_source))

    # # Save commercial/residential data
    # save_polygons_data(location_id, poly_id, str_poly, data_source, '%s/%s' % (cfg['outputFolder'], data_source))

    # # Save industrial data
    # save_polygons_data(location_id, poly_id, str_poly, data_source, '%s/%s' % (cfg['outputFolder'], data_source))


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

    for data_source in cfg['downloader']['geoAdmin']['dataSource']:
        logger.info('Download data for %s datasource' % data_source)

        for zone_file in sorted(glob.glob('%s%sdata%s%s.json' % (cfg['zonesSplitter']['folder'], os.sep, os.sep,
                                                                 cfg['downloader']['zonesRegExp']))):
            download_zone_data(data_source, zone_file)

    # Ending program
    logger.info('Ending program')
