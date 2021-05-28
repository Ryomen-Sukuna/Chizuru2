import html
import time
import requests
import datetime
from bs4 import BeautifulSoup

from telegram.error import BadRequest
from telegram import Update, MessageEntity, ParseMode
from telegram.utils.helpers import mention_html, escape_markdown
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Filters, CommandHandler, CallbackContext

from tg_bot import (
    dispatcher,
    OWNER_ID,
    DEV_USERS,
    SUDO_USERS,
    SUPPORT_USERS,
    WHITELIST_USERS,
    StartTime
)
from tg_bot.__main__ import STATS, USER_INFO, TOKEN
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot.modules.helper_funcs.chat_status import user_admin, sudo_plus
from tg_bot.modules.helper_funcs.extraction import extract_user
import tg_bot.modules.sql.users_sql as sql
from tg_bot.modules.language import gs
from tg_bot.modules.helper_funcs.decorators import kigcmd
from tg_bot.modules.helper_funcs.get_time import get_time


@kigcmd(command='gifid')
def gifid(update: Update, _):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.animation:
        update.effective_message.reply_text(
            f"Gif ID:\n<code>{msg.reply_to_message.animation.file_id}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text("Please reply to a gif to get its ID.")


@kigcmd(command='info', pass_args=True)
def info(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args
    chat = update.effective_chat
    message = update.effective_message
    user_id = extract_user(message, args)

    if user_id:
        user = bot.get_chat(user_id)

    elif not message.reply_to_message and not args:
        user = message.from_user

    elif not message.reply_to_message and (
        not args
        or (
            len(args) >= 1
            and not args[0].startswith("@")
            and not args[0].isdigit()
            and not message.parse_entities([MessageEntity.TEXT_MENTION])
        )
    ):
        user = message.from_user

    else:
        return

    try:
        MsG = message.reply_text("Just A Second...")
    except:
        return

    text = (
        f"<b>• User Information:</b>\n"
        f"\n∘ ID: <code>{user.id}</code>"
        f"\n∘ First Name: {html.escape(user.first_name) or '<code>Deleted Account</code>'}"
    )

    if user.last_name:
        text += f"\n∘ Last Name: {html.escape(user.last_name)}"

    if user.username:
        text += f"\n∘ Username: @{html.escape(user.username)}"

    text += f"\n∘ Profile Link: <a href='tg://openmessage?user_id={user.id}'>Here</a>\n"


    num_chats = sql.get_user_num_chats(user.id)
    text += f"\n∘ Mutual Chats: <code>{num_chats}</code>"

    try:
        if chat.type != 'private':
           status = bot.get_chat_member(chat.id, user.id).status
           if status:
               if status in "left":
                   text += "\n∘ Chat Status: Not Here!"
               elif status == "member":
                   text += "\n∘ Chat Status: Member!"
               elif status in "administrator":
                   text += "\n∘ Chat Status: Admin!"
               elif status in "creator": 
                   text += "\n∘ Chat Status: Creator!"
    except BadRequest:
        pass

    try:
        user_member = chat.get_member(user.id)
        if user_member.status == "administrator":
            result = requests.post(
                f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id={chat.id}&user_id={user.id}"
            )
            result = result.json()["result"]
            if "custom_title" in result.keys():
                custom_title = result["custom_title"]
                text += f"\n∘ Admin Title: <code>{custom_title}</code>"
    except BadRequest:
        pass

   
    if user.id == OWNER_ID:
      # text += "\n<b>This Person Is My Creator!</b>"
        text += ""

    elif user.id in DEV_USERS:
        text += "\n∘ <b>DEV USER: </b>Yes!"
        
    elif user.id in SUDO_USERS:
        text += "\n∘ <b>SUDO USER: </b>Yes!"
        
    elif user.id in SUPPORT_USERS:
        text += "\n∘ <b>SUPPORT USER: </b>Yes!"
       
    elif user.id in WHITELIST_USERS:
        text += "\n∘ <b>WHITELIST USER: </b>Yes!"


    try:
        MsG.edit_text(
            text,
            timeout=60,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except:
        return


@kigcmd(command="ud")
def ud(update: Update, _):
    message = update.effective_message
    text =  message.text.split(" ", 1)

    if len(text) == 1:
        message.reply_text(
           "_Format:_ `/ud <anything>`",
           parse_mode=ParseMode.MARKDOWN,
        )
        return

    results = requests.get(
        "https://api.urbandictionary.com/v0/define?term=" + text
    ).json()

    try:
        results = f"*{escape_markdown(text)}*:\n\nResult*:* {escape_markdown(results.get('list')[0].get('definition'))}\n\nExample*:* _{escape_markdown(results.get('list')[0].get('example'))}_"
    except:
        results = "No results found!"

    message.reply_text(results, parse_mode=ParseMode.MARKDOWN)


@kigcmd(command='echo', pass_args=True, filters=Filters.chat_type.groups)
@user_admin
def echo(update: Update, _):
    message = update.effective_message
    args = message.text.split(" ", 1)

    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)

    message.delete()


def send_formatting(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        gs(update.effective_chat, "greetings_format_help").format(context.bot.first_name),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
               [InlineKeyboardButton(text="Markdown", callback_data="subhelp_wel_markdown"),
               InlineKeyboardButton(text="Fillings", callback_data="subhelp_wel_fillings")],
               [InlineKeyboardButton(text="Random Content", callback_data="subhelp_wel_random")],
        ]),
    )


@kigcmd(command='formatting')
def formatting(update: Update, context: CallbackContext):
    chat = update.effective_chat

    if chat.type == "private":
        send_formatting(update, context)
    else:
        update.effective_message.reply_text(
            "Contact me in PM for help!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Help", url=f"t.me/{dispatcher.bot.username}?start=formatting")]]),
        )


@kigcmd(command='ping')
@sudo_plus
def ping(update: Update, _):
    msg = update.effective_message
    start_time = time.time()
    message = msg.reply_text("Pinging...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 3)
    message.edit_text(
        "*Pong!!!*\n`{}ms`".format(ping_time),
        parse_mode=ParseMode.MARKDOWN,
    )


def get_help(chat):
    return gs(chat, "misc_help")



__mod_name__ = "Misc"
