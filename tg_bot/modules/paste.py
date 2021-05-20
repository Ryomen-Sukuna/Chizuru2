import requests

from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram.utils.helpers import escape_markdown

from tg_bot.modules.helper_funcs.decorators import kigcmd



@kigcmd(command='paste', pass_args=True)
def paste(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message

    if message.reply_to_message:
        data = message.reply_to_message.text

    elif len(args) >= 1:
        data = message.text.split(" ", 1)[1]

    else:
        message.reply_text("What am I supposed to do with this?")
        return

    key = (
        requests.post("https://nekobin.com/api/documents", json={"content": data})
        .json()
        .get("result")
        .get("key")
    )

    url = f"https://nekobin.com/{key}"

    reply_text = f"Nekofied to *Nekobin* : {url}"

    message.reply_text(
        reply_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
    )


@kigcmd(command='getpaste', pass_args=True)
def get_paste_content(update: Update, context: CallbackContext):
    args = context.args
    burl = 'nekobin.com/'
    BURL = 'https://nekobin.com/'
    message = update.effective_message
    chat = update.effective_chat  # type: Optional[Chat]

    if message.reply_to_message:
        key = message.reply_to_message.text

    elif len(args) >= 1:
        key = message.text.split(" ", 1)[1]

    else:
        message.reply_text("Please supply a nekobin url!")
        return

    if ((key == burl) or (key == BURL)):
        message.reply_text("Please supply a valid nekobin url!")
        return

    format1 = f'{BURL}/'
    format2 = f'{BURL}/raw'
    format3 = f'{burl}/'
    format4 = f'{burl}/raw'

    if key.startswith(format1):
        key = key[len(format1):]
    elif key.startswith(format2):
        key = key[len(format2):]
    elif key.startswith(format3):
        key = key[len(format3):]
    elif key.startswith(format4):
        key = key[len(format4):]
    else:
        message.reply_text("Please supply a valid nekobin url!")
        return

    result = requests.get(f'{BURL}/raw/{key}')
    if result.status_code != 200:
        try:
            res = result.json()
            message.reply_text(res['message'])
        except Exception as e:
            if result.status_code == 404:
                message.reply_text(
                    "Failed to reach dogbin",
                )
            else:
                message.reply_text(
                    f"Unknown error occured due to {e}",
                )
        result.raise_for_status()

    message.reply_text(
       f"```{escape_markdown(result.text)}```",
       parse_mode=ParseMode.MARKDOWN,
    )

