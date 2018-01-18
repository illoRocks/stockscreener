from stockscreener.sec_digger import SecDigger
import logging
import os

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

# use SecDigger
sd = SecDigger()

# set debug level
sd.loggingBasicConfig(
  level=logging.DEBUG,
  format='%(levelname)s/%(module)s/%(funcName)s %(message)s'
  )

# connect to Database
sd.connect(database='sec_digger', collection='stocks')

# Init Database / apply only once!
# sd.download_idx()
# sd.save_idx()

# # if index allredy exist
# sd.download_idx(whole=False)
# sd.save_idx()

# download filings
options = {
  'multiprocessing': False,
  'cik': '796343',
  'save': False,
  'local_file_path': '%s/test' % WORKING_DIR
}
sd.get_files_from_web(**options)
