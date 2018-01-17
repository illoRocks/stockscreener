'''
Created on 06.02.2017

@author: olli
'''

import datetime
import requests
import sqlite3
import zipfile
import io
  
# Generate the list of quarterly zip files archived in EDGAR
current_year = datetime.date.today().year
current_quarter = (datetime.date.today().month - 1) // 3 + 1

if current_quarter == 1:
    last_quarter = 4
    last_year = current_year - 1
else:
    last_quarter = current_quarter - 1
    last_year = current_year
    
quarterly_files = ['https://www.sec.gov/Archives/edgar/full-index/%d/QTR%s/xbrl.zip' % (last_year, last_quarter),
                   'https://www.sec.gov/Archives/edgar/full-index/xbrl.zip']

# Download index files and write content into SQLite
con = sqlite3.connect('edgar_idx.db')
cur = con.cursor()
 
for url in quarterly_files:
    request = requests.get(url)
    file = zipfile.ZipFile(io.BytesIO(request.content))
    with file.open('xbrl.idx') as z:
        for line in z: 
            if '-----' in line.decode('latin-1'):
                break
        records = [tuple(line.decode('latin-1').rstrip().split('|')) 
                    for line in z]
 
    cur.executemany('INSERT OR IGNORE INTO idx VALUES (?, ?, ?, ?, ?)', records)
    print(url, 'downloaded and wrote to SQLite')
  
con.commit()
con.close()


