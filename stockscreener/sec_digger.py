#!/usr/bin/env python3.6
import datetime
import requests
import zipfile
import io
import time
from pprint import pprint
from multiprocessing import Pool
import logging
import logging.config

from .helper import ctime
from .edgar_idx import SecIdx
from .mongo_db import MongoHelper
from .download_filings import DownloadFilings


logger = logging.getLogger(__name__)


# def calculatestar(kwargs):
#     return mp_ffw(**kwargs)
#
#
# def mp_ffw(save=False, verbose=False, **kwargs):
#     """create Download-Handler"""
#
#     df = DownloadFilings(**kwargs)
#
#     df.download(verbose=verbose)
#     if save:
#         p = '/temp' if 'local_file_path' not in kwargs else '/' + kwargs['local_file_path']
#         p += '' if 'cik' not in kwargs else '/' + kwargs['cik']
#         df.save_documents(p)
#     result = df.parse(verbose=verbose)
#
#     return result


class SecDigger(SecIdx, MongoHelper):
    """Handler for SEC-filings"""

    def __init__(self):
        super().__init__()
        self.session = {'connection': 'not connected!',
                        'downloaded files': 0}

    def loggingBasicConfig(self, **kwargs):
      logging.basicConfig(**kwargs)

    @staticmethod
    def calculatestar(kwargs):
        return SecDigger.mp_ffw(**kwargs)

    @staticmethod
    def mp_ffw(save = False, local_file_path = 'temp', **kwargs):
        """create Download-Handler"""

        t = {'start': time.time()}
        df = DownloadFilings(**kwargs)
        res = df.download()
        t['download'] = time.time()
        if type(res) == str:
            return res
        if save:
            df.save_documents(local_file_path)
            t['save'] = time.time()
        result = df.parse()
        t['parse'] = time.time()

        return result, t

    def get_files_from_web(self, multiprocessing=False, name=None, ticker=None, cik=None, save=False, local_file_path='/temp'):
        if not self.connected:
            logger.error(self.status)
            quit()

        start_time = time.time()

        query = [{'$unwind': '$edgar_path'},
                 {'$match': {'edgar_path.log': {'$eq': None}}},
                 {'$match': {'edgar_path.form': {'$in': ['10-K', '10-Q']}}}]

        # add some other criterion
        if cik:
            query.append(
                {'$match': {'_id': {'$in': [cik] if type(cik) == str else cik}}})
        if ticker:
            query.append(
                {'$match': {'ticker': {'$in': [ticker] if type(ticker) == str else ticker}}})
        if name:
            query.append(
                {'$match': {'name': {'$in': [name] if type(name) == str else name}}})

        # noinspection PyTypeChecker
        query.append({'$project': {'_id': 0,
                                   'cik': '$_id',
                                   'name': 1,
                                   'url': '$edgar_path.path',
                                   'form': '$edgar_path.form',
                                   'date': '$edgar_path.date'}})

        # execute download for each edgar_path
        tasks = []
        for row in self.col.aggregate(query):
            row['save'] = save
            row['local_file_path'] = local_file_path
            tasks.append(row)

        if len(tasks) == 0:
            logger.debug('no more filings!')
            quit()

        def store_result(res):
            if type(data) == str:
                if 'error' in data:
                    self.col.update({'_id': data['cik'], 'edgar_path.path': data['edgar_path']},
                                    {'$set': {'edgar_path.$.log': 'error'}}, False, True)
            else:
                try:
                    self.col.update_one(**data['query'])
                except TypeError:
                    pprint(data['query'])
                    quit()

                self.col.update({'_id': data['cik'], 'edgar_path.path': data['edgar_path']},
                                {'$set': {'edgar_path.$.log': 'stored'}}, False, True)
            
            logger.info(" verstrichen: %s min\tVerarbeitet: %s Stücke" % (round((time.time() - start_time) / 60), i))

        i = 1
        if not multiprocessing:
            logger.debug('use synchronious mode')
            for row in tasks:
                logger.debug("task - name: %s url: %s" % (row['name'], row['url']))
                data, t = self.mp_ffw(**row)
                # logger.debug("data: %s" % data)
                store_result(data)
                i += 1
                self.session['downloaded files'] += 1
                ctime(t)

        else:

            worker = 10 if multiprocessing is bool else multiprocessing
            with Pool(worker) as pool:

                imap_unordered_it = pool.imap_unordered(
                    SecDigger.calculatestar, tasks)

                i = 0
                print('Unordered results using pool.imap_unordered():')
                for data, t in imap_unordered_it:
                    print(data['edgar_path'])
                    store_result(data)
                    i += 1
                    self.session['downloaded files'] += 1
                    ctime(t)

    def __str__(self):
        """print all abaut this session"""
        l = ''
        for key, value in self.session.items():
            l += '%s:\t%s\n' % (key, value)
        return l


if __name__ == '__main__':
    """lade IDX herunter und seicher diese in DB"""
    # use SecDigger
    sd = SecDigger()

    # set debug level
    sd.loggingBasicConfig(level=logging.DEBUG)

    # connect to Database
    sd.connect(database='sec_digger', collection='stocks')


# edgar/data/1000045/0001193125-11-216128.txt'
