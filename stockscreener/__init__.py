try:
    from .sec_digger import SecDigger
    from .settings import Settings
    from .server import SecServer
    from .mongo_db import MongoHelper
except (ImportError, SystemError):
    from sec_digger import SecDigger
    from settings import Settings
    from server import SecServer
    from mongo_db import MongoHelper


__version__ = '1.0.1'