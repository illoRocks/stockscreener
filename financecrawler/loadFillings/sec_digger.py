#!/usr/bin/env python3.6
from download_filings import DownloadFilings
from mongo_db import MongoDigger
import datetime
import requests
import zipfile
import io
from edgar_idx import SecIdx
from pprint import pprint
import time
from multiprocessing import Pool


def ctime(t, digit=1):
    summary = 'Verbrauchte Zeit: '
    w = False
    n = 1
    if type(t) == list:
        for s in t:
            if w:
                summary += 't%s-%s\t' % (n, round(s-w, digit))
            w = s
            n += 1
    elif type(t) == dict:
        for s in t:
            if w:
                summary += '%s - %ssec | \t' % (s, round(t[s]-w, digit))
            w = t[s]
            n += 1
    else:
        print('TypeError: variable is %s. It must be dict or list!' % type(t))
        return
    summary += '\t' + str(type(t))
    print(summary)

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


class SecDigger(SecIdx, MongoDigger):
    """Handler for SEC-filings"""

    def __init__(self):
        super().__init__()
        self.session = {'connection': 'not connected!',
                        'downloaded files': 0}
        self.local_file_path = 'temp'

    @staticmethod
    def calculatestar(kwargs):
        return SecDigger.mp_ffw(**kwargs)

    @staticmethod
    def mp_ffw(save=False, verbose=False, **kwargs):
        """create Download-Handler"""

        t = {'start': time.time()}

        if verbose: print('create DownloadFillings')
        df = DownloadFilings(**kwargs)
        if verbose: print('start DownloadFillings.download')
        res = df.download(verbose=verbose)
        t['download'] = time.time()
        if type(res) == str:
            return res
        if save:
            p = '/temp' if 'local_file_path' not in kwargs else '/' + kwargs['local_file_path']
            p += '' if 'cik' not in kwargs else '/' + kwargs['cik']
            df.save_documents(p)
            t['save'] = time.time()
        result = df.parse()
        t['parse'] = time.time()

        return result, t

    def get_files_from_web(self, multiprocessing=False, name=None, ticker=None, cik=None, save=False, verbose=False):
        if self.col == 'Not connected to database!':
            print(self.col)
            return

        start_time = time.time()

        query = [{'$unwind': '$edgar_path'},
                 {'$match': {'edgar_path.log': {'$eq': None}}},
                 {'$match': {'edgar_path.form': {'$in': ['10-K', '10-Q']}}}]

        # add some other criterion
        if cik:
            query.append({'$match': {'_id': {'$in': [cik] if type(cik) == str else cik}}})
        if ticker:
            query.append({'$match': {'ticker': {'$in': [ticker] if type(ticker) == str else ticker}}})
        if name:
            query.append({'$match': {'name': {'$in': [name] if type(name) == str else name}}})

        # noinspection PyTypeChecker
        query.append({'$project': {'_id': 0,
                                   'cik': '$_id',
                                   'name': 1,
                                   'url': '$edgar_path.path',
                                   'form': '$edgar_path.form',
                                   'date': '$edgar_path.date'}})
        if verbose:
            print(query)
        # execute download for each edgar_path

        tasks = []
        for row in self.col.aggregate(query):
            row['save'] = save
            row['verbose'] = verbose
            tasks.append(row)
            # row['local_file_path'] = self.local_file_path

        if len(tasks) == 0:
            print('no more filings!')
            quit()

        def store_result(res):
            if type(data) == str:
                print(data)
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

            print(" verstrichen: %s min" % (round((time.time() - start_time) / 60)))
            print(" Verarbeitet: %s Stücke" % i)

        i = 1
        if not multiprocessing:
            for row in tasks:
                print(row)
                data, t = self.mp_ffw(**row)
                store_result(data)
                i += 1
                self.session['downloaded files'] += 1
                ctime(t)

        else:

            worker = 10 if multiprocessing is bool else multiprocessing
            with Pool(worker) as pool:

                imap_unordered_it = pool.imap_unordered(SecDigger.calculatestar, tasks)

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
    m = SecDigger()
    m.connect(database='sec_digger', collection='stocks')
    # m.download_idx(verbose=True)#, quarterly_files=['https://www.sec.gov/Archives/edgar/full-index/2012/QTR3/xbrl.zip', ])
    # print(m)
    # m.save_idx()
    # print(m)
    m.get_files_from_web(multiprocessing=False, verbose=False)#, cik='796343')#, save=False)  # eingrenzug
    print('\n', m)
    # pfad aus der Datenbank ziehen und danach log = 'stored'

# edgar/data/1000045/0001193125-11-216128.txt'
