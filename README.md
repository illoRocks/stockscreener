# stockscreener

Download XBRL from the SEC and store it to MongoDB or as local files.

## Features

* Optimized for multiprozessing
* MongoDB as Database

### Dependencies

* pymongo

## Usage

Make sure that MongoDB is running on your machine!

### 1. Initialize the Database

Download all paths from 1993 from EDGAR and save it to MongoDB

```python
from stockscreener.sec_digger import SecDigger

sd = SecDigger()

# connect to Database
sd.connect(database='sec_digger', collection='stocks')

# Init Database / apply only once!
sd.download_idx()
sd.save_idx()
```

if database is allready initialized download only the current and last quarter

```python
sd.download_idx(whole=False)
sd.save_idx()
```

### 2.1 Download Reports from the EDGAR server and save it to MongoDB | Singleprocess

Specify the company with `cik`, `ticker` or `name`. It should be a valid EDGAR string. Check the existing database or the sec website for this. Specify only one identifier. If more are given cik will be used.

```python
import os
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

options = {
  'cik': '796343',
  'save': True,
  'local_file_path': '%s/xbrl' % WORKING_DIR
}
sd.get_files_from_web(**options)
```

If save is true the xbrl will be written on the `local_file_path`. Please use a absolut path!

The report will automaticly written on the given collection. You have to use the same credentials as befor.

### 2.2 Download Reports from the EDGAR server and save it to MongoDB | Multiprocessing

not tested!

### Configure the Handler

#### Set logging options

use the [options](https://docs.python.org/3/library/logging.html) from logging module

```python
sd.loggingBasicConfig(
  level=logging.DEBUG,
  format='%(levelname)s/%(module)s/%(funcName)s %(message)s'
  )
```

### ROADMAP

* make the financial positions more readable and useable for further analyses
* improve logging system
* command line interface
* easy to use as a cronjob
* pip

## Example Schema

```json
// collection: stocks
{
"_id" : "796343",
  "edgar_path" : [
    {
      "log" : null,
      "form" : "8-K",
      "path" : "edgar/data/796343/0001104659-05-040250.txt",
      "date" : "2005-08-18"
  }
  ],
  "name" : "ADOBE SYSTEMS INC",
  "lastDocument" : "2006-10-11",
  "lastUpdate" : "2018-01-18T19:27:47.797+07:00",
  "NumberOfDocuments" : 5,
  "fillings" : {
    "DeferredIncomeTaxes" : [
      {
        "endDate" : "2005-09-02",
        "startDate" : "2004-12-04",
        "value" : -40293000.0,
        "updated" : "2005-10-05"
      },
      {
        "updated" : "2006-02-08",
        "startDate" : "2003-11-29",
        "endDate" : "2004-12-03",
        "value" : 46270000
      }
    ]
  }
}
```

Take account of values for a position with the same `startDate` and `endDate`. The `updated`field show you the latest.

## LICENSE

Please feel free to use this software for non-commercial projects!

[![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/2.0/de/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/2.0/de/)
This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 2.0 Germany License](http://creativecommons.org/licenses/by-nc-sa/2.0/de/)