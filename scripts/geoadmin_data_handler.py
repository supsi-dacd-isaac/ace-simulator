import argparse
import logging
import json
import glob
import os
import sys
from pathlib import Path


# Functions
def handle_zone(cfg_ds, zone_folder, fresults):
    # Simple sum
    attrs_to_sum = dict()
    for attr_to_sum_key in cfg_ds['attributesToSumPerZone']:
        attrs_to_sum[attr_to_sum_key] = 0

    # Grouped sum
    if cfg_ds['attributesToSumPerZoneGroupedBy'] is not None:
        grouped_attrs_to_sum = dict()
        for elem in cfg_ds['attributesToSumPerZoneGroupedBy']:
            grouped_attrs_to_sum[elem['groupingAttribute']] = dict()
            for attr_to_group in elem['groupedAttributes']:
                grouped_attrs_to_sum[elem['groupingAttribute']][attr_to_group] = dict()
                for case in elem['cases']:
                    grouped_attrs_to_sum[elem['groupingAttribute']][attr_to_group][case] = 0
    else:
        grouped_attrs_to_sum = None

    ids = []
    for geoadmin_raw_file_path in sorted(glob.glob('%s%s/*' % (zone_folder, os.sep))):
        ids, attrs_to_sum, grouped_attrs_to_sum = handle_geoadmin_file(cfg_ds, geoadmin_raw_file_path, ids,
                                                                       attrs_to_sum, grouped_attrs_to_sum, fresults)

    return attrs_to_sum, grouped_attrs_to_sum


def check_filter(cfg_ds, attr):
    if cfg_ds['filter'] is None:
        return True
    else:
        k = list(cfg_ds['filter'].keys())[0]
        if cfg_ds['filter'][k] == attr[k]:
            return True
        else:
            return False


def handle_geoadmin_file(cfg_ds, file_path, ids, attrs_to_sum, grouped_attrs_to_sum, fresults):
    data = json.loads(open(file_path).read())
    if len(data['results']) > 0:
        for elem in data['results']:
            # if elem['featureId'] not in ids:
            if elem['featureId'] not in ids and check_filter(cfg_ds, elem['attributes']) is True:
                # Save data
                str_data = '%s,%s' % (file_path.split(os.sep)[-2], elem['featureId'])
                for attr in cfg_ds['attributesToReport']:
                    str_data = '%s,%s' % (str_data, elem['attributes'][attr])
                fresults.write('%s\n' % str_data)

                # Sum simple data
                for attr in cfg_ds['attributesToSumPerZone']:
                    attrs_to_sum[attr] += elem['attributes'][attr]

                # Sum grouped data
                if grouped_attrs_to_sum is not None:
                    for k_grouping in grouped_attrs_to_sum.keys():
                        for k_grouped in grouped_attrs_to_sum[k_grouping].keys():
                            grouped_attrs_to_sum[k_grouping][k_grouped][elem['attributes'][k_grouping]] += elem['attributes'][k_grouped]

                # Append the identifier
                ids.append(elem['featureId'])
    return ids, attrs_to_sum, grouped_attrs_to_sum


def prepare_file(file_path, prefix_header, header_attrs, header_grouped_attr):
    fw = open(file_path, 'w')
    header = prefix_header
    for header_attr in header_attrs:
        header = '%s,%s' % (header, header_attr)

    if header_grouped_attr is not None:
        for elem in header_grouped_attr:
            for attr_to_group in sorted(elem['groupedAttributes']):
                for case in sorted(elem['cases']):
                    header = '%s,%s_%s_%s' % (header, attr_to_group, elem['groupingAttribute'], case)

    fw.write('%s\n' % header)

    return fw


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

    for cfg_data_source in cfg['handler']['dataSourcesData']:
        logger.info('Handle data for %s datasource' % cfg_data_source['name'])

        out_folder = '%s%s%s%s' % (cfg['handler']['outputfolder'], os.sep, cfg_data_source['name'], os.sep)
        Path(out_folder).mkdir(parents=True, exist_ok=True)

        # Open and prepare results and resume files
        fw_results = prepare_file('%s/results.csv' % out_folder, 'zone,featureId',
                                  cfg_data_source['attributesToReport'], None)

        fw_resume = prepare_file('%s/resume_zones.csv' % out_folder, 'zone',
                                 cfg_data_source['attributesToSumPerZone'],
                                 cfg_data_source['attributesToSumPerZoneGroupedBy'])

        # Create municipality resume file
        municipalities_data = dict()
        for zone_folder in sorted(glob.glob('%s%s%s%s%s' % (cfg['downloader']['outputFolder'], os.sep, cfg_data_source['name'], os.sep,
                                                            cfg['downloader']['zonesRegExp']))):
            totals_simple_attrs, totals_grouped_attrs = handle_zone(cfg_data_source, zone_folder, fw_results)

            # Add the simple totals to the zone
            str_data = zone_folder.split(os.sep)[-1]
            for header_attr in cfg_data_source['attributesToSumPerZone']:
                str_data = '%s,%s' % (str_data, totals_simple_attrs[header_attr])

                # Get the municipality code
                tmp = str_data.split('_')
                zone_code = tmp[0]

            # Add the grouped totals to the zone
            if totals_grouped_attrs is not None:
                for k_grouping in totals_grouped_attrs.keys():
                    for k_grouped in sorted(totals_grouped_attrs[k_grouping].keys()):
                        for k_case in sorted(totals_grouped_attrs[k_grouping][k_grouped].keys()):
                            str_data = '%s,%s' % (str_data, totals_grouped_attrs[k_grouping][k_grouped][k_case])

                            k_mun = '%s_%s_%s' % (k_grouped, k_grouping, k_case)
                            municipalities_data[zone_code][k_mun] = 'N/A'

            fw_resume.write('%s\n' % str_data)

        fw_results.close()
        fw_resume.close()

    # Ending program
    logger.info('Ending program')
