import re
import html
import json
import random
import time
import urllib.request
import urllib.parse
import requests

from telegram import ParseMode, Update, ChatAction, ChatPermissions
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, CallbackContext
from telegram.error import BadRequest

from tg_bot.modules.helper_funcs.decorators import kigcmd, kigmsg, kigcallback
from tg_bot.modules.helper_funcs.chat_status import is_user_admin
from tg_bot.modules.helper_funcs.extraction import extract_user
import tg_bot.modules.fun_strings as fun


# truth / dare
@kigcmd(command="truth")
def truth(update, context):
     xyz = requests.get("https://elianaapi.herokuapp.com/games/truth")
     update.effective_message.reply_text(xyz)

@kigcmd(command="dare")
def dare(update, context):
     xyz = requests.get("https://elianaapi.herokuapp.com/games/dares").json()
     dare = xyz.get("dare")
     update.effective_message.reply_text(dare)


@kigcmd(command='runs')
def runs(update, context):
    update.effective_message.reply_text(random.choice(fun.RUN_STRINGS))

@kigcmd(command='slap')
def slap(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    chat = update.effective_chat

    reply_text = (
        message.reply_to_message.reply_text
        if message.reply_to_message
        else message.reply_text
    )

    curr_user = html.escape(message.from_user.first_name)
    user_id = extract_user(message, args)

    if user_id == bot.id:
        temp = random.choice(fun.SLAP_BOT_TEMPLATES)

        if isinstance(temp, list):
            if temp[2] == "tmute":
                if is_user_admin(chat, message.from_user.id):
                    reply_text(temp[1])
                    return

                mutetime = int(time.time() + 60)
                bot.restrict_chat_member(
                    chat.id,
                    message.from_user.id,
                    until_date=mutetime,
                    permissions=ChatPermissions(can_send_messages=False),
                )
            reply_text(temp[0])
        else:
            reply_text(temp)
        return

    if user_id:

        slapped_user = bot.get_chat(user_id)
        user1 = curr_user
        user2 = html.escape(slapped_user.first_name)

    else:
        user1 = bot.first_name
        user2 = curr_user

    temp = random.choice(fun.SLAP_TEMPLATES)
    item = random.choice(fun.ITEMS)
    hit = random.choice(fun.HIT)
    throw = random.choice(fun.THROW)
    reply = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    reply_text(reply, parse_mode=ParseMode.HTML)

@kigcmd(command='pat')
def pat(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = str(update.message.text)
    try:
        msg = msg.split(" ", 1)[1]
    except IndexError:
        msg = ""
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )
    pat_type = random.choice(("Photo", "Gif"))
    if pat_type == "Photo":
        pats = []
        pats = json.loads(
            urllib.request.urlopen(
                urllib.request.Request(
                    "http://headp.at/js/pats.json",
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; U; Linux i686) "
                        "Gecko/20071127 Firefox/2.0.0.11"
                    },
                )
            )
            .read()
            .decode("utf-8")
        )
        try:
            context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.UPLOAD_PHOTO)
            if "@" in msg and len(msg) > 5:
                context.bot.send_photo(
                    chat_id,
                    f"https://headp.at/pats/{urllib.parse.quote(random.choice(pats))}",
                    caption=msg,
                )
            else:
                context.bot.send_photo(
                    chat_id,
                    f"https://headp.at/pats/{urllib.parse.quote(random.choice(pats))}",
                    reply_to_message_id=msg_id,
                )
        except BadRequest:
            return
    if pat_type == "Gif":
        try:
            context.bot.send_chat_action(update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
            pat = requests.get('https://some-random-api.ml/animu/pat').json()
            if "@" in msg and len(msg) > 5:
                context.bot.send_animation(
                    chat_id,
                    pat['link'],
                    caption=msg,
                )
            else:
                context.bot.send_animation(
                    chat_id,
                    pat['link'],
                    reply_to_message_id=msg_id,
                )
        except BadRequest:
            return

@kigcmd(command='hug')
def hug(update: Update, context: CallbackContext):
    reply_animation = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    hug = requests.get('https://some-random-api.ml/animu/hug').json()
    reply_animation(hug['link'])

@kigcmd(command='toss')
def toss(update, context):
    update.message.reply_text(random.choice(fun.TOSS))

@kigcmd(command='decide')
def yesnowtf(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    res = requests.get("https://yesno.wtf/api")
    if res.status_code != 200:
         msg.reply_text(random.choice(fun.DECIDE))
         return
    else:
        res = res.json()
    try:
        context.bot.send_animation(
            chat.id, animation=res["image"], caption=str(res["answer"]).upper()
        )
    except BadRequest:
        return

@kigmsg(Filters.regex(r"(?i)^Chizuru\?"), friendly="decide")
def decide(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun.DECIDE))


@kigcmd(command='rmeme')
def rmemes(update, context):
    message = update.effective_message
    chat = update.effective_chat

    SUBREDS = [
        "AnimeFunny", "dankmemes", "MangaMemes",
        "AdviceAnimals", "animememes", "memes",
        "meme", "memes_of_the_dank", "TikTokCringe",
        "HindiMemes", "Animemes", "teenagers", "funny",
        "memesIRL", "funnytweets", "animenocontext",
        "insanepeoplefacebook", "terriblefacebookmemes",
        "wholesomeanimemes", "anime_irl", "KizunaA_Irl"
    ]

    subreddit = random.choice(SUBREDS)
    res = requests.get(f"https://meme-api.herokuapp.com/gimme/{subreddit}")

    if res.status_code != 200:  # Like if api is down?
        message.reply_text("Failed To Get Meme! Maybe API Is Down!")
        return
    else:
        res = res.json()

    rpage = res.get(str("subreddit"))  # Subreddit
    title = res.get(str("title"))  # Post title
    memeu = res.get(str("url"))  # meme pic url
    plink = res.get(str("postLink"))

    caps = f"- <b>Title</b>: {title}\n"
    caps += f"- <b>Subreddit:</b> <pre>r/{rpage}</pre>"

    keyb = [[InlineKeyboardButton(text="Reddit link 🔗", url=plink)]]
    try:
        context.bot.send_photo(
             chat.id,
             photo=memeu,
             caption=(caps),
             reply_markup=InlineKeyboardMarkup(keyb),
             parse_mode=ParseMode.HTML,
             timeout=60,
        )
    except BadRequest as excp:
        message.reply_text(
            f"Failed To Send Meme! \n\n<code>{excp.message}</code>",
            parse_mode=ParseMode.HTML,
            timeout=60,
        )


# Superhero Quote
@kigcmd(command='squote')
def squote(update: Update, context: CallbackContext):
    try:
        animu = requests.get('https://superhero-quotes.herokuapp.com/random').json()
        if animu['StatusCode'] == 200:
           banner = "DCU" if animu['Banner'] == "DC Universe (DCU)" else "MCU"
           update.effective_message.reply_text(f'❝ <em>{animu["Stuff"]["data"]["quote"]}</em> ❞'
                      f'\n\n- <b>{animu["Stuff"]["data"]["author"]}</b> || ( <b>{banner}</b> )',
                       parse_mode=ParseMode.HTML,
                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Change", callback_data="squote_change")]]),
           )
    except:
        pass

@kigcallback(pattern=r"squote_.*")
def squote_button(update: Update, context: CallbackContext):
    query = update.callback_query
    change = re.match(r"squote_change", query.data)

    try:
        if change:
            animu = requests.get('https://superhero-quotes.herokuapp.com/random').json()
            if animu["StatusCode"] == 200:
                banner = "DCU" if animu["Banner"] == "DC Universe (DCU)" else "MCU"
                query.message.edit_text(
                        f"❝ <em>{animu['Stuff']['data']['quote']}</em> ❞"
                        f"\n\n- <b>{animu['Stuff']['data']['author']}</b> || ( <b>{banner}</b> )",
                        parse_mode=ParseMode.HTML,
                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Change", callback_data="squote_change")]]),
                )
            else:
                query.answer("API Is Down! Try Again!")

        context.bot.answer_callback_query(query.id)

    except BadRequest:
        pass



def get_help(chat):
    from tg_bot.modules.language import gs
    return gs(chat, "fun_help")

__mod_name__ = "Fun"
