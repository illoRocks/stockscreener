from pymongo import MongoClient

def getDb():
  ''' get mongo-collection (`secFillings`) '''
  client = MongoClient("mongodb://localhost:27017")
  db = client.secFillings
  return db

