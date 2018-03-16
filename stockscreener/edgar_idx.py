#!/usr/bin/env python3.6
'''
Created on 04.02.2017

@author: Oliver Haag
'''
import datetime
import requests
import pymongo
import io
from collections import defaultdict
from urllib.request import urlopen
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
from urllib.request import urlopen, build_opener
from zipfile import ZipFile
import logging
import threading
import asyncio
import aiohttp

try:
    from .mongo_db import MongoHelper
except (ImportError, SystemError):
    from mongo_db import MongoHelper


import logging
logger = logging.getLogger(__name__)


class SecIdx(MongoHelper):
    def __init__(self):
        super().__init__()
        self.idx = []

    def download_idx(self, init=False, quarterly_files=list()):
        """if init then 1993 until the most recent quarter"""

        if type(quarterly_files) is not list:
            raise TypeError('quarterly_files: expect list!')

        current_year = datetime.date.today().year
        current_quarter = (datetime.date.today().month - 1) // 3 + 1

        if init and len(quarterly_files) == 0:
            logger.info('initialize database')
            start_year = 1993
            years = list(range(start_year, current_year))
            quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
            history = [(y, q) for y in years for q in quarters]
            for i in range(1, current_quarter):
                history.append((current_year, 'QTR%d' % i))
            quarterly_files = [
                'https://www.sec.gov/Archives/edgar/full-index/%d/%s/xbrl.zip' % (x[0], x[1]) for x in history]
            quarterly_files.sort()
            quarterly_files.append(
                'https://www.sec.gov/Archives/edgar/full-index/xbrl.zip')

            logging.debug('Start year: 1993')

        elif len(quarterly_files) == 0:
            logging.debug("download index of current quarter")

            if current_quarter == 1:
                last_quarter = 4
                last_year = current_year - 1

            else:
                last_quarter = current_quarter - 1
                last_year = current_year

            quarterly_files = [
                'https://www.sec.gov/Archives/edgar/full-index/%d/QTR%s/xbrl.zip' % (
                    last_year, last_quarter),
                'https://www.sec.gov/Archives/edgar/full-index/xbrl.zip']

        async def getUrl(url):
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.read()
                    await asyncio.sleep(5)
                    
            with ZipFile(BytesIO(data)) as zfile:
                with zfile.open('xbrl.idx') as z:
                    for line in z:
                        if '----' in line.decode('latin-1'):
                            break
                    self.idx.extend(
                        tuple(line.decode('latin-1').rstrip().split('|')) for line in z)
            logger.debug(url)

        logger.debug('download zip files...')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(
            *(getUrl(args) for args in quarterly_files)))

        logger.debug('Files downloaded')

    def save_idx(self):
        """save idx to mongodb"""

        if not self.connected:
            logger.error(self.status)
            quit()

        elif len(self.idx) == 0:
            logger.debug('need files!')

        else:
            logger.info("prepare query...")
            bulk = []
            for cik, name, form, date, path in self.idx:
                bulk.append({'cik': cik,
                             'path': path,
                             'name': name,
                             'form': form,
                             'date': date,
                             'log': None})

            logger.info("write to database...")
            try:
                logging.info('ignore errors!')
                self.col_edgar_path.insert_many(bulk, ordered=False)
            except pymongo.errors.BulkWriteError as err:
                logging.error('BulkWriteError: %s' % err.details)
                
            logging.debug("saved all paths")

    def __str__(self):
        if len(self.idx) == 0:
            return 'no files!'
        else:
            return 'paths: %s' % len(self.idx)


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s/%(module)s/%(funcName)s %(message)s'
    )

    i = SecIdx()
    i.connect()
    # i.save_idx()  # Not connected to database!
    # logging.debug(i)  # no files!
    # # , quarterly_files=['https://www.sec.gov/Archives/edgar/full-index/2012/QTR3/xbrl.zip', ])
    # i.download_idx()
    # logging.debug(i)  # paths: NUMBER
    # i.save_idx()  # Not connected to database!
    # i.save_idx()
    # logging.debug("finish")

    # # Download current Index
    i.download_idx(init=True)

    # store paths in database
    i.save_idx()
