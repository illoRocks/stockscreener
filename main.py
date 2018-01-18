from stockscreener.sec_digger import SecDigger

# use SecDigger
sd = SecDigger()

# connect to Database
sd.connect(database='sec_digger', collection='stocks')

# optional settings
sd.verbose = True

# Init Database / apply only once!
# sd.download_idx()
# sd.save_idx()
# print(sd)

# if index allredy exist
sd.download_idx(whole=False)
sd.save_idx()
print(sd)

# download filings
options = {
  'multiprocessing': False,
  'cik': '796343',
  'save': False
}
sd.get_files_from_web(**options)  # eingrenzug
print('\n', m)
