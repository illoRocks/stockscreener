# stockscreener

Download XBRL from the SEC and store it to MongoDB or as local files.

This project is under activ development!

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

# connect to MongoDB
sd.connect(
    host='localhost',
    port=27017
)

# Init Database / apply only once!
sd.download_idx(
  init=True
)
sd.save_idx()
```

if database is allready initialized download only the current and last quarter

```python
sd.download_idx()
sd.save_idx()
```

### 2.1 Download Reports from the EDGAR server and save it to MongoDB | Singleprocess

Specify the company with `cik`, `ticker` or `name`. It should be a valid EDGAR string. Check the existing database or the sec website for this. Specify only one identifier. If more are given then `cik` will be used. Identifier could be a string or an array with strings.

```python
import os
WORKING_DIR = os.path.dirname(os.path.abspath(__file__))

sd.get_files_from_web(
  cik='796343',
  save=True,
  local_file_path='%s/test' % WORKING_DIR,
  save_to_db=True
)
```

If `save=True` then the xbrl file will be written on the `local_file_path`. Please use a absolut path! If you only want to download the files and save it to local storage `save_to_db=False` as option. Use `number_of_files` as argument for limitation of downloads.

### 2.2 Download Reports from the EDGAR server and save it to MongoDB | Multiprocessing

specify the company: read 2.1

`multiprocessing` could be boolean or integer. If boolean then the program use 4 worker by default else the programm use the the given integer for numbers of worker.

```python
sd.get_files_from_web(
    cik='796343',
    multiprocessing=8
)
```

### logging

use the [options](https://docs.python.org/3/library/logging.html) from logging module

write it on top of your script

```python
import logging

logging.basicConfig(
    level=logging.DEBUG
)
```

Logging system is not well implemented for multiprocessing!

### ROADMAP

* make the financial positions / database more readable
* improve logging system
* parse local xbrl
* database to CSV
* command line interface
* easy setup for automated process
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

## Usefull queries

### Unwind EDGAR paths

```javascript
db.edgarPath.aggregate([
    {'$unwind': '$edgar_path'},
    {'$match': {'edgar_path.log': {'$eq': null}}},
    {'$match': {'edgar_path.form': {'$in': ['10-K', '10-Q']}}},
    {'$match': {'_id': {'$in': ['796343']}}},
    {'$project':
        {
            'url': '$edgar_path.path',
            'name': 1,
            'form': '$edgar_path.form',
            'date': '$edgar_path.date',
            'cik': '$_id',
            '_id': 0
        }}
])
```

Take account of values for a position with the same `startDate` and `endDate`. The `updated`field show you the latest.

## LICENSE

Please feel free to use this software for non-commercial projects!

[![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/2.0/de/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/2.0/de/)

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 2.0 Germany License](http://creativecommons.org/licenses/by-nc-sa/2.0/de/)