from functools import wraps
from datetime import datetime
from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram.error import BadRequest, Unauthorized


def gloggable(func):
        @wraps(func)
        def glog_action(update, context, *args, **kwargs):
                result = func(update, context, *args, **kwargs)
                chat = update.effective_chat
                message = update.effective_message

                if result:
                        datetime_fmt = "%H:%M - %d-%m-%Y"
                        result += "\n<b>Event Stamp</b>: <code>{}</code>".format(
                            datetime.utcnow().strftime(datetime_fmt)
                        )

                        if message.chat.type == chat.SUPERGROUP and message.chat.username:
                            result += f'\n<b>Link:</b> <a href="https://t.me/{chat.username}/{message.message_id}">click here</a>'
                        if log_chat := str(GBAN_LOGS):
                                send_log(context, log_chat, chat.id, result)

                return result

        return glog_action

def send_log(
        context: CallbackContext, log_chat_id: str, orig_chat_id: str, result: str
    ):
        bot = context.bot
        try:
            bot.send_message(
                log_chat_id,
                result,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
                log.warning(excp.message)
                log.warning(result)
                log.exception("Could not parse")

                bot.send_message(
                    log_chat_id,
                    result
                    + "\n\nFormatting has been disabled due to an unexpected error.",
                )


def loggable(func):
     return func

__mod_name__ = "Logger"
