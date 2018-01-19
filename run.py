#!/usr/bin/env python3.5

import argparse
import logging
import os


from stockscreener.sec_digger import SecDigger
from stockscreener.helper import bool_or_int

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

parser = argparse.ArgumentParser(description='Download filings.')

parser.add_argument('--debug',
                    action="store_true",
                    default=False,
                    help='comming soon'
)

parser.add_argument('-host',
                    default='localhost',
                    help='comming soon'
)

parser.add_argument('-port',
                    default='27017',
                    type=int,
                    help='comming soon'
)

parser.add_argument('--init',
                    action="store_true",
                    default=False,
                    help='comming soon'
)

parser.add_argument('-cik',
                    nargs='+',
                    default='796343',
                    help='comming soon'
)

parser.add_argument('--saveLocal',
                    action="store_true",
                    default=False,
                    help='comming soon'
)

parser.add_argument('-path',
                    default='%s/test' % WORKING_DIR,
                    help='comming soon'
)

parser.add_argument('-saveDb',
                    default=True,
                    help='comming soon'
)

parser.add_argument('-multi',
                    type=bool_or_int,
                    default=False,
                    help='comming soon'
)

args = parser.parse_args()

for arg in vars(args):
    print (arg, getattr(args, arg))

# Setup Config
if args.debug:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s/%(module)s/%(funcName)s %(message)s'
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
sd.get_files_from_web(
    cik = args.cik,
    save = args.saveLocal,
    local_file_path = args.path,
    save_to_db = args.saveDb,
    multiprocessing = args.multi
)

# python3 run.py --init --debug
# python3 run.py -port 27017 -host localhost -multi 9 --debug -cik 796343