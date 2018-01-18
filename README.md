# stockscreener

Download XBRL from the SEC and store it to MongoDB or as local files.

## Features

Optimized for multiprozessing
MongoDB as Database

### Dependencies

pymongo

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

Specify the company:
`cik`: any valid central index key,
`ticker`: any valid ticker,
`name`: any valid company name

Specify only one identifier. If more are given cik will be used.

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

## LICENSE

Please fell free to use this software for non-commercial projects!

[![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/2.0/de/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/2.0/de/)

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 2.0 Germany License](http://creativecommons.org/licenses/by-nc-sa/2.0/de/)