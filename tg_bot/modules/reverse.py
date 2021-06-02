import os
import re
import urllib
import requests
from bs4 import BeautifulSoup

from telegram import TelegramError
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.modules.helper_funcs.decorators import kigcmd


opener = urllib.request.build_opener()
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.68"
opener.addheaders = [("User-agent", useragent)]


@kigcmd(command=["reverse", "grs"])
def reverse(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat_id = update.effective_chat.id
    rtmid = msg.message_id
    imagename = "googlereverse.png"

    if os.path.isfile(imagename):
        os.remove(imagename)

    reply = msg.reply_to_message
    if reply:
        if reply.sticker:
            file_id = reply.sticker.file_id
        elif reply.photo:
            file_id = reply.photo[-1].file_id
        elif reply.document:
            file_id = reply.document.file_id
        else:
             msg.reply_text("Reply To An Image Or Sticker To Lookup!")
             return

        image_file = context.bot.get_file(file_id)
        image_file.download(imagename)
    else:
         msg.reply_text(
             "Please Reply To A Sticker, Or An Image To Search It!", parse_mode=ParseMode.MARKDOWN,
         )
         return

    MsG = context.bot.send_message(chat_id,
                                   "Let Me See...",
                                   reply_to_message_id=rtmid,
    )
    try:
        searchUrl = "https://www.google.com/searchbyimage/upload"
        multipart = {
            "encoded_image": (imagename, open(imagename, "rb")),
            "image_content": "",
        }
        response = requests.post(searchUrl, files=multipart, allow_redirects=False)
        fetchUrl = response.headers.get("Location")

        os.remove(imagename)
        if response != 400:
            MsG.edit_text("Downloading...")
        else:
            MsG.edit_text("Google Told Me To Go Away...")
            return

        match = ParseSauce(fetchUrl + "&hl=en")
        guess = match.get("best_guess")
        MsG.edit_text("Uploading...")
        if match.get("override") and not match.get("override") == "":
            imgspage = match.get("override")
        else:
            imgspage = match.get("similar_images")


        if guess and imgspage:
            MsG.edit_text("Hmmm....")
        else:
            MsG.edit_text("Couldn't Find Anything!")
            return

        buttuns = [[InlineKeyboardButton(text="Images Link", url=fetchUrl)], [InlineKeyboardButton(text="Similar Images", url=imgspage)]]
        search_result = guess.replace("Possible related search: ", "")

        MsG.edit_text("*Search Results*: \n\n`{}`".format(search_result),
                      parse_mode=ParseMode.MARKDOWN,
                      reply_markup=InlineKeyboardMarkup(buttuns),
        )

    except BadRequest as Bdr:
        MsG.edit_text(f"ERROR! - _Couldn't Find Anything!!_ \n\n*Reason*: BadRequest!\n\n{Bdr}", parse_mode=ParseMode.MARKDOWN)
    except TelegramError as Tge:
        MsG.edit_text(f"ERROR! - _Couldn't Find Anything!!_ \n\n*Reason*: TelegramError!\n\n{Tge}", parse_mode=ParseMode.MARKDOWN)
    except Exception as Exp:
        MsG.edit_text(f"ERROR! - _Couldn't Find Anything!!_ \n\n*Reason*: Exception!\n\n{Exp}", parse_mode=ParseMode.MARKDOWN)
    except:
        MsG.edit_text("ERROR! - _Couldn't Find Anything!!_ \n\n*Reason*: Duno!", parse_mode=ParseMode.MARKDOWN)


def ParseSauce(googleurl):
    source = opener.open(googleurl).read()
    soup = BeautifulSoup(source, "html.parser")

    results = {"similar_images": "", "override": "", "best_guess": ""}

    try:
        for bess in soup.findAll("a", {"class": "PBorbe"}):
             url = "https://www.google.com" + bess.get("href")
             results.get("override") = url
    except:
        pass

    for similar_image in soup.findAll("input", {"class": "gLFyf"}):
         url = "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote_plus(similar_image.get("value"))
         results.get("similar_images") = url

    for best_guess in soup.findAll("div", attrs={"class": "r5a77d"}):
         results.get("best_guess") = best_guess.get_text()

    return results