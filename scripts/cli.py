#!/usr/bin/env python3.5
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(
    os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.insert(0, os.path.normpath(os.path.join(SCRIPT_DIR, '..')))


import argparse
import logging
import configparser

# from ... import stockscreener
from stockscreener import SecDigger, Settings
from stockscreener.helper import bool_or_int

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

# setup configuration file
config = Settings()

p = argparse.ArgumentParser(description='Download filings from EDGAR.')

p.add_argument('--debug',
               action="store_true",
               default=config.get_logging(),
               help='output debug informations'
               )

p.add_argument('--info',
               action="store_true",
               default=True,
               help='output process informations'
               )

# Database

p.add_argument('-host',
               default=config.get_database_host(),
               help='specify the host. default = localhost'
               )

p.add_argument('-port',
               default=config.get_database_port(),
               type=int,
               help='specify the port. default = 27017'
               )
               
p.add_argument('-username',
               default=config.get_database_username(),
               type=int,
               help='specify username of your database. (default: None)'
               )

p.add_argument('-password',
               default=config.get_database_password(),
               type=int,
               help='specify username of your database. (default: None)'
               )

p.add_argument('-authSource',
               default=config.get_database_password(),
               type=int,
               help='specify authSource of your database'
               )

p.add_argument('--init',
               action="store_true",
               default=False,
               help='initialize the database. the programm quit after that'
               )

# Identifier

p.add_argument('-cik',
               nargs='+',
               default='796343',
               help='valid central index key. one or more strings'
               )

p.add_argument('-cikPath',
               default=config.get_cik_path(),
               help='path to textfile with valid central index key. seperated by line breaks'
               )

p.add_argument('-name',
               nargs='+',
               help='valid company name or regex "/coca cola/i". one or more'
               )

p.add_argument('-nameRegex',
               nargs='+',
               help='regex like "^coca cola". one or more'
               )

p.add_argument('--transform_after',
               action="store_true",
               default=config.get_transform_after(),
               help='transform database with schema'
               )


# Other options

p.add_argument('--saveLocal',
               action="store_true",
               default=config.get_saveLocal(),
               help='set this flag if you want to save the files localy'
               )

p.add_argument('-path',
               default=config.get_local_file_path(),
               help='specify the path where the files should be stored'
               )

p.add_argument('-saveDb',
               default=config.get_saveDb(),
               help='if set to False it will be not stored at the database'
               )

p.add_argument('-multi',
               type=bool_or_int,
               default=config.get_multi(),
               help='Option for multiprocessing. default = False. if True then 4 worker will be used or use your prefered number of worker.'
               )

p.add_argument('-limit',
               type=int,
               default=config.get_number_of_files(),
               help='limit the number of downloads'
               )

p.add_argument('--skipIndex',
               action="store_true",
               default=False,
               help='skip the index updater'
               )

args = p.parse_args()

# Setup Config
if args.debug:
    level = 10
elif args.info:
    level = 20
else:
    level = config.get_logging_level()

logging.basicConfig(
    level=level,
    format='%(levelname)s\t%(message)s'
)

# use SecDigger
sd = SecDigger()

# connect to Database
sd.connect(
    init=args.init,
    host=args.host,
    port=args.port,
    username=args.username,
    password=args.password,
    authSource=args.authSource,
    name_collection=config.get_db_name_collection(),
    name_path=config.get_db_name_path(),
    name_companies=config.get_db_name_companies(),
    name_reports=config.get_db_name_reports()
)

# fill database with paths
if not args.skipIndex:
    sd.download_idx(init=args.init)
    sd.save_idx()

if args.init:
    quit()

# download filings
key = {}
if args.name:
    key['name'] = args.name
elif args.nameRegex:
    key['name_regex'] = args.nameRegex
elif args.cikPath:
    key['cik_path'] = args.cikPath
else:
    key['cik'] = args.cik

sd.get_files_from_web(
    **key,
    save=args.saveLocal,
    local_file_path=args.path,
    save_to_db=args.saveDb,
    multiprocessing=args.multi,
    number_of_files=args.limit
)

if args.transform_after:
    sd.transform_collection()

print('finish')

# python3 scripts/cli.py --init --debug
# python3 scripts/cli.py -multi 8 --skipIndex -limit 8
# python3 scripts/cli.py -port 27017 -host localhost -multi 8 -cik 796343 --skipIndex --debug
# python3 scripts/cli.py -port 27017 -host localhost -multi 8 -nameRegex "coca cola" -limit 5
# python3 scripts/cli.py -cikPath dowjones.txt -limit 1 --skipIndex --transform_after
# python3 scripts/cli.py -multi 0 -cik 796343 --skipIndex --debug -limit 1
