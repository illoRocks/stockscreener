from configparser import ConfigParser, NoOptionError
from os import path

WORKING_DIR = path.dirname(path.abspath(__file__))

class Settings():
    """manage mongoDB for SecDigger"""

    def __init__(self, file_name=['config.ini', 'stockscreener.ini']):
        self.config = ConfigParser()
        self.config.read(file_name)

    def get_setting(self, section, val_type, my_setting, default):
        try:
            if val_type == int:
                ret = self.config.getint(section, my_setting, fallback=default)
            elif val_type == bool:
                ret = self.config.getboolean(
                    section, my_setting, fallback=default)
            elif val_type == float:
                ret = self.config.getfloat(
                    section, my_setting, fallback=default)
            else:
                ret = self.config.get(section, my_setting, fallback=default)

        except (NoOptionError, KeyError):
            ret = None

        return ret

    # databas options: host and port
    def get_database_host(self):
        return self.get_setting('DATABASE', str, 'host', 'localhost')

    def get_database_port(self):
        return self.get_setting('DATABASE', int, 'port', 27017)

    def get_database_username(self):
        return self.get_setting('DATABASE', str, 'username', None)

    def get_database_password(self):
        return self.get_setting('DATABASE', str, 'password', None)

    def get_database_authSource(self):
        return self.get_setting('DATABASE', str, 'authSource', None)

    # logging options
    def get_logging(self):
        return self.get_setting('LOGGING', bool, 'Logging', False)

    def get_logging_level(self):
        return self.get_setting('LOGGING', int, 'level', 30)

    # server options: host and port
    def get_server_host(self):
        return self.get_setting('SERVER_OPTIONS', str, 'host', 'localhost')

    def get_server_port(self):
        return self.get_setting('SERVER_OPTIONS', str, 'port', 3030)

    # Database names: collection, paths, companies and reports
    def get_db_name_collection(self):
        return self.get_setting('DATABASE_NAMES', str, 'collection', 'stockscreener')

    def get_db_name_path(self):
        return self.get_setting('DATABASE_NAMES', str, 'path', 'path')

    def get_db_name_companies(self):
        return self.get_setting('DATABASE_NAMES', str, 'companies', 'companies')

    def get_db_name_reports(self):
        return self.get_setting('DATABASE_NAMES', str, 'reports', 'reports')

    # parser options: saveLocal, save (to mongoDB)
    def get_saveLocal(self):
        return self.get_setting('PARSER_OPTIONS', bool, 'save', False)

    def get_local_file_path(self):
        return self.get_setting('PARSER_OPTIONS', str, 'local_file_path', '%s/test' % WORKING_DIR)

    def get_saveDb(self):
        return self.get_setting('PARSER_OPTIONS', bool, 'save_to_db', True)

    def get_multi(self):
        return self.get_setting('PARSER_OPTIONS', int, 'multiprocessing', 0)

    def get_number_of_files(self):
        return self.get_setting('PARSER_OPTIONS', int, 'number_of_files', 0)

    def get_cik_path(self):
        return self.get_setting('PARSER_OPTIONS', str, 'cik_path', None)

    def get_transform_after(self):
        return self.get_setting('PARSER_OPTIONS', str, 'transform_after', False)



        