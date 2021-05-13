import html
import time
import requests
import datetime

from telegram.error import BadRequest
from telegram.utils.helpers import mention_html
from telegram import Update, MessageEntity, ParseMode
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, Filters, CallbackContext

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
import tg_bot.modules.helper_funcs.health as hp
from tg_bot.modules.helper_funcs.get_time import get_time as get_readable_time

MARKDOWN_HELP = f"""
Markdown is a very powerful formatting tool supported by telegram. {dispatcher.bot.first_name} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.

- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>

- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.

Keep in mind that your message <b>MUST</b> contain some text other than just a button!
"""

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
    message = update.effective_message
    chat = update.effective_chat
    user_id = extract_user(update.effective_message, args)

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
        message.reply_text("I can't extract a user from this.")
        return

    else:
        return

    try:
        MsG = message.reply_text("Just A Second...")
    except:
        return

    text = (
        f"<b>• User Information:</b>\n"
        f"\n∘ ID: <code>{user.id}</code>"
        f"\n∘ First Name: {html.escape(user.first_name)}"
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
           status = status = bot.get_chat_member(chat.id, user.id).status
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
                text += f"\n∘ Admin Title: <code>{custom_title}</code> \n"
    except BadRequest:
        pass

    if user_id not in [bot.id, 777000, 1087968824]:                                                                                         
       if user.first_name != "":
          userhp = hp.hpmanager(user)
          text += f"\n∘ Health: <code>{userhp['earnedhp']}/{userhp['totalhp']}</code> ∙ <code>{userhp['percentage']}% </code> \n  {hp.make_bar(int(userhp['percentage']))}\n "                                                                                         
    else:
       text += "\n"

   
    if user.id == OWNER_ID:
      # text += "\n<b>This Person Is My Master!</b>"
        text += ""

    elif user.id in DEV_USERS:
        text += "\n∘ <b>DEV USER: </b>Yes!"
        
    elif user.id in SUDO_USERS:
        text += "\n∘ <b>SUDO USER: </b>Yes!"
        
    elif user.id in SUPPORT_USERS:
        text += "\n∘ <b>SUPPORT USER: </b>Yes!"
       
    elif user.id in WHITELIST_USERS:
        text += "\n∘ <b>WHITELIST USER: </b>Yes!"


    text += "\n"
    for mod in USER_INFO:
        if mod.__mod_name__ == "Users":
            continue

        try:
            mod_info = mod.__user_info__(user.id)
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id)
        if mod_info:
            text += "\n" + mod_info

    try:
        MsG.edit_text(
            text,
            timeout=60,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    except:
        pass


@user_admin
@kigcmd(command='echo', pass_args=True, filters=Filters.chat_type.groups)
def echo(update: Update, _):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)

    message.delete()

@kigcmd(command='markdownhelp', filters=Filters.chat_type.private)
def markdown_help(update: Update, _):
    chat = update.effective_chat
    update.effective_message.reply_text((gs(chat.id, "markdown_help_text")), parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, `code`, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )

@sudo_plus
@kigcmd(command='ping')
def ping(update: Update, _):
    msg = update.effective_message
    start_time = time.time()
    message = msg.reply_text("Pinging...")
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 3)
    message.edit_text(
        "*Pong!!!*\n`{}ms`".format(ping_time), parse_mode=ParseMode.MARKDOWN
    )


def get_help(chat):
    return gs(chat, "misc_help")



__mod_name__ = "Misc"
