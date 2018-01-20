''' just for testing '''

## find relevat financial positions

# var pattern = /cost/i
# db.companies.aggregate([
#     { "$match": { _id: "796343" }},
#     { $project: {
#             filings: { "$objectToArray": "$$ROOT.fillings" }
#     } },
#     { $unwind: "$filings" },
#     { $match: { "filings.k": pattern }  },
#     { $project: {
#             names: "$filings.k",
#             numberOfValues: { $size: "$filings.v" },
#             values: "$filings.v"
#     } },
#     { $sort: { numberOfValues: -1 } }    
#  ])

# mapping
import pymongo
import logging

logger = logging.getLogger(__name__)

try:
    from .mongo_db import MongoHelper
except (ImportError, SystemError):
    from mongo_db import MongoHelper

class DbCleaner(MongoHelper):

    def __init__(self):
        super().__init__()




if __name__ == '__main__':
    c = DbCleaner()
    c.connect()
    print(c)