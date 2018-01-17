# stockscreener

## Notification

High memory usage ( >=8Gb )

## Usage

Make sure that MongoDB is running on your machine!

### Initialize the Database

Download all paths and save it to MongoDB

```python
from stockscreener.edgar_idx import SecIdx

print("init Database")
i = SecIdx()
i.connect(database='sec_digger', collection='stocks')
i.download_idx(verbose=True))
i.save_idx()
print("finish")
```

!it take a while to write the data to the database! 

### Download Reports from the EDGAR server and save it to MongoDB

(coming soon)


1. XBRL-Links runterladen
	1.1 falls zum ersten mal dann: edgar_idx_all.py
	1.2 wenn sqlite vorhanden, dann: edgar_idx_current.py
2. Dateien lokal speichern mit 
		load_files.py -> direkt in konsole schreiben 
		wird parallel auf allen Kernen ausgeführt
3. XBRL aufbereiten: clean_xbrl