

''' just for testing '''


# reset edgar paths
# db.edgarPath.find({ })
#   .forEach(function (doc) {
#     doc.edgar_path.forEach(function (edgar_path) {
#       edgar_path.log = null
#     });
#     db.edgarPath.save(doc);
#   });

# find relevat financial positions
# var pattern = /cost/i
#  db.financialPositions.aggregate([
#      { "$match": { _id: "1001039" }},
#      { $project: {
#              filings: { "$objectToArray": "$$ROOT" }
#      } },
#      { $unwind: "$filings" },
#      { $match: { "filings.k": pattern }  },
#      { $project: {
#              names: "$filings.k",
#              numberOfValues: { $size: "$filings.v" },
#              values: "$filings.v"
#      } },
#      { $sort: { numberOfValues: -1 } }
#   ])

# clean position
# var cik = "1001039"
# db.financialPositions.aggregate([
#     {$match: {_id: cik}},
#     {$project: {
#         "revenues": "$SalesRevenueNet"
#     }},
#     {$unwind: "$revenues"},
#     {$group: {
#         "_id": {
#             "duration": {$divide: [{$subtract: ["$revenues.endDate", "$revenues.startDate"]}, 86400000]},
#             "startDate": "$revenues.startDate",
#             "endDate": "$revenues.endDate",
#             "segment": "$revenues.segment"
#         },
#         "latest": {"$max": "$revenues.updated"},
#         "revenues": {"$push": "$revenues"}
#     }},
#     {$unwind: "$revenues"},
#     {$redact: {$cond: [
#             {"$eq": ["$revenues.updated", "$latest"]},
#             "$$KEEP",
#             "$$PRUNE"
#         ]
#     }},
#     {$group: {
#         "_id": cik,
#         "revenues": {$push: {
#             "duration": "$_id.duration",
#             "startDate": "$_id.startDate",
#             "endDate": "$_id.endDate",
#             "segment": "$_id.segment",
#             "value": "$revenues.value",
#             "updated":  "$revenues.updated",
#         }}
#         // ]
#     }},
# ])


# prüfe einzelne zahlen
#  db.financialPositions.aggregate([
#      { "$match": { _id: "1001039" }},
#      { $project: {
#              revenues: "$SalesRevenueNet"
#      } },
#      { $unwind: "$revenues" },
#      { "$match": { "revenues.startDate": "2012-09-30" }},
#      { "$match": { "revenues.endDate": "2013-09-28" }},
#      { $project: {
#              revenues: "$revenues.value",
#              updated: "$revenues.updated",
#              segment0: { $arrayElemAt: [ "$revenues.segment", 0 ] },
#              segment1: { $arrayElemAt: [ "$revenues.segment", 1 ] },
#              segment3: { $arrayElemAt: [ "$revenues.segment", 2 ] }
#      } },
#   ])

# mapping
import pymongo
import logging
import json
import os
from pprint import pprint

logger = logging.getLogger(__name__)

try:
    from .mongo_db import MongoHelper
except (ImportError, SystemError):
    from mongo_db import MongoHelper


class DbCleaner(MongoHelper):

    def __init__(self):
        super().__init__()
        self.map = json.load(open(os.path.dirname(
            os.path.abspath(__file__)) + '/sec_schema.json'))
        pprint(self.map)

    def getPositionNames(self, cik):
        pipeline = [
            {"$match": {"_id": cik}},
            {"$project": {"arrayofkeyvalue": {"$objectToArray": "$$ROOT"}}},
            {"$unwind": "$arrayofkeyvalue"},
            {"$group": {"_id": cik, "allkeys": {"$addToSet": "$arrayofkeyvalue.k"}}}
        ]
        result = self.col_financial_positions.aggregate(pipeline)
        result = list(result)
        if len(result) == 0:
            return None
        result = result[0]
        return result['allkeys']


    def getPosition(self, cik, target_name, current_name):
        pipeline = [
            {"$match": {"_id": cik}},
            {"$project": {
                target_name: "$" + current_name
            }},    {"$unwind": "$" + target_name},
            {"$group": {
                "_id": {
                    "duration": {"$divide": [{"$subtract": ["$" + target_name + ".endDate", "$" + target_name + ".startDate"]}, 86400000]},
                    "startDate": "$" + target_name + ".startDate",
                    "endDate": "$" + target_name + ".endDate",
                    "segment": "$" + target_name + ".segment"
                },
                "latest": {"$max": "$" + target_name + ".updated"},
                target_name: {"$push": "$" + target_name}
            }},    {"$unwind": "$" + target_name},
            {"$redact": {"$cond": [
                {"$eq": ["$" + target_name + ".updated", "$latest"]},
                "$$KEEP",
                "$$PRUNE"
            ]}},
            {"$group": {
                "_id": cik,
                target_name: {"$push": {
                    "duration": "$_id.duration",
                    "startDate": "$_id.startDate",
                    "endDate": "$_id.endDate",
                    "segment": "$_id.segment",
                    "value": "$" + target_name + ".value",
                    "updated":  "$" + target_name + ".updated",
                }}
            }},
        ]
        result = self.col_financial_positions.aggregate(pipeline)
        return list(result)[0]


    def create_clean_collection(self):
        ciks = self.col_companies.distinct('_id')
        l = len(ciks)
        i = 0
        for cik in ciks:
            i += 1
            keys = self.getPositionNames(cik)
            if keys is None:
                logger.debug("%s von %s processed. %s has no positions" % (i, l, cik))
                continue
            for map_key, map_values in self.map['financial_positions'].items():
                print(map_key, map_values)
                for map_value in map_values:
                    print(map_value)
                    if map_value in keys:
                        t = self.getPosition(cik, map_key, map_value)
                        self.col_clean_financial_positions.update_one({"_id": cik}, { "$set": t}, True)
            logger.debug("%s von %s processed. latest: %s" % (i, l, cik))

if __name__ == '__main__':

    logging.basicConfig(level = logging.DEBUG)

    c = DbCleaner()
    c.connect()
    # c.col_clean_financial_positions.drop()
    c.create_clean_collection()
    print(c)
