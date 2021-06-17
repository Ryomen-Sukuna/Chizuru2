import os
import sys
import time
import json
import logging
from logging.config import fileConfig

from tg_bot.modules.sql import SESSION
import telegram.ext as tg
from telethon import TelegramClient
from telethon.sessions import MemorySession
from ptbcontrib.postgres_persistence import PostgresPersistence


# get Devs & Contributors
def get_user_list(key):
      # Import here to evade a circular import
      with open('{}/tg_bot/{}'.format(os.getcwd(), 'elevated_users.json'),
                'r') as royals:
              return json.load(royals)[key]

# enable logging
fileConfig('logging.ini')
log = logging.getLogger('[RentalBot]')
logging.getLogger('ptbcontrib.postgres_persistence.postgrespersistence').setLevel(logging.WARNING)


# if python version < 3.9, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
	log.error(
	    "[@LustPriest] You MUST have a python version of at least 3.9! Multiple features depend on this. Bot quitting."
	)
	quit(1)


# Some Important Things
from tg_bot.config import Rental as Rent
API_ID = Rent.API_ID
API_HASH = Rent.API_HASH
DB_URI = Rent.DB_URI
ERROR_DUMP = Rent.ERROR_DUMP
GBAN_LOGS = Rent.GBAN_LOGS
JOIN_LOGGER = Rent.JOIN_LOGGER
MESSAGE_DUMP = Rent.MESSAGE_DUMP
TOKEN = Rent.TOKEN
SUPPORT_CHAT = Rent.SUPPORT_CHAT
WALL_API = Rent.WALL_API

# Devs & Contributors
OWNER_ID = Rent.OWNER_ID
DEV_USERS = [OWNER_ID] + get_user_list("devs")
SUDO_USERS = [OWNER_ID] + get_user_list("sudos")
SUPPORT_USERS = get_user_list("supports")
SARDEGNA_USERS = get_user_list("sardegnas")
WHITELIST_USERS = get_user_list("whitelists")


# setup
updater = tg.Updater(TOKEN, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10}, persistence=PostgresPersistence(SESSION))
dispatcher = updater.dispatcher
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
StartTime = time.time()
IMPORTED = {}

# Load at end to ensure all prev variables have been set
from tg_bot.modules.helper_funcs.handlers import CustomCommandHandler
tg.CommandHandler = CustomCommandHandler
