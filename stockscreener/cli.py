#!/usr/bin/env python3.5

"""
python3 -m stockscreener.cli --config config.ini -init

"""

import configargparse
import logging
import argparse
import sys
import os
from configparser import ConfigParser

from .helper import bool_or_int
from .sec_digger import SecDigger

# SCRIPT_DIR = os.path.dirname(os.path.realpath(
#     os.path.join(os.getcwd(), os.path.expanduser(__file__))))
# sys.path.insert(0, os.path.normpath(os.path.join(SCRIPT_DIR, '..')))

logger = logging.getLogger(__name__)

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))


p = configargparse.ArgumentParser(default_config_files=['config.ini', 'stockscreener.ini'],
                                  add_config_file_help='Download filings from EDGAR.')

p.add_argument('-c', '--config', is_config_file=True, help='config file path')

# setup arguments
p.add_argument('-d', '--debug', action="store_true",
               help='output debug informations')

p.add_argument('-i', '--info', action="store_true",
               help='output process informations')

p.add_argument('--logging', help='logging level', type=int)


# Database connection

p.add_argument('--client', default='MongoDB', help='default: MongoDB')

p.add_argument('--host', default='localhost',
               help='specify the host. default = localhost')

p.add_argument('--port', default=27017, type=int,
               help='specify the port. default = 27017')

p.add_argument('--username',
               help='specify username of your database')

p.add_argument('--password',
               help='specify username of your database')

p.add_argument('--authSource', help='specify authSource of your database')

p.add_argument('-init', action="store_true", default=False,
               help='initialize the database. the programm quit after that')

p.add_argument('--ssh_username',
               help='specify username of your database')

p.add_argument('--ssh_password',
               help='specify username of your database')

p.add_argument('--ssh_address',
               help='specify username of your database')

# Database Names

p.add_argument('--db_collection',
               help='specify username of your database')

p.add_argument('--db_path',
               help='specify username of your database')

p.add_argument('--db_companies',
               help='specify username of your database')

p.add_argument('--db_reports',
               help='specify username of your database')


# Identifier

p.add_argument('-cik', nargs='+', default='796343',
               help='valid central index key. one or more strings')

p.add_argument('--cik_path',
               help='path to textfile with valid central index key. seperated by line breaks')

p.add_argument('-name', nargs='+',
               help='valid company name or regex "/coca cola/i". one or more')

p.add_argument('-nameRegex', nargs='+',
               help='regex like "^coca cola". one or more')

p.add_argument('--transform_after', action="store_true",
               help='transform database with schema')


# Other options

p.add_argument('--save_local', action="store_true",
               help='set this flag if you want to save the files localy')

p.add_argument('--local_file_path',
               help='specify the path where the files should be stored')

p.add_argument('--save_db',
               help='if set to False it will be not stored at the database')

p.add_argument('--nthreads', type=bool_or_int,
               help='Option for multiprocessing. default = False. if True then 4 worker will be used or use your prefered number of worker.')

p.add_argument('--limit', type=int, help='limit the number of downloads')

p.add_argument('--skipIndex', action="store_true",
               help='skip the index updater')


options = p.parse_args()


def main():

    # Setup Config
    if options.debug:
        level = 10
    elif options.info:
        level = 20
    else:
        level = options.logging

    logging.basicConfig(
        level=level,
        format='%(levelname)s\t%(message)s'
    )

    # use SecDigger
    sd = SecDigger()

    # connect to Database
    sd.connect(
        db_type="MongoDB",
        init=options.init,
        host=options.host,
        port=options.port,
        username=options.username,
        password=options.password,
        ssh_address=options.ssh_address,
        ssh_username=options.ssh_username,
        ssh_password=options.ssh_password,
        authSource=options.authSource,
        name_collection=options.db_collection,
        name_path=options.db_path,
        name_companies=options.db_companies,
        name_reports=options.db_reports
    )
    # fill database with paths

    if not options.skipIndex:
        logger.info("init or update edgar paths")
        sd.download_idx(init=options.init)
        sd.save_idx()

    if options.init:
        quit()

    sys.exit(0)
    # download filings
    key = {}
    if options.name:
        key['name'] = options.name
    elif options.nameRegex:
        key['name_regex'] = options.nameRegex
    elif options.cikPath:
        key['cik_path'] = options.cikPath
    else:
        key['cik'] = options.cik

    sd.get_files_from_web(
        **key,
        save=options.saveLocal,
        local_file_path=options.path,
        save_to_db=options.saveDb,
        multiprocessing=options.multi,
        number_of_files=options.limit
    )

    if options.transform_after:
        sd.transform_collection()

    print('finish')

# python3 scripts/cli.py --init --debug
# python3 scripts/cli.py -multi 8 --skipIndex -limit 8
# python3 scripts/cli.py -port 27017 -host localhost -multi 8 -cik 796343 --skipIndex --debug
# python3 scripts/cli.py -port 27017 -host localhost -multi 8 -nameRegex "coca cola" -limit 5
# python3 scripts/cli.py -cikPath dowjones.txt -limit 1 --skipIndex --transform_after
# python3 scripts/cli.py -multi 0 -cik 796343 --skipIndex --debug -limit 1
