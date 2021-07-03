import html
from gpytranslate import SyncTranslator

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from tg_bot.modules.helper_funcs.decorators import kigcmd



__mod_name__ = "Translator"
trans = SyncTranslator()


@kigcmd(command=['tr', 'tl'])
def translate(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    reply_msg = message.reply_to_message
    if not reply_msg:
        message.reply_text("Reply to a message to translate it!")
        return
    if reply_msg.caption:
        to_translate = reply_msg.caption
    elif reply_msg.text:
        to_translate = reply_msg.text
    try:
        args = message.text.split()[1].lower()
        if "//" in args:
            source = args.split("//")[0]
            dest = args.split("//")[1]
        else:
            source = trans.detect(to_translate)
            dest = args
    except IndexError:
        source = trans.detect(to_translate)
        dest = 'en'
    translation = trans(to_translate,
                        sourcelang=source, 
                        targetlang=dest)
    reply = f"Translated from <i>{source}</i> to <i>{dest}</i>:\n<code>{html.escape(translation.text)}</code>"

    message.reply_text(reply, parse_mode=ParseMode.HTML)


@kigcmd(command='langs')
def languages(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(
        "Click on the button below to see the list of supported language codes.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Language codes", url="https://telegra.ph/Lang-Codes-03-19-3")]]),
        disable_web_page_preview=True,
    )
