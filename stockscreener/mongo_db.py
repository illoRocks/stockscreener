import pymongo
import json
import logging
from pprint import pprint
import os


logger = logging.getLogger(__name__)


class MongoHelper:
    """manage mongoDB for SecDigger"""

    def __init__(self):
        self.col_edgar_path = {}
        self.col_companies = {}
        self.col_reports = {}
        self.col_clean_financial_positions = {}
        self.connected = False
        self.status = 'Not connected to database!'

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
    ):
        ''' TODO: mongodb-connection-string and password username '''

        try:
            credentials = {}
            if username is not None:
                credentials['username'] = username
            if password is not None:
                credentials['password'] = password
            if authSource is not None:
                credentials['authSource'] = authSource
                
            conn = pymongo.MongoClient(host, port, **credentials)
            db = conn[name_collection]

            self.col_edgar_path = db[name_path]
            self.col_companies = db[name_companies]
            self.col_reports = db[name_reports]
            self.col_segments = db[name_segments]
            self.name_transformed = name_transformed

            if init:
                # TODO weiteren index für schnelle updates anlegen
                self.col_reports.create_index([
                    ('company', pymongo.ASCENDING),
                    ('label', pymongo.ASCENDING),
                    ('updated',  pymongo.ASCENDING),
                    ('startDate',  pymongo.ASCENDING),
                    ('endDate',  pymongo.ASCENDING),
                    ('instant',  pymongo.ASCENDING),
                    ('value',  pymongo.ASCENDING),
                    ('duration',  pymongo.ASCENDING)])
                
                self.col_companies.create_index([
                    ('cik', pymongo.ASCENDING)], unique=True)

                self.col_edgar_path.create_index([
                    ('_id', pymongo.ASCENDING),
                    ('path', pymongo.ASCENDING)], unique=True)

                self.col_edgar_path.create_index([
                    ('path', pymongo.ASCENDING)], unique=True)

            # self.col_segments.create_index([
            #     ('label', pymongo.ASCENDING)], unique=True)

            self.connected = True

        except pymongo.errors.ServerSelectionTimeoutError as err:
            logger.error("Could not connect to MongoDB: %s" % err)
            quit()

        logger.info('database connection successful')

    def __str__(self):
        if not self.connected:
            return self.status
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
