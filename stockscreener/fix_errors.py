
import os
import logging
import sys

try:
    from .xbrl_crawler import XbrlCrawler
except (ImportError, SystemError):
    from xbrl_crawler import XbrlCrawler

logging.basicConfig(
    level=10,
    format='%(levelname)s\t%(message)s'
)

# init crawler
# crawler1 = XbrlCrawler("edgar/data/98246/0000098246-19-000047.txt")
# crawler1.download()
# crawler1.save_documents_local("logs/xbrl")
# result = crawler1.parse()
# print(result)
# sys.exit(0)

# init crawler
crawler = XbrlCrawler()

# setup files
cik = "63908"
accessions = os.listdir("logs/errors/" + cik)
crawler.read_files_local("logs/errors", cik, accessions[0])

result = crawler.parse()

print(result)

# print(os.listdir("logs/errors"))
# crawler = XbrlCrawler()

# crawler.parse("log/errors/")
