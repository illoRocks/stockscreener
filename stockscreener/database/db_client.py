import logging
import sys
from pprint import pprint
from sshtunnel import SSHTunnelForwarder

from stockscreener.database.mongo_db import MongoHelper


logger = logging.getLogger(__name__)


class DBClient:
    """manage Databases for SecDigger"""

    def __init__(self):
        self.client: MongoHelper
        self.connected = False

    def connect(self, db_type="mongodb", init=True,
                host='localhost', port=27017, **kwargs):
        """connect to database"""

        if self.connected:
            logger.info("Allready connected")

        ssh_address = kwargs.pop('ssh_address')
        ssh_username = kwargs.pop('ssh_username')
        ssh_password = kwargs.pop('ssh_password')
        if ssh_address:
            logger.info("Use ssh tunnel: %s" % ssh_address)
            server = SSHTunnelForwarder(
                ssh_address_or_host=ssh_address,
                ssh_username=ssh_username,
                ssh_password=ssh_password,
                remote_bind_address=(host, port)
            )
            server.start()
            port = server.local_bind_port
            host = 'localhost'

        if type(db_type) is str and db_type.lower() == "mongodb":
            self.client = MongoHelper()

        self.client.connect(init, host, port, **kwargs)
        self.connected = self.client.connected

    def db_get_edgar_path(self, **kwargs) -> list:
        return self.client.get_edgar_path(**kwargs)

    def db_save_edgar_path(self, paths: list):
        self.client.save_edgar_path(paths)

    def db_update_edgar_path(self, filter, update):
        self.client.update_edgar_path(filter, update)

    def db_update_companie(self, filter, update):
        self.client.update_companie(filter, update)

    def db_save_report_positions(self, bulk: list):
        self.client.save_report_positions(bulk)

    def db_save_segments(self, bulk: list):
        self.client.save_segments(bulk)