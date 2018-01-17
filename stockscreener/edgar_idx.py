#!/usr/bin/env python3.6
'''
Created on 04.02.2017

@author: Oliver Haag
'''
import datetime
import requests
import pymongo
import io
from pprint import pprint
from collections import defaultdict
from urllib.request import urlopen
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
from urllib.request import urlopen, build_opener
from zipfile import ZipFile

from mongo_db import MongoDigger

class SecIdx(MongoDigger):
    def __init__(self):
        super().__init__()
        self.idx = []
        self.session = {}

    def download_idx(self, whole=True, verbose=False, quarterly_files=list()):
        """if whole then 1993 until the most recent quarter"""

        if type(quarterly_files) is not list:
            raise TypeError('expect list!')

        current_year = datetime.date.today().year
        current_quarter = (datetime.date.today().month - 1) // 3 + 1

        if whole and len(quarterly_files) == 0:
            start_year = 1993
            years = list(range(start_year, current_year))
            quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
            history = [(y, q) for y in years for q in quarters]
            for i in range(1, current_quarter):
                history.append((current_year, 'QTR%d' % i))
            quarterly_files = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/xbrl.zip' % (x[0], x[1]) for x in
                               history]
            quarterly_files.sort()
            quarterly_files.append('https://www.sec.gov/Archives/edgar/full-index/xbrl.zip')

            if verbose:
                print('Start year: 1993')

        elif quarterly_files is None:
            if current_quarter == 1:
                last_quarter = 4
                last_year = current_year - 1

            else:
                last_quarter = current_quarter - 1
                last_year = current_year

            quarterly_files = [
                'https://www.sec.gov/Archives/edgar/full-index/%d/QTR%s/xbrl.zip' % (last_year, last_quarter),
                'https://www.sec.gov/Archives/edgar/full-index/xbrl.zip']

            if verbose:
                print('Start -> Year: %s Quarter: %s' % (last_year, last_quarter))

        for url in quarterly_files:
            print(url)
            try:
                s = requests.Session()
                s.trust_env = False
                response = s.get(url, stream=True)
                if response.status_code == 503:
                    response.raise_for_status()
            except requests.exceptions.HTTPError:
                print("oops something unexpected happened!", url)
                continue

            with ZipFile(BytesIO(response.content)) as zfile:
                with zfile.open('xbrl.idx') as z:
                    for line in z:
                        if '----' in line.decode('latin-1'):
                            break
                    self.idx.extend([tuple(line.decode('latin-1').rstrip().split('|')) for line in z])

            if verbose:
                print('File downloaded')

    def save_idx(self):
        """save idx to mongodb"""

        if self.col == 'Not connected to database!':
            print(self.col)

        elif len(self.idx) == 0:
            print('need files!')

        else:
            idx_dict = defaultdict(dict)
            print("processing...")
            for cik, name, form, date, path in self.idx:
                # acc = path.split('/')[-1][:-4]
                # self.col.update({'_id': cik},
                #                 {'$set': {'name': name,
                #                           'edgar_path.' + acc + '.form': form,
                #                           'edgar_path.' + acc + '.date': date,
                #                           'edgar_path.' + acc + '.log': None}},
                #                 upsert=True)

                self.col.update({'_id': cik},
                                {'$set': {'name': name},
                                 '$addToSet': {'edgar_path': {
                                                'form': form,
                                                'date': date,
                                                'path': path,
                                                'log': None}}},
                                upsert=True)
            print("saved all paths")

    def __str__(self):
        if len(self.idx) == 0:
            return 'no files!'
        else:
            return 'paths: %s' % len(self.idx)


if __name__ == '__main__':
    i = SecIdx()
    i.save_idx() # Not connected to database!
    print(i)  # no files!
    i.download_idx(verbose=True) #, quarterly_files=['https://www.sec.gov/Archives/edgar/full-index/2012/QTR3/xbrl.zip', ])
    print(i) # paths: NUMBER
    i.save_idx()  # Not connected to database!
    i.connect(database='sec_digger', collection='stocks')
    i.save_idx()
    print("finish")
