
import pymongo


class MongoDigger:
    """manage mongoDB for SecDigger"""

    def __init__(self):
        self.session = {}
        self.col = 'Not connected to database!'

    def connect(self, database, collection, host='localhost', port=27017):
        try:
            conn = pymongo.MongoClient(host, port)
            conn.server_info()
            self.col = conn[database][collection]
            self.session['connection'] = str(self.col)
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print("Could not connect to MongoDB: %s" % err)
            quit()

    def __str__(self):
        if self.col == 'Not connected to database!':
            return self.col
        else:
            return "Connected successfully!!! %s" % str(self.col)


if __name__ == '__main__':
    m = MongoDigger()
    print(m)
    m.connect()
    print(m)
