from telegram import TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler

from tg_bot import RentalBot, dispatcher
from tg_bot.modules.helper_funcs.chat_status import dev_plus


@dev_plus
def allow_groups(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        state = "Lockdown is " + "on" if not SaitamaRobot.ALLOW_CHATS else "off"
        update.effective_message.reply_text(f"Current state: {state}")
        return
    if args[0].lower() in ["off", "no"]:
        RentalBot.ALLOW_CHATS = True
    elif args[0].lower() in ["yes", "on"]:
        RentalBot.ALLOW_CHATS = False
    else:
        update.effective_message.reply_text("Format: /lockdown Yes/No or Off/On")
        return
    update.effective_message.reply_text("Done! Lockdown value toggled.")


@dev_plus
def leave(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args
    if args:
        chat_id = str(args[0])
        try:
            bot.leave_chat(int(chat_id))
            update.effective_message.reply_text("Left chat.")
        except TelegramError:
            update.effective_message.reply_text("Failed to leave chat for some reason.")
    else:
        update.effective_message.reply_text("Send a valid chat ID")



LEAVE_HANDLER = CommandHandler("leave", leave, run_async=True)
ALLOWGROUPS_HANDLER = CommandHandler("lockdown", allow_groups, run_async=True)

dispatcher.add_handler(LEAVE_HANDLER)
dispatcher.add_handler(ALLOWGROUPS_HANDLER)

__mod_name__ = "Dev"
__handlers__ = [LEAVE_HANDLER, ALLOWGROUPS_HANDLER]
