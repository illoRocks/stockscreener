#!/usr/bin/env python3.6


import sys
from download_filings import SecDigger

args = {}
try:
    args['limit'] = int(sys.argv[2])
except:
    pass

try:
    args['processes'] = int(sys.argv[1])
except:
    pass

# Datenbank anlegen cik als Index + Accession als List
# edgar_idx.getIdx()

# Berichte runterladen
crawler = SecDigger()
crawler.get_param()
crawler.download(verbose=True)
crawler.save_documents(join(dirname(abspath(__file__)), 'temp'))




