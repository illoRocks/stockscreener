import pymongo


class MongoHelper:
    """manage mongoDB for SecDigger"""

    def __init__(self):
        self.session = {}
        self.col = {}
        self.connected = False
        self.status = 'Not connected to database!'

    def connect(self, database, collection, host='localhost', port=27017):
        try:
            conn = pymongo.MongoClient(host, port)
            conn.server_info()
            self.col = conn[database][collection]
            self.session['connection'] = str(self.col)
            self.connected = True
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print("Could not connect to MongoDB: %s" % err)
            quit()

    def __str__(self):
        if not self.connected:
            return self.status
        else:
            return "Connected successfully!!! %s" % str(self.col)


if __name__ == '__main__':
    m = MongoHelper()
    print(m) # Not connected to database!
    m.connect(database = 'secTest', collection='test')
    print(m.connected) # True
    print(m) # Connected successfully!!! ...
