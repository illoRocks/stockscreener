#!/usr/bin/env python3.5

import argparse
import logging
import os
import configparser

from stockscreener.sec_digger import SecDigger
from stockscreener.helper import bool_or_int

# setup configuration file
config = configparser.ConfigParser()
config.read(['config.ini', 'stockscreener.ini'])
DATABASE = config['DATABASE']
LOGGING = config['LOGGING']
PARSER_OPTIONS = config['PARSER_OPTIONS']

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

p = argparse.ArgumentParser(description='Download filings from EDGAR.')

p.add_argument('--debug',
               action="store_true",
               default=LOGGING.getboolean('Logging', False),
               help='output debug informations'
               )

p.add_argument('--info',
               action="store_true",
               default=True,
               help='output process informations'
               )

p.add_argument('-host',
               default=DATABASE.get('host', 'localhost'),
               help='specify the host. default = localhost'
               )

p.add_argument('-port',
               default=DATABASE.getint('port', 27017),
               type=int,
               help='specify the port. default = 27017'
               )

p.add_argument('--init',
               action="store_true",
               default=False,
               help='initialize the database. the programm quit after that'
               )

p.add_argument('-cik',
               nargs='+',
               default='796343',
               help='valid central index key. one or more strings'
               )

p.add_argument('-cikPath',
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

p.add_argument('--saveLocal',
               action="store_true",
               default=PARSER_OPTIONS.getboolean('save', False),
               help='set this flag if you want to save the files localy'
               )

p.add_argument('-path',
               default=PARSER_OPTIONS.get(
                   'local_file_path', '%s/test' % WORKING_DIR),
               help='specify the path where the files should be stored'
               )

p.add_argument('-saveDb',
               default=PARSER_OPTIONS.getboolean('save_to_db', True),
               help='if set to False it will be not stored at the database'
               )

p.add_argument('-multi',
               type=bool_or_int,
               default=PARSER_OPTIONS.getint('multiprocessing', 0),
               help='Option for multiprocessing. default = False. if True then 4 worker will be used or use your prefered number of worker.'
               )

p.add_argument('-limit',
               type=int,
               default=PARSER_OPTIONS.getint('number_of_files', -1),
               help='limit the number of downloads'
               )

p.add_argument('--skipIndexdex',
               action="store_true",
               default=False,
               help='skip the index updater'
               )


args = p.parse_args()

# Setup Config
if args.debug:
    logging.basicConfig(
        level=LOGGING.getint('level', 30),
        format='%(levelname)s\t%(message)s'
    )

# use SecDigger
sd = SecDigger()

# connect to Database
sd.connect(
    host=args.host,
    port=args.port
)

# fill database with paths
if not args.skipIndexdex:
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

# python3 run.py --init --debug
# python3 run.py -port 27017 -host localhost -multi 9 --debug -cik 796343
# python3 run.py -port 27017 -host localhost -multi 9 --debug -nameRegex "coca cola" -limit 5
# python3 run.py -cikPath dowjones.txt --skipIndex
