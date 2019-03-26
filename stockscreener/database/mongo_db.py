from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError, WriteError, ServerSelectionTimeoutError, OperationFailure
import json
import logging
from pprint import pprint
from sshtunnel import SSHTunnelForwarder
import os
import sys
import re



logger = logging.getLogger(__name__)


class BaseClient:
    def connect(self, **kwargs):
        raise NotImplementedError("connect() not implemented")

    def get_edgar_path(self, **kwargs):
        raise NotImplementedError("get_edgar_path() not implemented")

    def save_edgar_path(self, path: list):
        raise NotImplementedError("save_edgar_path() not implemented")

    def update_edgar_path(self, filter: dict, update: dict):
        raise NotImplementedError("update_edgar_path() not implemented")

    def update_companie(self, filter: dict, update: dict):
        raise NotImplementedError("update_companie() not implemented")

    def save_report_positions(self, bulk: list):
        raise NotImplementedError("save_report_positions() not implemented")

    def save_segments(self, bulk: list):
        raise NotImplementedError("save_segments() not implemented")


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
        ''' TODO: mongodb-connection-string and password username '''

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
                # TODO weiteren index für schnelle updates anlegen
                self.col_reports.create_index([
                    ('company', ASCENDING),
                    ('label', ASCENDING),
                    ('updated',  ASCENDING),
                    ('startDate',  ASCENDING),
                    ('endDate',  ASCENDING),
                    ('instant',  ASCENDING),
                    ('value',  ASCENDING),
                    ('duration',  ASCENDING)])

                self.col_companies.create_index([
                    ('cik', ASCENDING)], unique=True)

                self.col_edgar_path.create_index([
                    ('_id', ASCENDING),
                    ('path', ASCENDING)], unique=True)

                self.col_edgar_path.create_index([
                    ('path', ASCENDING)], unique=True)

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
        self.col_edgar_path.insert_many(paths, ordered=False)
        
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

    def __str__(self):
        if not self.connected:
            return "Not connected!"
        else:
            return "Connected successfully!"

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


if __name__ == '__main__':
    pass
    # m = MongoHelper()
    # print(m)  # Not connected to database!
    # m.connect(database='secTest', collection='test')
    # print(m.connected)  # True
    # print(m)  # Connected successfully!!! ...
