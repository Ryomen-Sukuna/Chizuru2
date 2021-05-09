import html
import json
import random
import time
import urllib.request
import urllib.parse
import requests
from telegram import ParseMode, Update, ChatPermissions
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.error import BadRequest

import tg_bot.modules.fun_strings as fun_strings
from tg_bot import dispatcher
from tg_bot.modules.language import gs
from tg_bot.modules.helper_funcs.chat_status import is_user_admin
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigcallback

@kigcmd(command='runs')
def runs(update: Update, context: CallbackContext):
    update.effective_message.reply_text(random.choice(fun_strings.RUN_STRINGS))

@kigcmd(command='slap')
def slap(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat

    reply_text = (
        message.reply_to_message.reply_text
        if message.reply_to_message
        else message.reply_text
    )

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id == bot.id:
        temp = random.choice(fun_strings.SLAP_Kigyō_TEMPLATES)

        if isinstance(temp, list):
            if temp[2] == "tmute":
                if is_user_admin(chat, message.from_user.id):
                    reply_text(temp[1])
                    return

                mutetime = int(time.time() + 60)
                bot.restrict_chat_member(
                    chat.id,
                    message.from_user.id,
                    until_date=mutetime,
                    permissions=ChatPermissions(can_send_messages=False),
                )
            reply_text(temp[0])
        else:
            reply_text(temp)
        return

    if user_id:

        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(slapped_user.first_name)

    else:
        user1 = bot.first_name
        user2 = curr_user

    temp = random.choice(fun_strings.SLAP_TEMPLATES)
    item = random.choice(fun_strings.ITEMS)
    hit = random.choice(fun_strings.HIT)
    throw = random.choice(fun_strings.THROW)
    reply = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(reply, parse_mode=ParseMode.HTML)

@kigcmd(command='pat')
def pat(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = str(update.message.text)
    try:
        msg = msg.split(" ", 1)[1]
    except IndexError:
        msg = ""
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )
    pats = []
    pats = json.loads(
        urllib.request.urlopen(
            urllib.request.Request(
                "http://headp.at/js/pats.json",
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; U; Linux i686) "
                    "Gecko/20071127 Firefox/2.0.0.11"
                },
            )
        )
        .read()
        .decode("utf-8")
    )
    if "@" in msg and len(msg) > 5:
        context.bot.send_photo(
            chat_id,
            f"https://headp.at/pats/{urllib.parse.quote(random.choice(pats))}",
            caption=msg,
        )
    else:
        context.bot.send_photo(
            chat_id,
            f"https://headp.at/pats/{urllib.parse.quote(random.choice(pats))}",
            reply_to_message_id=msg_id,
        )

@kigcmd(command='roll')
def roll(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(range(1, 7)))

@kigcmd(command='toss')
def toss(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(fun_strings.TOSS))

@kigcmd(command='decide')
def decide(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun_strings.DECIDE))

@kigcmd(command='table')
def table(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun_strings.TABLE))


@kigcallback(pattern=r'subhelp_.*')
def subhelp_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    query = update.callback_query
    if query.data == "subhelp_back":
        query.message.edit_text(
                text=gs(chat, "fun_help"),
                reply_markup=InlineKeyboardMarkup(
                        [InlineKeyboardButton(text="Back", callback_data="help_back"),]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )
    elif query.data == "subhelp_afk":
        query.message.edit_text(
                text=gs(chat, "afk_help"),
                reply_markup=InlineKeyboardMarkup(
                        [InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_stick":
        query.message.edit_text(
                text=gs(chat, "sticker_help"),
                reply_markup=InlineKeyboardMarkup(
                        [InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_tr":
        query.message.edit_text(
                text=gs(chat, "gtranslate_help"),
                reply_markup=InlineKeyboardMarkup(
                        [InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )



def get_help(chat):
    return gs(chat, "fun_help")


def get_help_btns():
     buttuns = [
        [InlineKeyboardButton(text="AFK", callback_data="subhelp_afk"),
        InlineKeyboardButton(text="Sticker", callback_data="subhelp_stick"),
        InlineKeyboardButton(text="Translation", callback_data="subhelp_tr"),],
        [InlineKeyboardButton(text="Back", callback_data="help_back"),],
     ]
     return buttuns

__mod_name__ = "Fun"
