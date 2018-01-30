import pymongo
import logging

logger = logging.getLogger(__name__)


class MongoHelper:
    """manage mongoDB for SecDigger"""

    def __init__(self):
        self.col_edgar_path = {}
        self.col_companies = {}
        self.col_financial_positions = {}
        self.col_clean_financial_positions = {}
        self.connected = False
        self.status = 'Not connected to database!'

    def connect(
        self,
        host = 'localhost',
        port = 27017,
        name_collection ='stockscreener',
        name_path ='paths',
        name_companies ='companies',
        name_reports ='reports',
        name_segments = 'segments'
    ):
        ''' TODO: mongodb-connection-string and password username '''

        try:
            conn = pymongo.MongoClient(host, port)
            db = conn[name_collection]

            self.col_edgar_path = db[name_path]
            self.col_companies = db[name_companies]
            self.col_financial_positions = db[name_reports]
            self.col_segments = db[name_segments]
            self.col_clean_financial_positions = db['cleanFinancialPositions']

            # TODO weiteren index für schnelle updates anlegen
            self.col_financial_positions.create_index([
                ('cik', pymongo.ASCENDING),
                ('label', pymongo.ASCENDING),
                ('updated',  pymongo.ASCENDING),
                ('startDate',  pymongo.ASCENDING),
                ('endDate',  pymongo.ASCENDING),
                ('instant',  pymongo.ASCENDING)], unique=True)

            self.col_edgar_path.create_index([
                ('cik', pymongo.ASCENDING),
                ('path', pymongo.ASCENDING)], unique=True)

            self.col_edgar_path.create_index([
                ('path', pymongo.ASCENDING)], unique=True)

            self.col_segments.create_index([
                ('label', pymongo.ASCENDING)], unique=True)
                

            self.connected = True

        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error("Could not connect to MongoDB: %s" % err)
            quit()

        logger.info('database connection successful')

    def __str__(self):
        if not self.connected:
            return self.status
        else:
            return "Connected successfully!"


if __name__ == '__main__':
    m = MongoHelper()
    print(m)  # Not connected to database!
    m.connect(database='secTest', collection='test')
    print(m.connected)  # True
    print(m)  # Connected successfully!!! ...
