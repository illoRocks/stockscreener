'''
Created on 19.02.2017

@author: olli
'''
from datetime import datetime
from pprint import pprint
import pymongo

try:
    conn=pymongo.MongoClient('localhost', 27017)
    print("Connected successfully!!!", conn)
except:
    print("Could not connect to MongoDB: %s")
    

db = conn.fin_db

col = db.fil_col

c = col.count()
print('Number of companies: %s\n' % c)
i = 1
# 
# 
# mapper = {'revenues': 'revenueTotal',
#         'salesrevenuegoodsnet': 'revenueTotal',
#         'salesrevenuenet': 'revenueTotal',
#         'netincomeloss': 'netIncome'}
# 
# def append_items(periode, value, docDate, mapper = mapper):
# 
data = {}
for doc in col.find()[:1]:
    print('Number: %s of %s\n'
          'CIK: %s\n'
          'Last document: %s' % (i, c, doc['_id'], doc['lastDocument']))
    for f in doc['fillings']:
        print(f)
        print(doc['fillings'][f])
        
#     pprint(doc)
#     for key in doc['fillings']:
#         print ('\tAccession: %s\n'
#                '\tdocument end date: %s' % (key, doc['fillings'][key]['documentPeriodEndDate']))
#         for values in doc['fillings'][key]['content']:
#             print(values['period'])
#             print(values['values'])
#             data['netincomeloss'].append({'value': values['values']['netincomeloss'],
#                                           'updated': doc['fillings'][key]['documentPeriodEndDate'],
#                                          **values['period']})
#             break
#         
#         pprint(doc['fillings'][key]['content'])
#         break
# pprint(data)
#     
#     print('\n', doc['_id'])
#     print(doc['entityRegistrantName'],'\n')
#     
#     for value in doc['fillings']['0001432093-11-000567']['content']:
#         print (value)
#         break
#     
    
    
# Zeige Daten
# v = col.count()#164
# print(v)
# print(db.collection_names(include_system_collections=False))
# pprint.pprint(col.find_one({'_id': '0001048911'}))
# pprint.pprint(col.find_one())
# cur = col.find({})
# for c in cur:
#     pprint.pprint(c)
# print(col.find({'fillings.0000950123-09-04407611':{"$exists":True}}).count())
# cur = col.find({'fillings.0000950123-09-04407611':{"$exists":True}})
# for c in cur:
#     pprint.pprint(c)
# if col.find({'fillings.0000950123-09-0440761':{"$exists":True}}).count() > 0:
#     print(True)    



# # Colletions löschen
# result = col.delete_many({})
# print(result)
# print(result.deleted_count)




