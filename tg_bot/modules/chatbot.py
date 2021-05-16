import html
import requests
from time import sleep, time

from telegram import Update, ParseMode
from telegram.utils.helpers import mention_html
from telegram.ext import CallbackContext, Filters
from telegram.error import BadRequest, RetryAfter, Unauthorized

from tg_bot import ERROR_DUMP
import tg_bot.modules.sql.chatbot_sql as sql
from tg_bot.modules.log_channel import gloggable
from tg_bot.modules.helper_funcs.chat_status import dev_plus
from tg_bot.modules.helper_funcs.chat_status import user_admin
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigmsg



@kigcmd(command='chatbot', pass_args=True, filters=Filters.chat_type.groups)
@user_admin
@gloggable
def chatmode(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    is_chat = sql.is_chat(chat.id)
    args = message.text.split(" ", 1)
    if len(args) == 1:
        message.reply_text("Chatbot Status For This Group: <i>{}</i>".
               format("Enabled" if is_chat else "Disabled"),
               parse_mode=ParseMode.HTML,
               timeout=60,
        )
        return ""

    if args[1].lower() in ("yes", "on"):
        if not is_chat:
            sql.add_chat(chat.id)
            message.reply_text("Chatbot successfully enabled for this group!")
            logger = (f"<b>{html.escape(chat.title)}:</b>\n"
                      f"#AI_ENABLED\n"
                      f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n")
            return logger
        else:
            message.reply_text("Chatbot is already enabled for this group!")
            return ""

    elif args[1].lower() in ("off", "no"):
        if is_chat:
            sql.del_chat(chat.id)
            message.reply_text("Chatbot successfully disabled for this group!")
            logger = (
               f"<b>{html.escape(chat.title)}:</b>\n"
               f"#AI_DISABLED\n"
               f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            )
            return logger
        else:
            message.reply_text("Chatbot is already disabled for this group!")
            return ""

    elif args[1].lower() in ("random"):
        if not is_chat:
            sql.add_chat(chat.id, True)
            message.reply_text("Chatbot successfully enabled for this group!")
            logger = (
               f"<b>{html.escape(chat.title)}:</b>\n"
               f"#AI_ENABLED\n"
               f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            )
            return logger
        else:
            message.reply_text("Chatbot is already enabled for this group!")
            return ""

    else:
         message.reply_text("Chatbot Status For This Group: <i>{}</i>".
                format("Enabled" if is_chat else "Disabled"),
                parse_mode=ParseMode.HTML,
                timeout=60,
         )
         return ""


def check_message(context: CallbackContext, message):
    if message.text.lower() == f"@{context.bot.username}".lower():
        return True
    reply_msg = message.reply_to_message
    if reply_msg:
        if reply_msg.from_user.id == context.bot.id:
            return True
    else:
        return False

def get_response(update: Update, _):
     user = update.effective_user
     message = update.effective_message

     url = "https://acobot-brainshop-ai-v1.p.rapidapi.com/get"
     querystring = {
          "bid": "156213",
          "key": "AFL4yzDEQfAQkbyZ",
          "uid": user.id,
          "msg": message.text
     }
     headers = {
         'x-rapidapi-key': "e91d04a576mshac8d48e78a1f675p1d378fjsnc50315bee616",
         'x-rapidapi-host': "acobot-brainshop-ai-v1.p.rapidapi.com"
     }

     response = requests.request("GET", url, headers=headers, params=querystring)
     return response.text


@kigmsg(Filters.all & (~Filters.update.edited_message & ~Filters.forwarded) & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")) & Filters.chat_type.groups)
def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    is_chat = sql.is_chat(chat.id)
    bot = context.bot
    if not is_chat:
        return
    if message.text and not message.document:
        if not check_message(context, message):
            return
        try:
            bot.send_chat_action(chat.id, action='typing')
            rep = get_response(update)
            sleep(0.5)
            message.reply_text(rep, timeout=60)
        except RetryAfter as e:
            return
        except BadRequest as br:
            bot.sendMessage(
                   ERROR_DUMP,
                   f"AI ERROR: BadRequest \nChat: {'@' + chat.username or chat.title} (<code>{chat.id}</code>)\n\n{br}",
                   parse_mode=ParseMode.HTML,
            )
        except Unauthorized as u:
            bot.sendMessage(
                   ERROR_DUMP,
                   f"AI ERROR: Unauthorized \nChat: {'@' + chat.username or chat.title} (<code>{chat.id}</code>)\n\n{u}",
                   parse_mode=ParseMode.HTML,
            )
        except Exception as e:
            bot.sendMessage(
                   ERROR_DUMP,
                   f"AI ERROR: Exception \nChat: {'@' + chat.username or chat.title} (<code>{chat.id}</code>)\n\n{e}",
                   parse_mode=ParseMode.HTML,
            )


@kigcmd(command='listchatbot')
@dev_plus
def listchatbot(update: Update, context: CallbackContext):
    chats = sql.get_all_chats()
    message = update.effective_message
    totalchats = "<b>AI-Enabled Chats</b>:\n"
    for chat in chats:
        x = None

        try:
            x = context.bot.get_chat(int(*chat))
        except BadRequest:
            sql.rem_chat(*chat)
        except Unauthorized:
            sql.rem_chat(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)

        if x is not None:
            chat_id = x.id
            title = x.title
            uname = x.username if x.username else None
            fullname = f"<a href='https://t.me/'{uname}>{title}</a>" if uname is not None else title
            totalchats += f"\n• {fullname} (<code<{chat_id}</code>)"

    if totalchats.endswith(":\n"):
        message.reply_text("There Are No Active Chats With AI Feature!")
        return
    message.reply_text(
         totalchats,
         timeout=60,
         parse_mode=ParseMode.HTML,
         disable_web_page_preview=True,
    )



__mod_name__ = "Chatbot"
__command_list__ = ["chatbot", "listchatbot"]
