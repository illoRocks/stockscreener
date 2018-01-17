#!/usr/bin/env python3.6
'''
Created on 06.02.2017

@author: olli
'''
import os.path
import sqlite3
from urllib.request import urlopen
from pathlib import Path
from re import search
import time
from logging import log

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "edgar_idx.db")
logpath = os.path.join(BASE_DIR, "logs/log_secfiles.log")
spath = '/media/daten/financecrawler/files/'

with sqlite3.connect(db_path) as con:
    cur = con.cursor()
    t = ('10-K','10-Q')
    cur.execute('SELECT type, cik, conm, path '
                'FROM idx WHERE type in (?,?) LIMIT 5000', t)

# download and save sec files
i = 1
tempfile = ''
header = False
content_header = ''
html = False
content_html = []
xbrl = False
content_xbrl = []

start_time = time.time()
for row in cur:
    t1 = time.time()
    path = Path(spath+row[3][:-4])
    if path.is_dir():
        continue
    
    url = 'https://www.sec.gov/Archives/' + row[3]
    print(str(i) + ': ' + url)
    i += 1
    
    t2 = time.time()
    try:
        resp = urlopen(url)
    except Exception as inst:
        print("URL-Exception: "+url)
        log(logpath, "URL-Exception: ", url, inst.args)
        continue
    
    t3 = time.time()

    try:
        lines = [l.decode('utf-8') for l in resp]
    except Exception as inst:
        print("Decode-Exception: "+url)
        log(logpath, "Decode-Exception: "+url)
        continue
    t4 = time.time()
#     print(t4-t3)    
 
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
        
#     t5 = time.time()
    
# Temporäre file speichern?
#     p = Path(spath+'temp.txt')
#     p.parent.mkdir(parents=True, exist_ok=True)
#     with p.open('w') as f:
#         f.write(tempfile)
#     tempfile = ''
    
    p = Path(spath+row[3][:-4]+'/header.txt')
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w') as f:
        f.write(content_header)
    print(' files/%s/header.txt' % row[3][:-4])
    content_header = ''
    
    for c in content_xbrl:
        p = Path(spath+row[3][:-4]+'/'+c[0])
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('w') as f:
            f.write(c[1])
        print(' files/%s/%s' % (row[3][:-4], c[0]))
    content_xbrl = []
    
    t6 = time.time()

    print(" verstrichen:           %s min" % (round((time.time() - start_time)/60)))
#     print(" Prüfe Datei vorhanden: %s sec " % (t2 - t1))
#     print(" Download:              %s sec " % (t3 - t2))
#     print(" Decodieren:            %s sec " % (t4 - t3))
#     print(" Verarbeite Datei:      %s sec " % (t5 - t4))
#     print(" Speicher XML:          %s sec " % (t6 - t5))
#     break

