import os
import sys
import time
import json
import logging
from logging.config import fileConfig

import telegram.ext as tg
from telethon import TelegramClient
from telethon.sessions import MemorySession
from pyrogram import Client, errors
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, ChannelInvalid
from pyrogram.types import Chat, User
from ptbcontrib.postgres_persistence import PostgresPersistence


StartTime = time.time()

def get_user_list(key):
      # Import here to evade a circular import
      with open('{}/tg_bot/{}'.format(os.getcwd(), 'elevated_users.json'),
                'r') as royals:
              return json.load(royals)[key]

# enable logging
fileConfig('logging.ini')
log = logging.getLogger('[RentalBot]')
logging.getLogger('ptbcontrib.postgres_persistence.postgrespersistence').setLevel(logging.WARNING)


# if version < 3.9, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
	log.error(
	    "[@LustPriest] You MUST have a python version of at least 3.9! Multiple features depend on this. Bot quitting."
	)
	quit(1)


from tg_bot.config import Rental as Rent

OWNER_ID = Rent.OWNER_ID
API_ID = Rent.API_ID
API_HASH = Rent.API_HASH
DEL_CMDS = Rent.DEL_CMDS
CUSTOM_CMD = Rent.CUSTOM_CMD
TOKEN = Rent.TOKEN
DB_URI = Rent.DB_URI
LOAD = list(map(str, Rent.LOAD.split()))
MESSAGE_DUMP = Rent.MESSAGE_DUMP
JOIN_LOGGER = Rent.JOIN_LOGGER
ERROR_DUMP = Rent.ERROR_DUMP
GBAN_LOGS = Rent.GBAN_LOGS
NO_LOAD = list(map(str, Rent.NO_LOAD.split()))
DEV_USERS = [OWNER_ID] + get_user_list("devs")
SUDO_USERS = [OWNER_ID] + get_user_list("sudos")
SUPPORT_USERS = get_user_list("supports")
SARDEGNA_USERS = get_user_list("sardegnas")
WHITELIST_USERS = get_user_list("whitelists")
WALL_API = Rent.WALL_API


from tg_bot.modules.sql import SESSION

updater = tg.Updater(TOKEN, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10}, persistence=PostgresPersistence(SESSION))
telethn = TelegramClient(MemorySession(), API_ID, API_HASH)
client = telethn
dispatcher = updater.dispatcher

kp = Client(":memory:", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN, workers=min(32, os.cpu_count() + 4))
apps = []
apps.append(kp)


async def get_entity(client, entity):
    entity_client = client
    if not isinstance(entity, Chat):
        try:
            entity = int(entity)
        except ValueError:
            pass
        except TypeError:
            entity = entity.id
        try:
            entity = await client.get_chat(entity)
        except (PeerIdInvalid, ChannelInvalid):
            for kp in apps:
                if kp != client:
                    try:
                        entity = await kp.get_chat(entity)
                    except (PeerIdInvalid, ChannelInvalid):
                        pass
                    else:
                        entity_client = kp
                        break
            else:
                entity = await kp.get_chat(entity)
                entity_client = kp
    return entity, entity_client

# Load at end to ensure all prev variables have been set
if CUSTOM_CMD and len(CUSTOM_CMD) >= 1:
    from tg_bot.modules.helper_funcs.handlers import CustomCommandHandler
    tg.CommandHandler = CustomCommandHandler
