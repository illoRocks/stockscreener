#!/usr/bin/env python3.6
import datetime
import requests
import zipfile
import io
import time
from multiprocessing import Pool
import logging
import re
import pymongo
import sys
import os.path

try:
    from .helper import ctime
    from .edgar_idx import SecIdx
    from .mongo_db import MongoHelper
    from .download_filings import XbrlCrawler
except (ImportError, SystemError):
    from helper import ctime
    from edgar_idx import SecIdx
    from mongo_db import MongoHelper
    from download_filings import XbrlCrawler


logger = logging.getLogger(__name__)

# disable log messages from the Requests library
logging.getLogger("requests").setLevel(logging.WARNING)


class SecDigger(SecIdx, MongoHelper):
    """Handler for SEC-filings"""

    def __init__(self):
        super().__init__()
        self.session = {'connection': 'not connected!',
                        'processed': 0}

    @staticmethod
    def calculatestar(kwargs):
        return SecDigger.mp_ffw(**kwargs)

    @staticmethod
    def mp_ffw(cik, date, url, save=False, local_file_path='temp', save_to_db=True, **kwargs):
        """create Download-Handler"""

        t = {'start': time.time()}
        df = XbrlCrawler(url=url, cik=cik, date=date)
        info = df.download()
        t['download'] = time.time()

        if type(info) == str:
            return info

        if save:
            df.save_documents(local_file_path)
            t['save'] = time.time()

        if save_to_db:
            result = df.parse()
            t['parse'] = time.time()
            return result, t

        return None, t

    def get_files_from_web(
        self,
        multiprocessing=False,
        name=None,
        name_regex=None,
        ticker=None,
        cik=None,
        cik_path=None,
        save=False,
        save_to_db=True,
        number_of_files=0,
        local_file_path='temp'
    ):
        logger.info('''
            start process with
            multiprocessing = %s 
            name = %s
            ticker = %s 
            cik = %s 
            cik_path = %s
            save = %s 
            save_to_db = %s 
            number_of_files = %s 
            local_file_path = %s
            ''' % (multiprocessing, name, ticker, cik, cik_path, save, save_to_db, number_of_files, local_file_path))

        if not self.connected:
            logger.error(self.status)
            quit()

        start_time = time.time()

        query = {}
        query['log'] = {'$eq': None}
        query['form'] = {'$in': ['10-K', '10-Q']}

        # add some other criterion
        if cik:
            query['cik'] = {'$in': [cik] if type(cik) == str else cik}
        elif ticker:
            query['ticker'] = {'$in': [ticker] if type(ticker) == str else ticker}
        elif name:
            query['name'] = {'$in': [name] if type(name) == str else name}
        elif name_regex:
            regx = [re.compile(r, re.IGNORECASE) for r in name_regex]
            query['name'] = {'$in': regx}
        elif cik_path:
            with open(cik_path, 'r') as file:
                ciks = [i.replace("\n", "") for i in file]
            query['cik'] = {'$in': ciks}
        else:
            logger.error("no company identifier")
            quit()

        logger.debug('path query: %s' % query)
        # execute download for each edgar_path
        tasks = []
        for row in self.col_edgar_path.find(query).limit(number_of_files):
            row['save'] = save
            row['local_file_path'] = local_file_path
            row['save_to_db'] = save_to_db
            tasks.append(row)
            
        if len(tasks) == 0:
            logger.debug(query)
            logger.warning('no more filings!')
            quit()

        def store_result(res):
            ''' store files in database '''

            if type(res) == str:
                if 'error' in res:
                    self.col_edgar_path.update({'cik': res['cik'], 'path': res['edgar_path']},
                                               {'$set': {'log': 'error'}}, False, True)
            else:
                try:
                    self.col_companies.update_one(**res['query_company'])
                    self.col_financial_positions.insert_many(res['query_financial_positions'], ordered=False)
                except TypeError:
                    logger.error(res['query_company'])
                    quit()
                except pymongo.errors.WriteError as err:
                    logger.error(res['query_company'])
                    logger.error('Please check the query: WriteError %s' % err)
                    quit()
                except pymongo.errors.BulkWriteError as err:
                    pass

                self.col_edgar_path.update({'cik': res['cik'], 'path': res['edgar_path']},
                                           {'$set': {'log': 'stored'}}, False, True)

            self.session['processed'] += 1

        if not multiprocessing:
            logger.debug('use synchronious mode')
            for row in tasks:
                data, t = self.mp_ffw(**row)
                if data is not None:
                    store_result(data)
                    logger.info("elapsed: %s min\tprocessed: %s Stücke | latest: %s" %
                                (round((time.time() - start_time) / 60), self.session['processed'], data['edgar_path']))

        else:

            worker = 4 if multiprocessing is bool else multiprocessing
            with Pool(worker) as pool:

                imap_unordered_it = pool.imap_unordered(
                    SecDigger.calculatestar, tasks)

                logger.info('Unordered results using pool.imap_unordered():')
                for data, t in imap_unordered_it:
                    store_result(data)
                    logger.info("elapsed: %s min\tprocessed: %s pieces\tlatest: %s" %
                    (round((time.time() - start_time) / 60), self.session['processed'], data['edgar_path']))

    def __str__(self):
        """print all abaut this session"""
        l = ''
        for key, value in self.session.items():
            l += '%s:\t%s\n' % (key, value)
        return l


if __name__ == '__main__':
    """lade IDX herunter und seicher diese in DB"""

    import logging
    logging.basicConfig(level=logging.DEBUG)

    # use SecDigger
    sd = SecDigger()

    # connect to Database
    sd.connect()

    # 
    sd.get_files_from_web(cik="1080224")

    # insert reports
    # sd.col_financial_positions.insert_many([
    #     {'startDate': datetime.datetime(2003, 11, 29, 0, 1), 'cik': '123', 'label': 'WeightedAverageNumberDilutedSharesOutstanding', 'updated': datetime.datetime(2006, 2, 8, 0, 0), 'value': 495626000, 'endDate': datetime.datetime(2004, 12, 3, 0, 0)},
    #     {'startDate': datetime.datetime(2003, 11, 29, 0, 2), 'cik': '123 f', 'label': 'OperatingExpenses', 'updated': datetime.datetime(2006, 2, 8, 0, 0), 'value': 970409000, 'endDate': datetime.datetime(2004, 12, 3, 0, 0)}, 
    #     {'startDate': datetime.datetime(2003, 11, 29, 0, 2), 'cik': '123', 'label': 'IssuanceCompensatoryStockAdditionalPaidCapital', 'updated': datetime.datetime(2006, 2, 8, 0, 0), 'value': 225000, 'endDate': datetime.datetime(2004, 12, 3, 0, 0)}
    #     ], ordered=False)

# edgar/data/1000045/0001193125-11-216128.txt'
