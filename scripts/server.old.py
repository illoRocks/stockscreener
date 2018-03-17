# from flask_pymongo import PyMongo
#!/usr/bin/env python3.5

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "../..")))

import argparse
import logging
from flask import Flask
from pprint import pprint

from stockscreener import Settings, SecServer

# setup configuration file
config = Settings()

p = argparse.ArgumentParser(
    description='Serve Financial Statements with Flask and GraphQL.')


p.add_argument('--debug',
               action="store_true",
               default=config.get_logging(),
               help='output debug informations'
               )

p.add_argument('-server_port',
               type=int,
               default=config.get_server_port(),
               help='specify port'
               )
p.add_argument('-server_host',
               default=config.get_server_host(),
               help='specify host'
               )

p.add_argument('-db_host',
               default=config.get_database_host(),
               help='specify the host. default = localhost'
               )

p.add_argument('-db_port',
               default=config.get_database_port(),
               type=int,
               help='specify the port. default = 27017'
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

# use StockServer
ss = SecServer(
    host=args.server_host,
    port=args.server_port
)

# connect to Database
ss.connect(
    init=False,
    host=args.db_host,
    port=args.db_port,
    name_collection=config.get_db_name_collection(),
    name_path=config.get_db_name_path(),
    name_companies=config.get_db_name_companies(),
    name_reports=config.get_db_name_reports()
)

ss.start()


print('finish')
