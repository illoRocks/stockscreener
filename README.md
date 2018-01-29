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

```sh
python3 run.py --init --debug
```

```sh
python3 run.py -port 27017 -host localhost -cik 796343
```

```sh
python3 run.py -port 27017 -host localhost -multi 6 -nameRegex "^ibm" "coca.*cola"
```

use a text file with central index keys. seperated by line breaks.

```sh
python3 run.py -cikPath dowjones.txt
```

use `--help` for more informations

```sh
python3 run.py --help
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
// company collection
{
  "_id" : "796343",
  "lastUpdate" : ISODate("2018-01-29T16:25:44.560+07:00"),
  "lastDocument" : "2008-04-04",
  "NumberOfDocuments" : NumberInt("33")
}

// financial position collection

{
  "_id" : ObjectId("5a6e8628061b291969cae892"),
  "endDate" : ISODate("2008-02-29T07:00:00.000+07:00"),
  "segment" : [
    "MobileDeviceSolutions"
  ],
  "updated" : ISODate("2008-04-04T07:00:00.000+07:00"),
  "cik" : "796343",
  "startDate" : ISODate("2007-12-01T07:00:00.000+07:00"),
  "value" : 15200000,
  "label" : "MobileDeviceSolutionsRevenue"
}

// EDGAR Path collection

{
  "_id" : "1107194",
  "edgar_path" : [
    {
      "log" : null,
      "form" : "SC TO-I/A",
      "path" : "edgar/data/1107194/0000891618-04-001377.txt",
      "date" : "2004-12-13"
    }
  ],
  "name" : "CENTILLIUM COMMUNICATIONS INC"
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