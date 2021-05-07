import os


class Config(object):

	API_ID = int(os.environ.get('API_ID'))
	API_HASH = os.environ.get('API_HASH')
	TOKEN = os.environ.get('TOKEN', None)
	OWNER_ID = int(os.environ.get('OWNER_ID', 1669575731))
	OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "LustPriest")

	SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", None)
	MESSAGE_DUMP = os.environ.get('MESSAGE_DUMP', None)
	JOIN_LOGGER = os.environ.get('JOIN_LOGGER', None)
	ERROR_DUMP = os.environ.get('ERROR_DUMP', None)
	GBAN_LOGS = os.environ.get('GBAN_LOGS', None)

	SYS_ADMIN = int(os.environ.get('SYS_ADMIN', 0))
	CUSTOM_CMD = [
	    '/',
	    '!',
	]

	# RECOMMENDED
	DB_URI = os.environ.get('DB_URI', "")
	LOAD = os.environ.get("LOAD", "")
	NO_LOAD = os.environ.get("NO_LOAD", "")
      STRICT_GBAN = bool(os.environ.get("STRICT_GBAN", True))
	WEBHOOK = bool(os.environ.get('WEBHOOK', False))
	INFOPIC = bool(os.environ.get('INFOPIC', False))
	URL = os.environ.get('URL', None)
	SPAMWATCH_API = os.environ.get('SPAMWATCH_API', None)

	# OPTIONAL
	CERT_PATH = os.environ.get('CERT_PATH')
	PORT = int(os.environ.get('PORT', 5000))
	DEL_CMDS = bool(os.environ.get('DEL_CMDS', True))
	BAN_STICKER = os.environ.get('BAN_STICKER',
	                             'CAADAgADOwADPPEcAXkko5EB3YGYAg')
	ALLOW_EXCL = bool(os.environ.get('ALLOW_EXCL', False))
	WALL_API = os.environ.get('WALL_API', None)
	CF_API_KEY = os.environ.get('CF_API_KEY', None)


# RentalBot
class Rental(Config):
	Rent = True
