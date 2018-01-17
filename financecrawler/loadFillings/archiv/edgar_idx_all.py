'''
Created on 04.02.2017

@author: olli
'''
import datetime
import requests
import sqlite3
import zipfile
import io

# Generate the list of quarterly zip files archived in EDGAR since
# start_year (earliest: 1993) until the most recent quarter
current_year = datetime.date.today().year
current_quarter = (datetime.date.today().month - 1) // 3 + 1
start_year = 1993
years = list(range(start_year, current_year))
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
history = [(y, q) for y in years for q in quarters]
for i in range(1, current_quarter):
    history.append((current_year, 'QTR%d' % i))
quarterly_files = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/xbrl.zip' % (x[0], x[1]) for x in history]
quarterly_files.sort()
# add the most recent quarter
quarterly_files.append('https://www.sec.gov/Archives/edgar/full-index/xbrl.zip')

# Download index files and write content into SQLite
con = sqlite3.connect('edgar_idx.db')
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS idx')
cur.execute('CREATE TABLE idx (cik TEXT, '
            'conm TEXT, '
            'type TEXT, '
            'date TEXT, '
            'path TEXT PRIMARY KEY'
            'clean TEXT)')

for url in quarterly_files:
    request = requests.get(url)
    file = zipfile.ZipFile(io.BytesIO(request.content))
    with file.open('xbrl.idx') as z:
        for line in z: 
            if '----' in line.decode('latin-1'):
                break
        records = [tuple(line.decode('latin-1').rstrip().split('|')) 
                    for line in z]

    cur.executemany('INSERT OR IGNORE INTO idx VALUES (?, ?, ?, ?, ?, NULL)', records)
    print(url, 'downloaded and wrote to SQLite')
 
con.commit()
con.close()

    
    
    
    
    