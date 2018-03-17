# from flask_pymongo import PyMongo
#!/usr/bin/env python3.5

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "../..")))

import argparse
from flask import Flask
from pprint import pprint

from stockscreener import Settings, MongoHelper

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

# use StockServer
ss = MongoHelper()

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


# server
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

print('finish')
