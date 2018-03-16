# stockscreener

Download XBRL from the SEC and store it to MongoDB or as local files.

This project is under activ development!

## Features

* Optimized for multiprozessing
* MongoDB as Database
* Low memory consumption
* CLI

### Dependencies

* pymongo
* requests

### Instalation

Install [Python 3](https://www.python.org/downloads/)

Install stockscreener from source:

```sh
git clone https://github.com/illoRocks/stockscreener

cd stockscreener

python3 setup.py install
```

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

Specify the company with `cik`, `name` or `name_regex` of the company. It should be a valid EDGAR string. Check the existing database or the sec website for this. Specify only one identifier. If more are given then `cik` will be used. Identifier could be a string or an array with strings.

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

#### Regex examples

IGNORECASE is used.

```python
sd.get_files_from_web(
  name_regex = "coca.*cola"
)

# OR

sd.get_files_from_web(
  name_regex = ["CoCa CoLa", "^ibm"]
)
```

### 2.2 Download Reports from the EDGAR server and save it to MongoDB | Multiprocessing

specify the company: read 2.1

`multiprocessing` could be boolean or integer. If `True` then the program use 4 worker by default else the programm use the the given integer for numbers of worker.

```python
sd.get_files_from_web(
    cik='796343',
    multiprocessing=8
)
```

### Use CLI

Initialize the database with the folowing statement.

```sh
python3 scripts/run.py --init --debug
```

Choose your preffered statement.

```sh
python3 scripts/run.py -port 27017 -host localhost -cik 796343
```

```sh
python3 scripts/run.py -port 27017 -host localhost -multi 6 -nameRegex "^ibm" "coca.*cola"
```

use a text file with central index keys. seperated by line breaks.

```sh
python3 scripts/run.py -cikPath dowjones.txt
```

use `--help` for more informations

```sh
python3 scripts/run.py --help
```

#### config.ini

most settings could be set in a `config.ini` file.

```ini
[DATABASE]
Client = Mongodb
Port = 27017
Host = localhost

[LOGGING]
Debug = true
; ERROR = 40, WARNING = 30, INFO = 20 or DEBUG = 10
Level = 10

[PARSER_OPTIONS]
save = false
local_file_path = /test
save_to_db = true
multiprocessing = 9
number_of_files = -1
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
* use sql database
* pip

## Example Schema

```json
// db.paths.find({})
{
  "_id" : ObjectId("5aab0129061b29095ab554d6"),
  "cik" : "1107194",
  "form" : "SC TO-I/A",
  "name" : "CENTILLIUM COMMUNICATIONS INC",
  "date" : "2004-12-13",
  "path" : "edgar/data/1107194/0000891618-04-001377.txt",
  "log" : null
}

// db.companies.find({})
{
  "_id" : "796343",
  "reports" : [
    ObjectId("5aab0ab6061b2913036a29e1"),
    ObjectId("5aab0ab6061b2913036a29e2"),
    // ...
  ],
  "lastDocument" : "2016-01-19",
  "lastUpdate" : ISODate("2018-03-16T02:10:14.760+01:00"),
  "NumberOfDocuments" : NumberInt("49"),
  "EntityRegistrantName" : "ADOBE SYSTEMS INC",
  "CurrentFiscalYearEndDate" : "--11-27"
}

// db.reports.find({})
{
  "_id" : ObjectId("5aab0ab6061b2913036a29e1"),
  "updated" : ISODate("2006-10-11T02:00:00.000+02:00"),
  "label" : "DeferredUnearnedRevenueCurrent",
  "instant" : ISODate("2005-12-02T01:00:00.000+01:00"),
  "company" : "796343",
  "value" : NumberInt("57839000"),
  "segment" : [
    "Consolidated"
  ]
}

// db.segments.find({})
{
  "_id" : "Consolidated",
  "reports" : [
    ObjectId("5aab0ab6061b2913036a29e1"),
    ObjectId("5aab0ab6061b2913036a29e2"),
    // ...
  ]
}


```

Take account of values for a position with the same `startDate`'s and `endDate`'s. The `updated` field shows the latest.

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

### search for companies by name

```json
db.edgarPath.find({ name: { $in: [
    /wal mart/i,
    /apple/i,
] }})
```

## LICENSE

Please feel free to use this software for non-commercial projects!

[![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/2.0/de/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/2.0/de/)

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 2.0 Germany License](http://creativecommons.org/licenses/by-nc-sa/2.0/de/)