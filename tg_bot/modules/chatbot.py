import html
import requests
from time import sleep, time

from telegram import Update
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.ext import CallbackContext, Filters
from telegram.utils.helpers import mention_html

import tg_bot.modules.sql.chatbot_sql as sql
from tg_bot.modules.log_channel import gloggable
from tg_bot.modules.helper_funcs.chat_status import dev_plus
from tg_bot.modules.helper_funcs.chat_status import user_admin
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigmsg



@kigcmd(command='chatbot', pass_args=True, filters=Filters.chat_type.groups)
@user_admin
@gloggable
def chatmode(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    is_chat = sql.is_chat(chat.id)
    args = msg.text.split(" ", 1)
    if len(args) == 1:
        msg.reply_text("??")
        return ""
    if args[1].lower() in ("yes", "on"):
        if not is_chat:
            sql.add_chat(chat.id)
            msg.reply_text("AI successfully enabled for this chat!")
            logger = (f"<b>{html.escape(chat.title)}:</b>\n"
                      f"#AI_ENABLED\n"
                      f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n")
            return logger
        else:
            msg.reply_text("AI is already enabled for this chat!")
            return ""
    elif args[1].lower() in ("off", "no"):
        if is_chat:
            sql.del_chat(chat.id)
            msg.reply_text("AI successfully disabled for this chat!")
            logger = (f"<b>{html.escape(chat.title)}:</b>\n"
                      f"#AI_DISABLED\n"
                      f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n")
            return logger
        else:
            msg.reply_text("AI is already disabled for this chat!")
            return ""


def check_message(context: CallbackContext, message):
    if message.text.lower() == f"@{context.bot.get_me().username}".lower():
        return True
    reply_msg = message.reply_to_message
    if reply_msg:
        if reply_msg.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False

def get_response(user, msg):
     response = requests.get(f"http://api.brainshop.ai/get?bid=156213&key=AFL4yzDEQfAQkbyZ&uid={user.id}&msg={msg.text}").json()

     return response[cnt]


@kigmsg(Filters.all & (~Filters.update.edited_message & ~Filters.forwarded) & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")) & Filters.groups)
def chatbot(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    is_chat = sql.is_chat(chat.id)
    bot = context.bot
    if not is_chat:
        return
    if msg.text and not msg.document:
        if not check_message(context, msg):
            return
        try:
            bot.send_chat_action(chat.id, action='typing')
            rep = get_response(user, msg)
            sleep(0.3)
            msg.reply_text(rep, timeout=60)
        except BadRequest as b:
            msg.reply_text(b, timeout=60)


@kigcmd(command='listchatbot')
@dev_plus
def listchatbot(update: Update, context: CallbackContext):
    chats = sql.get_all_chats()
    text = "<b>AI-Enabled Chats:</b>\n\n"
    for chat in chats:
        try:
            x = context.bot.get_chat(int(*chat))
            name = x.title if x.title else x.first_name
            text += f"\n• <code>{name}</code>"
        except BadRequest:
            sql.rem_chat(*chat)
        except Unauthorized:
            sql.rem_chat(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)
    update.effective_message.reply_text(text, parse_mode="HTML")



__mod_name__ = "Chatbot"
__command_list__ = ["chatbot", "listchatbot"]
