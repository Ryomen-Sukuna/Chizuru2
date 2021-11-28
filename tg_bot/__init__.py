import os
import sys
import time
import json
import logging
from typing import List
from logging.config import fileConfig

import telegram.ext as tg
from telethon import TelegramClient
from telethon.sessions import MemorySession


# get Devs & Contributors
def get_user_list(key) -> List:
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
DRAMA_URL = Rent.DRAMA_URL


# Devs & Contributors
OWNER_ID = Rent.OWNER_ID
EX_OWNER = Rent.EX_OWNER
DEVS = get_user_list("devs")
SUDOS = get_user_list("sudos")
SUPPORTS = get_user_list("supports")
SARDEGNAS = get_user_list("sardegnas")
WHITELISTS = get_user_list("whitelists")

DEV_USERS = list(set(DEVS + [OWNER_ID] + [EX_OWNER]))
SUDO_USERS = list(set(SUDOS + DEV_USERS))
SUPPORT_USERS = list(set(SUPPORTS + SUDO_USERS))
SARDEGNA_USERS = list(set(SARDEGNAS + SUPPORT_USERS))
WHITELIST_USERS = list(set(WHITELISTS + SARDEGNA_USERS))

# setup
updater = tg.Updater(TOKEN, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10})
dispatcher = dp = updater.dispatcher
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
StartTime = time.time()

# Load at end to ensure all prev variables have been set
from tg_bot.modules.helper_funcs.handlers import CustomCommandHandler
tg.CommandHandler = CustomCommandHandler
