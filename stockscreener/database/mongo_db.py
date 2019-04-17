from pymongo import MongoClient, ASCENDING, IndexModel
from bson.objectid import ObjectId
from pymongo.command_cursor import CommandCursor

from pymongo.errors import BulkWriteError, WriteError, ServerSelectionTimeoutError, OperationFailure
import json
import logging
from pprint import pprint
from sshtunnel import SSHTunnelForwarder
import os
import sys
import re

from stockscreener.database.base_client import BaseClient


logger = logging.getLogger(__name__)

indices = {
    'reports': [
        IndexModel([('company', ASCENDING),
                    ('label', ASCENDING),
                    ('updated',  ASCENDING),
                    ('startDate',  ASCENDING),
                    ('endDate',  ASCENDING),
                    ('instant',  ASCENDING),
                    ('value',  ASCENDING),
                    ('duration',  ASCENDING)])
    ],
    'companies': [
        IndexModel([('cik', ASCENDING)], unique=True),
        IndexModel([('cik', ASCENDING)], unique=True)
    ],
    'edgar_path': [
        IndexModel([('_id', ASCENDING),
                    ('path', ASCENDING)],
                   unique=True),
        IndexModel([('path', ASCENDING)], unique=True)
    ]
}


def get_first_element(cursor: list) -> dict:
    for result in cursor:
        return result


class MongoHelper(BaseClient):
    """manage mongoDB for SecDigger"""

    def __init__(self):
        self.col_edgar_path = {}
        self.col_companies = {}
        self.col_reports = {}
        self.col_clean_financial_positions = {}
        self.connected = False

    def connect(
        self,
        init=True,
        host='localhost',
        port=27017,
        username=None,
        password=None,
        authSource=None,
        name_collection='stockscreener',
        name_path='paths',
        name_companies='companies',
        name_reports='reports',
        name_segments='segments',
        name_transformed='financial_positions'
    ) -> None:
        ''' TODO: mongodb-connection-string '''

        credentials = {
            'host': host,
            'port': port
        }

        if username is not None:
            credentials['username'] = username
        if password is not None:
            credentials['password'] = password
        if authSource is not None:
            credentials['authSource'] = authSource

        try:
            conn = MongoClient(**credentials)
        except ServerSelectionTimeoutError as err:
            logger.error("Could not connect to MongoDB: %s" % err)
            sys.exit()

        db = conn[name_collection]
        self.col_edgar_path = db[name_path]
        self.col_companies = db[name_companies]
        self.col_reports = db[name_reports]
        self.col_segments = db[name_segments]
        self.name_transformed = name_transformed

        if init:
            try:
                self.col_edgar_path.create_indexes(indices['edgar_path'])
                self.col_reports.create_indexes(indices['reports'])
                self.col_companies.create_indexes(indices['companies'])

            except OperationFailure as err:
                logger.error("Could not create indices: %s" % err)
                logger.error("Check your credentials: %s" % credentials)
                quit()

        self.connected = True

        logger.info('database connection successful')

    def get_edgar_path(self, cik=None, ticker=None,
                       name=None, name_regex=None, limit=0) -> list:

        query = {}
        query['log'] = {'$eq': None}
        query['form'] = {'$in': ['10-K', '10-Q']}

        if cik:
            query['cik'] = {'$in': [cik] if type(cik) == str else cik}
        elif ticker:
            query['ticker'] = {'$in': [ticker]
                               if type(ticker) == str else ticker}
        elif name:
            query['name'] = {'$in': [name] if type(name) == str else name}
        elif name_regex:
            regx = [re.compile(r, re.IGNORECASE) for r in name_regex]
            query['name'] = {'$in': regx}
        else:
            sys.exit("no company identifier")

        logger.debug('path query: %s' % query)

        return self.col_edgar_path.find(query).limit(limit)

    def save_edgar_path(self, paths: list):
        try:
            self.col_edgar_path.insert_many(paths, ordered=False)
        except BulkWriteError:
            # logging.error('BulkWriteError: %s' % err.details)
            pass

    def update_edgar_path(self, filter, update):
        try:
            self.col_edgar_path.update_one(filter, update, False, True)
        except WriteError as err:
            logger.error('Please check the query: WriteError %s' % err)
            quit()

    def update_companie(self, filter, update):
        try:
            self.col_companies.update_one(filter, update, upsert=True)
        except WriteError as err:
            logger.error('Please check the query: WriteError %s' % err)
            quit()

    def save_report_positions(self, bulk):
        try:
            self.col_reports.bulk_write(bulk, ordered=False)
        except BulkWriteError as err:
            logger.debug(err.details)

    def save_segments(self, bulk):
        try:
            self.col_segments.bulk_write(bulk, ordered=False)
        except BulkWriteError as err:
            logger.debug(err.details)

    def get_companies(self, filter={}, limit=0):
        if '_id' in filter:
            filter['_id'] = ObjectId(filter['_id'])
        # logger.debug("get company -> filter: %s limit: %s" % (filter, limit))
        fields = {'cik': 1, 'EntityRegistrantName': 1, 'CurrentFiscalYearEndDate': 1,
                  'NumberOfDocuments': 1, 'lastDocument': 1}
        cursor = self.col_companies.find(filter, fields).limit(limit)
        return list(cursor)

    def get_fillings(self, filter={}, fields=None, segment=False):
        pipeline = [
            {'$group':
             {'_id': {
                 'company': "$company",
                 'label': "$label",
                 'segment': "$segment",
                 'instant': "$instant",
                 'startDate': "$startDate",
                 'endDate': "$endDate"
             },
                 'lastSalesDate': {'$last': "$updated"},
                 'entries': {'$push': "$$ROOT"}}
             },
            {'$replaceRoot': {'newRoot': {'$arrayElemAt': ["$entries", 0]}}},
            {'$match': {'segment': {'$exists': segment}}},
            {'$sort': {'periodEnd': -1, 'label': 1}}
        ]
        pipeline.append({'$match': filter})
        
        cursor = self.col_reports.aggregate(pipeline)

        # cursor = self.col_reports.find(filter, fields).limit(limit)
        return list(cursor)

    # def get_company(self, id):
    #     pipeline = [
    #         {"$group": {
    #             "_id": {
    #                 "company": "$company",
    #                 "label": "$label",
    #                 "segment": "$segment",
    #                 "instant": "$instant",
    #                 "startDate": "$startDate",
    #                 "endDate": "$endDate"
    #             },
    #             "lastSalesDate": {"$last": "$updated"},
    #             "entries": {"$push": "$$ROOT"}}
    #          },
    #         {"$replaceRoot": {"newRoot": {"$arrayElemAt": ["$entries", 0]}}},
    #         {"$match": {"segment": {"$exists": False}}},
    #         {"$addFields": {"periodEnd": {
    #             "$ifNull": ["$instant", "$endDate"]}}},
    #         {"$lookup": {
    #             "from": "companies",
    #             "localField": "company",
    #             "foreignField": "cik",
    #             "as": "meta"
    #         }},
    #         {"$match": {"meta": {"$ne": []}}},
    #         {"$unwind": "$meta"},
    #         {"$project": {"meta.reports": 0}},
    #         {"$group": {
    #             "_id": "$meta",
    #             "financial_positions": {
    #                 "$push": {
    #                     "label": "$label",
    #                     "value": "$value",
    #                     "instant": "$instant",
    #                     "startDate": "$startDate",
    #                     "endDate": "$endDate",
    #                     "periodEnd": "$periodEnd",
    #                     "segment": "$segment"
    #                 }}
    #         }},
    #         {"$project": {
    #             "_id": "$_id._id",
    #             "cik": "$_id.cik",
    #             "CurrentFiscalYearEndDate": "$_id.CurrentFiscalYearEndDate",
    #             "EntityRegistrantName": "$_id.EntityRegistrantName",
    #             "NumberOfDocuments": "$_id.NumberOfDocuments",
    #             "lastDocument": "$_id.lastDocument",
    #             "lastUpdate": "$_id.lastUpdate",
    #             "financial_positions": "$financial_positions"
    #         }},
    #         {"$match": {"_id": {"$eq": ObjectId(id)}}}
    #     ]

    #     cursor = self.col_reports.aggregate(pipeline)
    #     return get_first_element(list(cursor))

    def transform_collection(self):
        logger.info('transform collection...')
        opt = json.load(
            open(os.path.join(os.path.dirname(__file__), './sec_schema.json')))

        labels = []
        for key in opt['labels']:
            labels.extend(opt['labels'][key])

        pprint(labels)

        pipeline = [
            # filter latest
            {'$group':
                {'_id': {
                    'company': "$company",
                    'label': "$label",
                    'segment': "$segment",
                    'instant': "$instant",
                    'startDate': "$startDate",
                    'endDate': "$endDate"
                },
                    'lastSalesDate': {"$last": "$updated"},
                    'entries': {'$push': "$$ROOT"}
                }},
            {'$replaceRoot': {'newRoot': {'$arrayElemAt': ["$entries", 0]}}},

            # filter labels
            {'$match': {'label': {"$in": labels}}},

            # not use segment values
            {'$match': {'segment': {"$exists": False}}},

            # sort by date
            {'$sort': {'endDate': 1}},

            # # reports as array property
            # {'$group':
            #     {'_id': "$company",
            #         'reports': {
            #             '$push': {
            #                 '_id': "$$ROOT._id",
            #                 'endDate': "$$ROOT.endDate",
            #                 'value': "$$ROOT.value",
            #                 'label': "$$ROOT.label",
            #                 'updated': "$$ROOT.updated",
            #                 'duration': "$$ROOT.duration",
            #                 'startDate': "$$ROOT.startDate"
            #             }}}},

            # # join with compny collection
            # {'$lookup': {
            #     'from': "companies",
            #     'localField': "_id",
            #     'foreignField': "_id",
            #     'as': "company"}},
            # {'$unwind': "$company"},

            # {'$project': {
            #     'reports': 1,
            #     'lastUpdate': "$company.lastUpdate",
            #     'NumberOfDocuments': "$company.NumberOfDocuments",
            #     'EntityRegistrantName': "$company.EntityRegistrantName",
            #     'CurrentFiscalYearEndDate': "$company.CurrentFiscalYearEndDate"}},

            # write to new collection
            {'$out': self.name_transformed}
        ]

        # pprint(pipeline)

        cursor = self.col_reports.aggregate(pipeline)

        if len(list(cursor)):
            logger.info('transformation successful')

    def __str__(self):
        if not self.connected:
            return "Not connected!"
        else:
            return "Connected successfully!"


if __name__ == '__main__':
    pass
    # m = MongoHelper()
    # print(m)  # Not connected to database!
    # m.connect(database='secTest', collection='test')
    # print(m.connected)  # True
    # print(m)  # Connected successfully!!! ...
