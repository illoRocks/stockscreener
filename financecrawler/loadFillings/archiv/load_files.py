#!/usr/bin/env python3.6
'''
Created on 06.02.2017

@author: olli
'''

import os.path
import sqlite3
from pathlib import Path
from re import search
import time
import multiprocessing
import requests
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "edgar_idx.db")
logpath = os.path.join(BASE_DIR, "logs/log_secfiles.log")
file_path = '/media/daten/financecrawler/files'


def check_dir(r):
    path = Path(file_path + '/' + r[:-4])
    if path.is_dir():
        return False
    else:
        return True


def get_files(row, path, verbose=False):
    """download and save sec files"""

    url = 'https://www.sec.gov/Archives/' + row

    if verbose:
        print(url, '...download file')

    resp = requests.get(url, stream=True)

    if verbose:
        print('...search for XBRL and save it')

    try:

        xbrl = False
        header = False
        for line in resp.iter_lines():
            """suche nach XML-Datei und Header"""

            if xbrl:
                xbrl_file.write('%s\n' % line.decode("utf-8"))

            if not header and not xbrl and search(b'(<FILENAME>|<filename>)', line):
                filename = line[10:].decode("utf-8")

            elif not header and search(b'(<SEC-HEADER>|<sec-header>)', line):
                file_dir = '/'.join([path, row[:-4], 'header.txt'])
                os.makedirs(os.path.dirname(file_dir), exist_ok=True)
                header_file = open(file_dir, 'w')
                header = True

            elif header and search(b'(</SEC-HEADER>|</sec-header>)', line):
                header_file.write('%s\n' % line.decode("utf-8"))
                header = False

            elif not xbrl and \
                    search(b'(<xbrl>|<XBRL>)', line) and \
                    len(filename) >= 8 and \
                    not search('(FilingSummary|\.xsd|defnref|(pre|lab|def|cal|ref|R[0-9]{3})\.xml)', filename):
                xbrl = True
                file_dir = '/'.join([path, row[:-4], filename])
                os.makedirs(os.path.dirname(file_dir), exist_ok=True)
                xbrl_file = open(file_dir, 'w')

            elif xbrl and search(b'(</xbrl>|</XBRL>|</xbrli:xbrl>)', line) and xbrl:
                xbrl = False
                xbrl_file.close()

            if header:
                header_file.write('%s\n' % line.decode("utf-8"))

        return {'finished': row}

    except requests.exceptions.ChunkedEncodingError:

        shutil.rmtree('/'.join([path, row[:-4]]))
        return {'error': row}


def calculate(func, args):
    result = func(*args)
    return result


def calculatestar(args):
    return calculate(*args)


def load_files(processes=15, limit=False, file=False):
    start_time = time.time()

    if not file:

        print('... verbinde mit Datenbank')
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT path "
                        "FROM idx "
                        "WHERE type IN ('10-K', '10-Q') AND urlError IS NULL")

        print('... überprüfe, ob Datei schon vorhanden')
        rows = [u for u, in cur if check_dir(u)]

        if limit:
            rows = rows[:limit]

    else:

        rows = [file, ]
        print(rows)

    if processes == 1:
        print(
            'Starte sequentiellen Prozess\n'
            'Number of files: %s\n'
            'Gestartet: %s' % (len(rows), time.strftime("%d.%m.%Y %H:%M:%S")))

        for r in rows:
            res = get_files(r, file_path, True)
            print(res)
            break
        return

    else:

        print(
            'Creating pool with %d processes\n'
            'Number of files: %s\n'
            'Gestartet: %s' % (processes, len(rows), time.strftime("%d.%m.%Y %H:%M:%S")))

        with multiprocessing.Pool(processes) as pool:
            tasks = [(get_files, (x, file_path)) for x in rows]

            imap_unordered_it = pool.imap_unordered(calculatestar, tasks)

            i = 1
            err = []
            print('Unordered results using pool.imap_unordered():')
            for x in imap_unordered_it:
                print(x)
                if 'finished' not in x:
                    print('an error occurred!')
                    err.append(x)
                print(" verstrichen: %s min" % (round((time.time() - start_time) / 60)))
                print(" Verarbeitet: %s Stücke" % i)
                i += 1

        print('... speicher %s URL-Errors' % len(err))
        with sqlite3.connect(db_path) as con:
            cur = con.cursor()
            sql = 'UPDATE idx SET urlError = "yes" WHERE path in ({seq})'.format(seq=','.join(['?'] * len(err)))
            cur.execute(sql, err)
            con.commit()

    print("\nFertig...")


if __name__ == '__main__':
    n = 1
    t0 = time.time()
    for i in range(n): load_files(processes=1, limit=1, file='edgar/data/796343/0001104659-05-047297.txt')
    t1 = time.time()

    total_n = t1 - t0
    print(total_n)














