#!/usr/bin/env python3.5

from stockscreener.sec_digger import SecDigger
import logging
import os

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s/%(module)s/%(funcName)s %(message)s'
)

# use SecDigger
sd = SecDigger()


# connect to Database
sd.connect(
    host='localhost',
    port=27017
)

# # Initialize the Database / apply only once!
# sd.download_idx(init=True)
# sd.save_idx()

# if index allredy exist
sd.download_idx()
sd.save_idx()

# # download filings with singleprocessing
# sd.get_files_from_web(
#   cik='796343',
#   save=True,
#   local_file_path='%s/test' % WORKING_DIR,
#   save_to_db=True,
#   number_of_files=1
# )

# download filings with multiprocessing
sd.get_files_from_web(
    cik='796343',
    multiprocessing=8
)
print(sd)