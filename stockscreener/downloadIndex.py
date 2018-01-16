from connect import getDb
import datetime
import requests

''' TODO letztes Quartal muss jedes mal heruntergeladen werden '''


def start():
  ''' Generate the list of index files archived in EDGAR since start_year (earliest: 1993) until the most recent quarter '''
  
  current_year = datetime.date.today().year
  current_quarter = (datetime.date.today().month - 1) // 3 + 1
  start_year = 1993
  years = list(range(1993, current_year))
  quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
  history = [(y, q) for y in years for q in quarters]
  for i in range(1, current_quarter + 1):
      history.append((current_year, 'QTR%d' % i))
  urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/master.idx' % (x[0], x[1]) for x in history]
  urls.sort()
  last = urls[-2:]

  # check schon vorhandene Indizes
  db = getDb()
  existing = db.secIndex.distinct("parrentUrl")
  urls = [item for item in urls if item not in existing]

  # letzen zwei Listen müssen jedes mal mit heruntergeladen werden
  urls.extend(last)
  urls = list(set(urls))

  # lade alle Indizes runter
  for url in urls[:5]:
    lines = requests.get(url).text.splitlines()
    records = [tuple(line.split('|')) for line in lines[11:]]
    records = [{'cik': rec[0], 'conm': rec[1], 'type': rec[2], 'date': rec[3], 'path': rec[4], 'parrentUrl': url} for rec in records]
    db.secIndex.insert_many(records)
    print(url, 'downloaded and wrote to MongoDB')
  


if __name__ == "__main__":
  print("starte Programm")
  start()

