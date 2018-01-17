#!/usr/bin/env python3.6

'''
Created on 25.02.2017

@author: olli
'''
# import sys
# sys.path.append("..")
import os
import re
import time
import sqlite3
import multiprocessing

start_time = time.time()

# Wo werden die Berichte gespeichert?
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "edgar_idx.db")

path = '/media/daten/financecrawler/files/edgar/data'

# Schon bereinigte Dateien suchen
with sqlite3.connect(db_path) as con:
    cur = con.cursor()
    cur.execute('SELECT path, clean '
                'FROM idx '
                'WHERE clean = "yes"')
cleaned = [p.replace('.txt', '') for p, c in cur]

# Suche alle xml dateien
roots_xml = []
append = roots_xml.append
for root, dirs, files in os.walk(path):
    for f in files:
        if '.xml' in f and root.replace('/media/daten/financecrawler/files/', '') not in cleaned:
            append((root, f))

n = 1
prepared = []
def clean_xml(root, file, output):
    """ clean xml """
    file_path = '%s/%s' % (root, file)
    
#     func_start = time.time()
    with open(file_path, 'r') as f:
        xml_as_string = f.read()
        
    xml_as_string = re.sub('(<link:footnoteLink((.|\n)*?)footnoteLink>)', '', xml_as_string)
    xml_as_string = re.sub('&', '', xml_as_string)
    xml_as_string = re.sub('(us.{1,4}gaap:)', 'us-gaap:', xml_as_string) 
    
    linebreak = re.findall('</((.|\n)*?)>', xml_as_string)
    for b in linebreak:
        cleaned = re.sub('\n', '', b[0])
        xml_as_string = re.sub(b[0], cleaned, xml_as_string)

    with open(file_path, 'w') as f:
        f.write(xml_as_string)
        
    output.put(root)

def calculate(func, args):
    result = func(*args)
    return result

def calculatestar(args):
    return calculate(*args)

PROCESSES = 5
print('Creating pool with %d processes\n'
        'Number of files: %s\n'
        'Gestartet: %s' % (PROCESSES,len(roots_xml), time.strftime("%d.%m.%Y %H:%M:%S")))

with multiprocessing.Pool(PROCESSES) as pool:
    m = multiprocessing.Manager()
    q = m.Queue()  
    TASKS = [(clean_xml, (root, file, q)) for root, file in roots_xml]
    
    imap_unordered_it = pool.imap_unordered(calculatestar, TASKS)
    i = 1
    fin = []
    print('Unordered results using pool.imap_unordered():')
    for x in imap_unordered_it:
        fin.append(q.get())
        print(" verstrichen: %s min" % (round((time.time() - start_time)/60)))
        print(" Verarbeitet: %s Stücke" % i)
        if i % 100 == 0:
            fin = [f.replace('/media/daten/financecrawler/files/', '') for f in fin]
            fin = [f + '.txt' for f in fin]
            with sqlite3.connect(db_path) as con:
                cur = con.cursor()
                sql = 'UPDATE idx SET clean = "yes" WHERE path in ({seq})'.format(seq=','.join(['?']*len(fin)))
                cur.execute(sql, fin)
                con.commit()
            print('Fortschritt gespeichert')
            fin = []
        i += 1





