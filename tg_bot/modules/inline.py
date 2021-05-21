import os
import html
import json
import requests
import traceback
from uuid import uuid4
from typing import List

from telegraph import upload_file
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ParseMode, InlineQueryResultArticle, InputTextMessageContent


from pyrogram.types import InlineQueryResultArticle as IQRA, InputTextMessageContent as ITMC

from tg_bot import log, kp as app
import tg_bot.modules.sql.users_sql as sql
from tg_bot.modules.users import get_user_id
from tg_bot.modules.helper_funcs.misc import article
from tg_bot.modules.helper_funcs.decorators import kiginline



async def get_user_info(user):
    user = await app.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    mention = user.mention("Here")
    status = user.status
    dc_id = user.dc_id
    photo_id = user.photo.big_file_id if user.photo else None
    caption = f"""
**ID:** `{user_id}`
**DC:** {dc_id}
**Name:** {first_name, last_name or ''}
**Username:** {("@" + username) if username else "N/A"}
**Permalink:** {mention}
**Status:** {status}
"""
    return [caption, photo_id]

@app.on_inline_query()
async def inline_query_handler(client, query):
    try:
        text = query.query.strip().lower()
        answers = []
        if text.split()[0] == ".info":
            if len(text.split()) < 2:
                await client.answer_inline_query(
                    query.id,
                    results=answers,
                    switch_pm_text="User Info | info [USERNAME|ID]",
                    switch_pm_parameter="inline",
                )
                return

            txt = text.split()[1].strip()
            caption, photo_id = await get_user_info(txt)
            answers.append(IQRA(
                                 title="Found User.",
                                 input_message_content=ITMC(
                                                                caption, disable_web_page_preview=True,
                                                       ),
                           )
            )

            await client.answer_inline_query(
                query.id, results=answers, cache_time=5,
            )

    except Exception as e:
        e = traceback.format_exc()
        log.exception(e)
        return



def remove_prefix(text, prefix):
    if text.startswith(prefix):
        text = text.replace(prefix, "", 1)
    return text

@kiginline()
def inlinequery(update: Update, _) -> None:
    """
    Main InlineQueryHandler callback.
    """

    query = update.inline_query.query
    user = update.effective_user

    results: List = []
    inline_help_dicts = [
        {
            "title": "Anime",
            "description": "Search Anime & Manga On AniList.co",
            "message_text": "Click Here to search anime and manga on AniList.co",
            "thumb_urL": "https://telegra.ph/file/a546976e6f3ebf21a131a.jpg",
            "keyboard": ".anime ",
        },
        {
            "title": "Character",
            "description": "Search Characters on AniList.co",
            "message_text": "Click Here to search character on AniList.co",
            "thumb_urL": "https://telegra.ph/file/a546976e6f3ebf21a131a.jpg",
            "keyboard": ".char ",
        },
       # {
       #     "title": "Account info",
       #     "description": "Look up a Telegram account in my database",
       #     "message_text": "Click Here to look up a person in my database using their Telegram ID",
       #     "thumb_urL": "https://telegra.ph/file/57d5522a9d8fa56e3be27.jpg",
       #     "keyboard": ".info ",
       # },
    ]

    inline_funcs = {
        ".anime": media_query,
        ".char": character_query,
      # ".info": inlineinfo,
    }

    if (f := query.split(" ", 1)[0]) in inline_funcs:
        inline_funcs[f](remove_prefix(query, f).strip(), update, user)

    elif (f := query.split(" ", 1)[0]) in (".info"):
          return

    else:
        for ihelp in inline_help_dicts:
            results.append(
                article(
                    title=ihelp["title"],
                    description=ihelp["description"],
                    message_text=ihelp["message_text"],
                    thumb_url=ihelp["thumb_urL"],
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Click Here",
                                    switch_inline_query_current_chat=ihelp[
                                        "keyboard"
                                    ],
                                )
                            ]
                        ]
                    ),
                )
            )

        update.inline_query.answer(results, cache_time=5)


def inlineinfo(query: str, update: Update, context: CallbackContext) -> None:
    """Handle the inline query."""
    bot = context.bot
    query = update.inline_query.query
    user = update.effective_user

    try:
        search = str(query.split(" ", 1)[1])
    except IndexError:
        search = str(user.id)

    try:
        if search.isdigit() or search.isnumeric():
            user = bot.get_chat(int(search))
        elif search.startswith("@"):
            getuser = get_user_id(str(search))
            if getuser:
               user = bot.get_chat(int(getuser))
            else:
               user = bot.get_chat(str(search))
        else:
            user = bot.get_chat(search)
    except (BadRequest, ValueError):
        user = bot.get_chat(user.id)
    chat = update.effective_chat

    if os.path.isfile(f"inlineinfo{user.id}.jpg"):
        os.remove(f"inlineinfo{user.id}.jpg")

    text = (
        f"<b>• User Information:</b>\n"
        f"∘ ID: <code>{user.id}</code>\n"
        f"∘ First Name: {html.escape(user.first_name) if user.first_name is not None else '☠️ <code>Zombie</code> ☠️'}"
    )

    if user.last_name:
        text += f"\n∘ Last Name: {html.escape(user.last_name)}"

    if user.username:
        text += f"\n∘ Username: @{html.escape(user.username)}"

    text += f"\n∘ Profile Link: {mention_html(user.id, 'Here')}"

    sql.update_user(user.id, user.username)
    same_chats = sql.get_user_num_chats(user.id)
    if int(same_chats) >= 1:
         text += f"\n∘ Mutual Chats: <code>{same_chats}</code>"

    ispic = False
    try:
        profilepic = bot.get_user_profile_photos(user.id).photos[0][-1]
        userpic = bot.get_file(profilepic["file_id"])
        downloadpic = userpic.download(f"inlineinfo{user.id}.jpg")
        uploadpic = upload_file(downloadpic)
        os.remove(f"inlineinfo{user.id}.jpg")
        ispic = True
    # Incase user don't have profile pic
    except IndexError:
        ispic = False



    kb = InlineKeyboardMarkup(
               [
                  [
                    InlineKeyboardButton(
                          text="Search Again",
                          switch_inline_query_current_chat=".info ",
                    ),
                  ],
               ]
         )

    if ispic:
        try:
            results = [
              InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=f"{user.first_name or search} {user.last_name or ''}",
                    description=user.bio or "N/A",
                    thumb_url=f"https://telegra.ph{uploadpic[0]}",
                    input_message_content=InputTextMessageContent(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True),
                    reply_markup=kb,
              ),
            ]
        except:
            results = [
              InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=f"{user.first_name or search} {user.last_name or ''}",
                    description=user.bio or "N/A",
                    input_message_content=InputTextMessageContent(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True),
                    reply_markup=kb,
              ),
            ]
    else:
        results = [
           InlineQueryResultArticle(
              id=str(uuid4()),
              title=f"{user.first_name or search} {user.last_name or ''}",
              description=user.bio or "N/A",
              input_message_content=InputTextMessageContent(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True),
              reply_markup=kb,
           ),
        ]

    update.inline_query.answer(results, cache_time=5)



MEDIA_QUERY = '''query ($search: String) {
  Page (perPage: 10) {
    media (search: $search) {
      id
      title {
        romaji
        english
        native
      }
      type
      format
      status
      description
      episodes
      bannerImage
      duration
      chapters
      volumes
      genres
      synonyms
      averageScore
      airingSchedule(notYetAired: true) {
        nodes {
          airingAt
          timeUntilAiring
          episode
        }
      }
      siteUrl
    }
  }
}'''


def media_query(query: str, update: Update, context: CallbackContext) -> None:
    """
    Handle anime inline query.
    """
    results: List = []

    try:
        results: List = []
        r = requests.post('https://graphql.anilist.co',
                          data=json.dumps({'query': MEDIA_QUERY, 'variables': {'search': query}}),
                          headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
        res = r.json()
        data = res['data']['Page']['media']
        res = data
        for data in res:
            title_en = data["title"].get("english") or "N/A"
            title_ja = data["title"].get("romaji") or "N/A"
            format = data.get("format") or "N/A"
            type = data.get("type") or "N/A"
            bannerimg = data.get("bannerImage") or "https://telegra.ph/file/cc83a0b7102ad1d7b1cb3.jpg"
            try:
                des = data.get("description").replace("<br>", "").replace("</br>", "")
                description = des.replace("<i>", "").replace("</i>", "") or "N/A"
            except AttributeError:
                description = data.get("description")

            try:
                description = html.escape(description)
            except AttributeError:
                description = description or "N/A"

            if len((str(description))) > 700:
                description = description [0:700] + "....."

            avgsc = data.get("averageScore") or "N/A"
            status = data.get("status") or "N/A"
            genres = data.get("genres") or "N/A"
            genres = ", ".join(genres)
            img = f"https://img.anili.st/media/{data['id']}" or "https://telegra.ph/file/cc83a0b7102ad1d7b1cb3.jpg"
            aurl = data.get("siteUrl")


            kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Full Information",
                            url=aurl,
                        ),
                        InlineKeyboardButton(
                            text="Search Again",
                            switch_inline_query_current_chat=".anilist ",
                        ),

                    ],
                ])

            txt = f"<b>{title_en} | {title_ja}</b>\n"
            txt += f"<b>Format</b>: <code>{format}</code>\n"
            txt += f"<b>Type</b>: <code>{type}</code>\n"
            txt += f"<b>Average Score</b>: <code>{avgsc}</code>\n"
            txt += f"<b>Status</b>: <code>{status}</code>\n"
            txt += f"<b>Genres</b>: <code>{genres}</code>\n"
            txt += f"<b>Description</b>: <code>{description}</code>\n"
            txt += f"<a href='{img}'>&#xad</a>"

            results.append(
                InlineQueryResultArticle
                    (
                    id=str(uuid4()),
                    title=f"{title_en} | {title_ja} | {format}",
                    thumb_url=img,
                    description=f"{description}",
                    input_message_content=InputTextMessageContent(txt, parse_mode=ParseMode.HTML,
                                                                  disable_web_page_preview=False),
                    reply_markup=kb
                )
            )
    except Exception as e:

        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Search Again",
                        switch_inline_query_current_chat=".anime ",
                    ),

                ],
            ])

        results.append(

            InlineQueryResultArticle
                (
                id=str(uuid4()),
                title=f"Media {query} not found",
                input_message_content=InputTextMessageContent(f"Media {query} not found due to {e}", parse_mode=ParseMode.MARKDOWN,
                                                              disable_web_page_preview=True),
                reply_markup=kb
            )

        )

    update.inline_query.answer(results, cache_time=5)


CHAR_QUERY = '''query ($query: String) {
  Page (perPage: 15) {
        characters (search: $query) {
               id
               name {
                     first
                     middle
                     last
                     full
                     native
                     alternative
                     alternativeSpoiler
               }
               image {
                        large
                        medium
               }
               description
               gender
               dateOfBirth {
                              year
                              month
                              day
               }
               age
               siteUrl
               favourites
               modNotes
        }
    }
}'''

def character_query(query: str, update: Update, context: CallbackContext) -> None:
    """
    Handle character inline query.
    """
    results: List = []

    try:
        res = requests.post(
                    'https://graphql.anilist.co',
                    data=json.dumps({'query': CHAR_QUERY, 'variables': {'query': query}}),
                    headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
              ).json()

        data = res.get('data').get('Page').get('characters')
        res = data
        for data in res:
            name = data.get('name').get('full') or query
            nati_name = data.get('name').get('native') or 'N/A'
            alt_name = data.get('name').get('alternative') or 'N/A'
            favourite = data.get('favourites') or 'N/A'
            char_age = data.get('age', 'N/A')
            char_gender = data.get('gender') or 'N/A'
            thumb_url_large = data.get('image').get('large') or "https://telegra.ph/file/cc83a0b7102ad1d7b1cb3.jpg"
            site_url = data.get('siteUrl') or "https://anilist.co/characters"

            try:
                alt_name = data.get('name').get('alternative')
                neme = ""
                for altname in alt_name:
                     neme += f"`{altname}` ,"
                alt_name = f"{neme}"
            except:
                alt_name = data.get('name').get('alternative') or "N/A"

            try:
                des = data.get("description").replace("<br>", "").replace("</br>", "")
                description = des.replace("<i>", "").replace("</i>", "") or "N/A"
            except AttributeError:
                description = data.get("description")

            if len((str(description))) > 700:
                description = description [0:700] + "....."

            txt = f"*{name}* - (*{nati_name or 'N/A'}*)\n"
            txt += f"\n*Alternative*: {alt_name or 'N/A'}"
            txt += f"\n*Favourite*: {favourite or 'N/A'}"
            txt += f"\n*Gender*: {char_gender or 'N/A'}"
            txt += f"\n*Age*: {char_age or 'N/A'}"
            txt += f"\n\n*Description*: \n{description or 'N/A'}"

            kb = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="More Information",
                            url=site_url,
                        ),

                    ],
                    [
                        InlineKeyboardButton(
                            text="Search Again",
                            switch_inline_query_current_chat=".char ",
                        ),

                    ],
                ])

            results.append(InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=name or query,
                    description=site_url or query,
                    thumb_url=thumb_url_large or "https://telegra.ph/file/cc83a0b7102ad1d7b1cb3.jpg",
                    input_message_content=InputTextMessageContent(txt, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=False),
                    reply_markup=kb,
                )
            )
    except Exception as e:
        log.exception(e)
        kb = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Search Again",
                        switch_inline_query_current_chat=".char ",
                    ),

                ],
            ])

        results.append(

            InlineQueryResultArticle
                (
                id=str(uuid4()),
                title=f"Character {query} not found",
                thumb_url="https://telegra.ph/file/cc83a0b7102ad1d7b1cb3.jpg",
                input_message_content=InputTextMessageContent(f"Character {query} not found due to {e}"),
                reply_markup=kb
            )

        )

    update.inline_query.answer(results, cache_time=5)

