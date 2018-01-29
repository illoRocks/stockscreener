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

    def connect(self, host='localhost', port=27017, db_name='stockscreener'):
        ''' TODO: mongodb-connection-string and password username '''

        try:
            conn = pymongo.MongoClient(host, port)
            db = conn[db_name]

            self.col_edgar_path = db['edgarPath']
            self.col_companies = db['companies']
            self.col_financial_positions = db['financialPositions']
            self.col_clean_financial_positions = db['cleanFinancialPositions']

            self.col_financial_positions.create_index([
                ('cik', pymongo.ASCENDING),
                ('label', pymongo.ASCENDING),
                ('updated',  pymongo.ASCENDING),
                ('startDate',  pymongo.ASCENDING),
                ('endDate',  pymongo.ASCENDING),
                ('instant',  pymongo.ASCENDING)],unique=True)

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
