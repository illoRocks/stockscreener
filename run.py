#!/usr/bin/env python3.5

import argparse
import logging
import os

from stockscreener.sec_digger import SecDigger
from stockscreener.helper import bool_or_int

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Download filings from EDGAR.')

parser.add_argument('--debug',
                    action="store_true",
                    default=False,
                    help='output process informations'
)

parser.add_argument('-host',
                    default='localhost',
                    help='specify the host. default = localhost'
)

parser.add_argument('-port',
                    default=27017,
                    type=int,
                    help='specify the port. default = 27017'
)

parser.add_argument('--init',
                    action="store_true",
                    default=False,
                    help='initialize the database. the programm quit after that'
)

parser.add_argument('-cik',
                    nargs='+',
                    default='796343',
                    help='valid central index key. one or more strings'
)

parser.add_argument('-name',
                    nargs='+',
                    help='valid company name or regex "/coca cola/i". one or more'
)

parser.add_argument('-nameRegex',
                    nargs='+',
                    help='regex like "^coca cola". one or more'
)

parser.add_argument('--saveLocal',
                    action="store_true",
                    default=False,
                    help='set this flag if you want to save the files localy'
)

parser.add_argument('-path',
                    default='%s/test' % WORKING_DIR,
                    help='specify the path where the files should be stored'
)

parser.add_argument('-saveDb',
                    default=True,
                    help='if set to False it will be not stored at the database'
)

parser.add_argument('-multi',
                    type=bool_or_int,
                    default=False,
                    help='Option for multiprocessing. default = False. if True then 4 worker will be used or use your prefered number of worker.'
)


parser.add_argument('-limit',
                    type=int,
                    default=-1,
                    help='limit the number of downloads'
)

args = parser.parse_args()

# for arg in vars(args):
#     print (arg, getattr(args, arg))

# Setup Config
if args.debug:
    logging.basicConfig(
        level=logging.DEBUG,
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
else:
    key['cik'] = args.cik

sd.get_files_from_web(
    **key,
    save = args.saveLocal,
    local_file_path = args.path,
    save_to_db = args.saveDb,
    multiprocessing = args.multi,
    number_of_files = args.limit
)

# python3 run.py --init --debug
# python3 run.py -port 27017 -host localhost -multi 9 --debug -cik 796343
# python3 run.py -port 27017 -host localhost -multi 9 --debug -name "coca cola"