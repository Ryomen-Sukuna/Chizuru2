from contextlib import suppress
from telegram.error import Unauthorized
from telegram import TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler

from tg_bot import dispatcher
from tg_bot.modules.helper_funcs.chat_status import dev_plus


@dev_plus
def leave(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args

    if args and len(args) > 5:
        chat_id = str(args[0])
        try:
            bot.leave_chat(int(chat_id))
        except TelegramError as te:
            if update.effective_chat.id != chat_id:
                with suppress(TelegramError):
                    update.effective_message.reply_text(f"I Could Not Leave That Group(Dunno Why Thooo). \n\nReason - TelegramError\n {te}")
                return
        if update.effective_chat.id != chat_id:
            with suppress(Unauthorized):
                update.effective_message.reply_text(f"I Could Not Leave That Group(Dunno Why Thooo).")
    else:
        update.effective_message.reply_text("Send a valid Chat Id.")



LEAVE_HANDLER = CommandHandler("leave", leave, run_async=True)
dispatcher.add_handler(LEAVE_HANDLER)

__mod_name__ = "Dev"
__handlers__ = [LEAVE_HANDLER]
