import logging
import os
import sys, json
import time
import spamwatch
import telegram.ext as tg
from telethon import TelegramClient
from telethon.sessions import MemorySession
from pyrogram import Client, errors
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid, ChannelInvalid
from pyrogram.types import Chat, User
from rich.logging import RichHandler
from ptbcontrib.postgres_persistence import PostgresPersistence


def get_user_list(key):
	try:  # Import here to evade a circular import
		from tg_bot.modules.sql import nation_sql
		royals = nation_sql.get_royals(key)
		return [a.user_id for a in royals]
	except:
		with open('{}/tg_bot/{}'.format(os.getcwd(), 'elevated_users.json'),
		          'r') as royals:
			return json.load(royals)[key]


# enable logging
FORMAT = "[RentalBot] %(message)s"
logging.basicConfig(handlers=[RichHandler()], level=logging.INFO, format=FORMAT, datefmt="[%X]")
logging.getLogger("pyrogram").setLevel(logging.WARNING)
log = logging.getLogger("rich")

# if version < 3.9, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
	log.error(
	    "[@LustPriest] You MUST have a python version of at least 3.9! Multiple features depend on this. Bot quitting."
	)
	quit(1)


class RentalBot:
	def __init__(self, rent):
		self.rent = rent
		self.SYS_ADMIN = self.rent.SYS_ADMIN
		self.OWNER_ID = self.rent.OWNER_ID
		self.OWNER_USERNAME = self.rent.OWNER_USERNAME
		self.APP_ID = self.rent.API_ID
		self.API_HASH = self.rent.API_HASH
		self.WEBHOOK = self.rent.WEBHOOK
		self.URL = self.rent.URL
		self.CERT_PATH = self.rent.CERT_PATH
		self.PORT = self.rent.PORT
		self.INFOPIC = self.rent.INFOPIC
		self.DEL_CMDS = self.rent.DEL_CMDS
		self.STRICT_GBAN = self.rent.STRICT_GBAN
		self.ALLOW_EXCL = self.rent.ALLOW_EXCL
		self.CUSTOM_CMD = self.rent.CUSTOM_CMD
		self.BAN_STICKER = self.rent.BAN_STICKER
		self.TOKEN = self.rent.TOKEN
		self.DB_URI = self.rent.DB_URI
		self.loadbeta = self.rent.LOAD.split()
		self.LOAD = list(map(str, self.loadbeta))
		self.MESSAGE_DUMP = self.rent.MESSAGE_DUMP
		self.JOIN_LOGGER = self.rent.JOIN_LOGGER
		self.ERROR_DUMP = self.rent.ERROR_DUMP
		self.GBAN_LOGS = self.rent.GBAN_LOGS
		self.no_loadbeta = self.rent.NO_LOAD.split()
		self.NO_LOAD = list(map(str, self.no_loadbeta))
		self.SPAMWATCH_API = self.rent.SPAMWATCH_API
		self.WALL_API = self.rent.WALL_API
		self.CF_API_KEY = self.rent.CF_API_KEY

	def init_sw(self):
            if self.SPAMWATCH_API is None:
                log.warning("SpamWatch API key is missing! Check your config.ini")
                return None
            else:
                try:
                    sw = spamwatch.Client(SPAMWATCH_API)
                    return sw
                except:
                    sw = None
                    log.warning("Can't connect to SpamWatch!")
                    return sw


from tg_bot.config import Rental

Rent = RentalBot(Rental)

SYS_ADMIN = Rent.SYS_ADMIN
OWNER_ID = Rent.OWNER_ID
OWNER_USERNAME = Rent.OWNER_USERNAME
APP_ID = Rent.APP_ID
API_HASH = Rent.API_HASH
WEBHOOK = Rent.WEBHOOK
URL = Rent.URL
CERT_PATH = Rent.CERT_PATH
PORT = Rent.PORT
INFOPIC = Rent.INFOPIC
DEL_CMDS = Rent.DEL_CMDS
ALLOW_EXCL = Rent.ALLOW_EXCL
CUSTOM_CMD = Rent.CUSTOM_CMD
BAN_STICKER = Rent.BAN_STICKER
TOKEN = Rent.TOKEN
DB_URI = Rent.DB_URI
LOAD = Rent.LOAD
MESSAGE_DUMP = Rent.MESSAGE_DUMP
JOIN_LOGGER = Rent.JOIN_LOGGER
ERROR_DUMP = Rent.ERROR_DUMP
GBAN_LOGS = Rent.GBAN_LOGS
NO_LOAD = Rent.NO_LOAD
DEV_USERS = [OWNER_ID] + get_user_list("devs")
SUDO_USERS = [OWNER_ID] + get_user_list("sudos")
SUPPORT_USERS = get_user_list("supports")
SARDEGNA_USERS = get_user_list("sardegnas")
WHITELIST_USERS = get_user_list("whitelists")
spamwatch_api = Rent.SPAMWATCH_API
WALL_API = Rent.WALL_API
CF_API_KEY = Rent.CF_API_KEY

# SpamWatch
sw = Rent.init_sw()

from tg_bot.modules.sql import SESSION

StartTime = time.time()
updater = tg.Updater(TOKEN, workers=min(32, os.cpu_count() + 4), request_kwargs={"read_timeout": 10, "connect_timeout": 10}, persistence=PostgresPersistence(SESSION))
client = TelegramClient(MemorySession(), APP_ID, API_HASH)
dispatcher = updater.dispatcher

kp = Client(":memory:", api_id=APP_ID, api_hash=API_HASH, bot_token=TOKEN, workers=min(32, os.cpu_count() + 4))
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
