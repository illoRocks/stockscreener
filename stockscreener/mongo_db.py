import pymongo
import logging

logger = logging.getLogger(__name__)

class MongoHelper:
    """manage mongoDB for SecDigger"""

    def __init__(self):
        self.col_edgar_path = {}
        self.col_companies = {}
        self.col_financial_positions = {}
        self.connected = False
        self.status = 'Not connected to database!'

    def connect(self, host='localhost', port=27017):
        ''' TODO: mongodb-connection-string and password username '''

        try:
            conn = pymongo.MongoClient(host, port)
            self.col_edgar_path = conn['sec_digger']['edgarPath']
            self.col_companies = conn['sec_digger']['companies']
            self.col_financial_positions = conn['sec_digger']['financialPositions']
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
    print(m) # Not connected to database!
    m.connect(database = 'secTest', collection='test')
    print(m.connected) # True
    print(m) # Connected successfully!!! ...
