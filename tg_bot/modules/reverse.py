import os
import re
import urllib
import requests
from typing import List
from bs4 import BeautifulSoup
from dataclasses import dataclass

from saucenao_api import SauceNao, BasicSauce

from telegram import TelegramError
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram import Update, ParseMode, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.modules.helper_funcs.decorators import kigcmd


opener = urllib.request.build_opener()
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.68"
opener.addheaders = [("User-agent", useragent)]


@dataclass
class LowdaLasan:
    photo_url: str
    text: str

class Souce:
    def __init__(self, api_key: str, minimal_similarity: float):
        self.minimal_similarity = minimal_similarity
        self.sauce_api = SauceNao(api_key=api_key)

    def provide_response(self, path_to_file: str) -> List[LowdaLasan]:
        with open(path_to_file, "rb") as file:
            request_results = self.sauce_api.from_file(file)

        responses = [self.gen_response_obj(r) for r in request_results
                     if r.similarity >= self.minimal_similarity]
        return responses

    def gen_response_obj(self, response: BasicSauce) -> LowdaLasan:
        text = f"{response.similarity}\n"
        if response.urls != []:
            text += "\n".join(response.urls)
        else:
            text += f"Title:{response.title}\n" if response.title is not None else ""
            text += f"Author:{response.author}\n" if response.author is not None else ""
        thumbnail_url = response.thumbnail
        return LowdaLasan(thumbnail_url, text)


def post_souce_results(bot, chat_id: str, results: List[RequestResult]):
        if results == []:
            bot.send_message(chat_id=chat_id, text="Nothing found(")
            return
        media = [InputMediaPhoto(r.photo_url) for r in results]
        # caption put to first media becouse tg shows only first caption
        caption = ("\n" + "-" * 50 + "\n").join(r.text for r in results)
        media[0].caption = caption
        bot.send_media_group(chat_id=chat_id, media=media)


@kigcmd(command=["souce"])
def soucenao(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat_id = update.effective_chat.id
    rtmid = msg.message_id
    imagename = "soucereverse.png"

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
        souce = Souce(os.environ.get("SOUCE_API", None), 0.8)
        result = souce.provide_response(imagename)
        post_souce_results(context.bot, chat_id, result)
        os.remove(imagename)

    except BadRequest as Bdr:
        MsG.edit_text(f"ERROR! - _Couldn't Find Anything!!_ \n\n*Reason*: BadRequest!\n\n{Bdr}", parse_mode=ParseMode.MARKDOWN)
    except TelegramError as Tge:
        MsG.edit_text(f"ERROR! - _Couldn't Find Anything!!_ \n\n*Reason*: TelegramError!\n\n{Tge}", parse_mode=ParseMode.MARKDOWN)
    except Exception as Exp:
        MsG.edit_text(f"ERROR! - _Couldn't Find Anything!!_ \n\n*Reason*: Exception!\n\n{Exp}", parse_mode=ParseMode.MARKDOWN)
    except:
        MsG.edit_text("ERROR! - _Couldn't Find Anything!!_ \n\n*Reason*: Duno!", parse_mode=ParseMode.MARKDOWN)



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
        if match.get("override") and (not match.get("override") == "" or not match.get("override") == None):
            imgspage = match.get("override")
        else:
            imgspage = match.get("similar_images")

        buttuns = []
        if guess:
            MsG.edit_text("Hmmm....")
            search_result = guess.replace("Possible related search: ", "")
            buttuns.append([InlineKeyboardButton(text="Images Link", url=fetchUrl)])
        else:
            MsG.edit_text("Couldn't Find Anything!")
            return

        if imgspage:
            buttuns.append([InlineKeyboardButton(text="Similar Images", url=imgspage)])

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
             results["override"] = url
    except:
        pass

    for similar_image in soup.findAll("input", {"class": "gLFyf"}):
         url = "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote_plus(similar_image.get("value"))
         results["similar_images"] = url

    for best_guess in soup.findAll("div", attrs={"class": "r5a77d"}):
         results["best_guess"] = best_guess.get_text()

    return results

