from contextlib import suppress
from telegram.error import Unauthorized
from telegram import Update, ParseMode, TelegramError
from telegram.ext import CallbackContext, CommandHandler

from tg_bot import dispatcher
from tg_bot.modules.helper_funcs.chat_status import dev_plus


@dev_plus
def leave(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args

    if args and len(args[0]) > 5:
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


@dev_plus
def pip_install(update: Update, context: CallbackContext):
    message = update.effective_message
    args = context.args
    if not args:
        message.reply_text("Enter a package name.")
        return
    if len(args) >= 1:
        cmd = "py -m pip install {}".format(' '.join(args))
        process = subprocess.Popen(
            cmd.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,
        )
        stdout, stderr = process.communicate()
        reply = ""
        stderr = stderr.decode()
        stdout = stdout.decode()
        if stdout:
            reply += f"*Stdout*\n`{stdout}`\n"
        if stderr:
            reply += f"*Stderr*\n`{stderr}`\n"

        message.reply_text(text=reply, parse_mode=ParseMode.MARKDOWN)



LEAVE_HANDLER = CommandHandler("leave", leave, run_async=True)
PIP_INSTALL_HANDLER = CommandHandler("install", pip_install, run_async=True)
dispatcher.add_handler(LEAVE_HANDLER)
dispatcher.add_handler(PIP_INSTALL_HANDLER)


__mod_name__ = "Dev"
__handlers__ = [LEAVE_HANDLER, PIP_INSTALL_HANDLER]
