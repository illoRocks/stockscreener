#!/usr/bin/env python3.6
'''
Created on 06.02.2017

@author: olli
'''
import os.path
import sqlite3
import time
from pathlib import Path
from re import search
from urllib.request import urlopen

import gevent
import gevent.queue
from gevent import monkey

from archiv.writelog import log

start_time = time.time()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "edgar_idx.db")
logpath = os.path.join(BASE_DIR, "logs/log_secfiles.log")
file_path = '/media/daten/financecrawler/files/'

with sqlite3.connect(db_path) as con:
    cur = con.cursor()
    t = ('10-K','10-Q')
    cur.execute('SELECT type, cik, conm, path '
                'FROM idx WHERE type in (?,?) LIMIT 5500', t)

def check_dir(r):
    path = Path(file_path+r[3][:-4])
    if path.is_dir():
        return False
    else:
        return True

rows = [u for u in cur if check_dir(u)]

# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all()

output = gevent.queue.Queue()

# define a example function
def get_files(row, file_path, output):
    """download and save sec files"""
    func_time = time.time()

    url = 'https://www.sec.gov/Archives/' + row[3]
    output.put(url)

    try:
        resp = urlopen(url)
    except Exception as inst:
        print("URL-Exception: "+url)
        log(logpath, "URL-Exception: ", url, inst.args)
        return
    
    try:
        lines = [l.decode('utf-8') for l in resp]
    except Exception as inst:
        print("Decode-Exception: "+url)
        log(logpath, "Decode-Exception: "+url)
        return
    content_header = ''
    xbrl = False
    content_xbrl = []
    header = False
    for line in lines:
        """suche nach XML-Datei und Header"""
        if xbrl: new_xbrl[1] += line 
        if search('(<FILENAME>|<filename>)', line): 
            filename = line[10:-1]
        elif not header and search('(<SEC-HEADER>|<sec-header>)', line):
            # store header
            header = True
        elif header and search('(</SEC-HEADER>|</sec-header>)', line):
            # end header
            header = False
            content_header += line
        elif not xbrl and search('(<xbrl>|<XBRL>)', line) and not search('(FilingSummary|\.xsd|defnref|(pre|lab|def|cal|ref|R[0-9]{3})\.xml)', filename) and len(filename) >= 8: 
            xbrl = True
            new_xbrl = [filename, '']
        elif xbrl and search('(</xbrl>|</XBRL>|</xbrli:xbrl>)', line) and xbrl: 
            xbrl = False
            content_xbrl.append(new_xbrl)
        if header: content_header += line
    
    p = Path(file_path+row[3][:-4]+'/header.txt')
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w') as f:
        f.write(content_header)
#     print(' files/%s/header.txt' % row[3][:-4])
    
    for c in content_xbrl:
        p = Path(file_path+row[3][:-4]+'/'+c[0])
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('w') as f:
            f.write(c[1])
        print(' files/%s/%s' % (row[3][:-4], c[0]))
    output.put(time.time() - func_time)

# Setup a list of processes that we want to run

jobs = [gevent.spawn(get_files, *(x, file_path, output)) for x in rows[0:10]]

# Exit the completed processes
gevent.joinall(jobs)

# output.put(StopIteration)
for item in output:
    print(item)
print(" verstrichen: %s min" % (round((time.time() - start_time)/60)))

