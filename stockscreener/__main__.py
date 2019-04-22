from stockscreener.cli import main
import datetime
import time
import re
from pprint import pprint
from stockscreener.server import app
from stockscreener.database.db_client import DBClient
from stockscreener.interfaces import SecSchema
import os

from collections import defaultdict


import logging
logging.basicConfig(
    level=10,
    format='%(levelname)s\t%(message)s'
)

if __name__ == "__main__":

    app.run()
    # main()

    # client = DBClient()
    # client.connect()
    # f = client.get_fillings('21344').filter(form=SecSchema.INCOME)
    # print(f)
