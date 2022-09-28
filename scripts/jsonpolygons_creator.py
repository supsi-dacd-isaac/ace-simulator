import argparse
import json
import csv
import logging
import os
import sys


# Functions
def get_rectangle_vertexes(points):
    x1, y1 = points[0].split(',')
    x1 = float(x1)
    y1 = float(y1)

    x2, y2 = points[1].split(',')
    x2 = float(x2)
    y2 = float(y2)

    if x1 < x2 and y1 < y2:
        # First case (P1 bottom left)
        # ** --------- P2
        # |             |
        # |             |
        # |             |
        # P1 --------- **
        return [
                    [x1, y1],
                    [x2, y1],
                    [x2, y2],
                    [x1, y2],
               ]
    else:
        # Second case (P1 top left)
        # P1 --------- **
        # |             |
        # |             |
        # |             |
        # ** --------- P2
        return [
                    [x1, y1],
                    [x1, y2],
                    [x2, y2],
                    [x2, y1],
               ]


def get_polygon_vertexes(str_data):
    # Clean the data
    str_data = str_data.replace('\'', '').replace(' ', '').replace('\'', '').replace('\t', '')

    # Get the points
    points = str_data.split(';')

    # Rectangles special case
    if len(points) == 2:
        vertexes = get_rectangle_vertexes(points)
    else:
        vertexes = []
        for point in points:
            try:
                x, y = point.split(',')
            except Exception as e:
                logger.error('EXCEPTION: %s' % str(e))
            x = float(x)
            y = float(y)
            vertexes.append([x, y])
    return vertexes


def row_handling(row):
    num_polygons = int(row[2])
    municipality_info = {
        'name': row[0],
        'id': row[1],
        'polygons': []
    }
    for i in range(0, num_polygons):
        # Get the polygon vertexes
        vertxs = get_polygon_vertexes(row[3 + i])

        # Add the polygon data
        municipality_info['polygons'].append(vertxs)
    return municipality_info


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

    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)-15s::%(levelname)s::%(funcName)s::%(message)s', level=logging.INFO,
                        filename=None)

    args = arg_parser.parse_args()
    input_csv_file = cfg['polygons']['csvFile']
    output_json_file = cfg['polygons']['jsonFile']

    # Starting program
    logger.info('Starting program')

    logger.info('%s' % input_csv_file)

    logger.info('Read data from file %s' % input_csv_file)
    municipalities_info = []
    with open(input_csv_file, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=':')
        header = None
        for row in rows:
            if header is None:
                header = row
            else:
                if row[2] != '':
                    logger.info('Create polygons for %s' % row[1])
                    municipality_info = row_handling(row)
                    municipalities_info.append(municipality_info)
                else:
                    logger.warning('No available polygons for %s' % row[1])

    logger.info('Save data on file %s' % output_json_file)
    with open(output_json_file, 'w') as json_file:
        json.dump(municipalities_info, json_file, indent=2)

    # Ending program
    logger.info('Ending program')

