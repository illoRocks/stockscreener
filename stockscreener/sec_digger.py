#!/usr/bin/env python3.6
import datetime
import requests
import zipfile
import io
import time
from multiprocessing import Pool
import logging
import re
import sys
import os.path
import pprint


from stockscreener.helper import ctime
from stockscreener.edgar_idx import SecIdx
from stockscreener.database.db_client import DBClient
from stockscreener.xbrl_crawler import XbrlCrawler


logger = logging.getLogger(__name__)

# disable log messages from the Requests library
logging.getLogger("requests").setLevel(logging.WARNING)


class SecDigger(SecIdx, DBClient):
    """Handler for SEC-filings"""

    def __init__(self):
        super().__init__()
        self.session = {'connection': 'not connected!',
                        'processed': 0}

    @staticmethod
    def calculatestar(kwargs):
        return SecDigger.mp_ffw(**kwargs)

    @staticmethod
    def mp_ffw(cik, date, path, save=False, local_file_path='temp',
               save_to_db=True, **kwargs):
        """create Download-Handler"""

        t = {'start': time.time()}
        df = XbrlCrawler(url=path, cik=cik, date=date)
        df.download()
        t['download'] = time.time()

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
            logger.error("database is not connected")
            quit()

        start_time = time.time()

        if cik_path:
            with open(cik_path, 'r') as file:
                cik = [i.replace("\n", "") for i in file]

        # execute download for each edgar_path
        docs = self.db_get_edgar_path(name=name, name_regex=name_regex,
                                      ticker=ticker, cik=cik, limit=number_of_files)
        tasks = []
        for doc in docs:
            doc['save'] = save
            doc['local_file_path'] = local_file_path
            doc['save_to_db'] = save_to_db
            tasks.append(doc)

        if len(tasks) == 0:
            logger.warning('no more filings!')
            quit()

        def store_result(res):
            ''' store files in database '''

            if type(res) == str or res is None:
                if 'error' in res or res is None:
                    self.db_update_edgar_path(filter={'path': res['edgar_path']},
                                              update={'$set': {'log': 'error'}})
            else:
                self.db_update_companie(filter=res['query_company']['filter'],
                                        update=res['query_company']['update'])

                self.db_save_report_positions(res['query_financial_positions'])

                if len(res['query_segment']) > 0:
                    self.db_save_segments(res['query_segment'])

                self.db_update_edgar_path(filter={'path': res['edgar_path']},
                                          update={'$set': {'log': 'stored'}})

            self.session['processed'] += 1

        if not multiprocessing or multiprocessing <= 1:
            logger.debug('use synchronious mode')
            for row in tasks:
                data, _ = self.mp_ffw(**row)
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
                for data, _ in imap_unordered_it:
                    store_result(data)
                    logger.info("elapsed: %s min\tprocessed: %s pieces\tlatest: %s" %
                                (round((time.time() - start_time) / 60), self.session['processed'], data['edgar_path']))

    def __str__(self):
        """print all about this session"""
        l = ''
        for key, value in self.session.items():
            l += '%s:\t%s\n' % (key, value)
        return l


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    # use SecDigger
    sd = SecDigger()

    # connect to Database
    sd.connect()

    #
    # sd.get_files_from_web(cik="104169")

    # insert reports
    # sd.col_financial_positions.insert_many([
    #     {'startDate': datetime.datetime(2003, 11, 29, 0, 1), 'cik': '123', 'label': 'WeightedAverageNumberDilutedSharesOutstanding', 'updated': datetime.datetime(2006, 2, 8, 0, 0), 'value': 495626000, 'endDate': datetime.datetime(2004, 12, 3, 0, 0)},
    #     {'startDate': datetime.datetime(2003, 11, 29, 0, 2), 'cik': '123 f', 'label': 'OperatingExpenses', 'updated': datetime.datetime(2006, 2, 8, 0, 0), 'value': 970409000, 'endDate': datetime.datetime(2004, 12, 3, 0, 0)},
    #     {'startDate': datetime.datetime(2003, 11, 29, 0, 2), 'cik': '123', 'label': 'IssuanceCompensatoryStockAdditionalPaidCapital', 'updated': datetime.datetime(2006, 2, 8, 0, 0), 'value': 225000, 'endDate': datetime.datetime(2004, 12, 3, 0, 0)}
    #     ], ordered=False)

    res = sd.col_companies.find({})
    ciks = []

    u1 = res[0]['reports']
    u2 = res[1]['reports']
    u3 = res[2]['reports']

    l1 = len(u1)
    l2 = len(u2)
    l3 = len(u3)

    eq = []
    for i in u1:
        for j in u2:
            for k in u3:
                if i == j or i == k or j == k:
                    eq.append(i)

    print('result: ', len(eq))

# edgar/data/1000045/0001193125-11-216128.txt'
