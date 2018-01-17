from stockscreener.edgar_idx import SecIdx

if __name__ == "__main__":
  print("init Database")
  i = SecIdx()
  i.connect(database='sec_digger', collection='stocks')
  i.download_idx(verbose=True))
  i.save_idx()
  print("finish")