#!/usr/bin/env python3.6

'''
Created on 06.02.2017

@author: olli
'''
import multiprocessing
import os
import re
import time
from _collections import defaultdict
from datetime import datetime
from re import search
from xml.sax import make_parser

import pymongo

from archiv.sax_xbrl import xbrlHandler
from archiv.writelog import log

start_time = time.time()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
logpath = os.path.join(BASE_DIR, "logs/log_mongo.log")
local_idx = os.path.join(BASE_DIR, "logs/local_index.txt")
file_path = '/media/daten/financecrawler/files/'

# Connection to Mongo DB
try:
    conn = pymongo.MongoClient()
    print("Connected successfully!!!", conn)
except:
    print("Could not connect to MongoDB: %s")
db = conn.fin_db
col = db.fil_col

# Dateipfade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "edgar_idx.db")
path = '/media/daten/financecrawler/files/edgar/data'

# Suche alle xml dateien, die noch nicht gespeichert sind
existing_mdb = col.find({}, {'accessions': 1})
existing = []
for e in existing_mdb:
    existing.extend(e['accessions'])

print('Ordner durchsuchen...')
files = []
if False:
    for entries in os.scandir(path):
        for entry in os.scandir(entries):
            if entry not in existing:
                files.extend([f.path for f in os.scandir(entry)
                              if '.xml' in f.name and
                              not search('(FilingSummary|\.xsd|defnref|(pre|lab|def|cal|ref|R[0-9]{3})\.xml)', f.name)])
                
    # write index list
    with open('logs/local_index.txt', 'w') as thefile:
        for item in files:
            thefile.write("%s\n" % item)
else:
    with open('logs/local_index.txt', 'r') as thefile:
        for item in thefile:
            a = item.split('/')[-2]
            if a not in existing:
                files.append(item.replace('\n',''))

# quit()


def read_xbrl(roots, output = None):
    #gehe jede xml durch
    accession = roots.split('/')[-2]
    cik = roots.split('/')[-3]
    filename = roots.split('/')[-1]
    docDate = re.split('-|\.',filename)[1]
    docDate = datetime.strptime(docDate, "%Y%m%d")
    
    # clean xml
#     f.replace('.xml', '.log')
    with open(roots, 'r') as f:
        xml_as_string = f.read()
    xml_as_string = re.sub('(<link:footnoteLink((.|\n)*?)footnoteLink>)', '', xml_as_string)
    linebreak = re.findall('</((.|\n)*?)>', xml_as_string)
    for b in linebreak:
        cleaned = re.sub('\n', '', b[0])
        xml_as_string = re.sub(b[0], cleaned, xml_as_string)
    xml_as_string = re.sub('&', '', xml_as_string)
    xml_as_string = re.sub('(us.{1,4}gaap:)', 'us-gaap:', xml_as_string)
    with open(roots, 'w') as f:
        f.write(xml_as_string)

    # start parser
    parser = make_parser()
    b = xbrlHandler()
    parser.setContentHandler(b)
    try:
        parser.parse
    except Exception as inst:
        log(logpath, "ParserException:", roots, inst.args)
        return "ParserException"

    # Daten sortieren und in collection speichern
    def exist(dic, key, val):
        """prüfe ob wert in xml vorhanden ist und speicher in in dict"""
        if val in b.getData()['misc']:
            dic[key] = b.getData()['misc'][val]
        else:
            print('! '+val+' konnte nicht gefunden werden')

    content = defaultdict(dict)
    for ref, values in b.getData()['data'].items():
        for item in values:
            content['fillings.'+item].setdefault('$each', []).append({**b.getData()['context'][ref],# startDate and endDate
                                                                      'updated': docDate,
                                                                      'value': float(b.getData()['data'][ref][item])})

    data = {'filter': {'_id': cik},
            'update': {"$set": {'lastDocument': docDate,
                                'lastUpdate': datetime.today()},
                       '$push': {**content,
                                 'accessions': accession},
                       '$inc': {'NumberOfDocuments': 1}},
            'upsert': True}
    
    exist(data['update']['$set'], 'entityRegistrantName', 'entityregistrantname')
    exist(data['update']['$set'], 'commonStockDescription', 'commonstockdescription')
    exist(data['update']['$set'], 'currentFiscalYearEndDate', 'currentfiscalyearenddate')
#     pprint(data)
    if output is not None:
        output.put(data)

files = '/media/daten/financecrawler/files/edgar/data/1301611/0001144204-15-008393/lpnt-20141231.xml'
print(files)
read_xbrl(files)
quit()


def calculate(func, args):
    return func(*args)


def calculatestar(args):
    return calculate(*args)

PROCESSES = 5
print('Creating pool with %d processes\n'
        'Number of files: %s\n'
        'Gestartet: %s\n' % (PROCESSES,len(files), time.strftime("%d.%m.%Y %H:%M:%S")))
i = 1
with multiprocessing.Pool(PROCESSES) as pool:
    m = multiprocessing.Manager()
    q = m.Queue()
    TASKS = [(read_xbrl, (root, q)) for root in files]
    
    imap_unordered_it = pool.imap_unordered(calculatestar, TASKS)
    for x in imap_unordered_it:
        if x is not None: print(x)
        print(" verstrichen: %s min" % (round((time.time() - start_time)/60)))
        print(" Verarbeitet: %s Stücke" % i)
        _id = col.update_one(**q.get())
        i += 1

conn.close()

