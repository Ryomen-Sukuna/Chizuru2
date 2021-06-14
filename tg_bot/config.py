import os

class Config(object):
        API_ID = int(os.environ.get('API_ID'))
        API_HASH = os.environ.get('API_HASH')
        TOKEN = os.environ.get('TOKEN', None)
        OWNER_ID = int(os.environ.get('OWNER_ID', 1669575731))

        SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", None)
        MESSAGE_DUMP = os.environ.get('MESSAGE_DUMP', None)
        JOIN_LOGGER = os.environ.get('JOIN_LOGGER', None)
        ERROR_DUMP = os.environ.get('ERROR_DUMP', None)
        GBAN_LOGS = os.environ.get('GBAN_LOGS', None)

        CUSTOM_CMD = [
            '/',
            '!',
        ]

        # RECOMMENDED
        DB_URI = os.environ.get('DB_URI', "")
        WALL_API = os.environ.get('WALL_API', None)

        # OPTIONAL
        LOAD = os.environ.get("LOAD", "")
        NO_LOAD = os.environ.get("NO_LOAD", "")
        DEL_CMDS = bool(os.environ.get('DEL_CMDS', True))


# RentalBot
class Rental(Config):
        Rent = True
