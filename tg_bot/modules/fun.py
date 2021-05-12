import re
import html
import json
import random
import time
import urllib.request
import urllib.parse
import requests
from telegram import ParseMode, Update, ChatPermissions
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.error import BadRequest

import tg_bot.modules.fun_strings as fun
from tg_bot import dispatcher
from tg_bot.modules.helper_funcs.chat_status import is_user_admin
from tg_bot.modules.helper_funcs.extraction import extract_user
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigmsg, kigcallback


# truth / dare
@kigcmd(command="truth")
def truth(update: Update, context: CallbackContext):
    try:
       try:
          xyz = requests.get("https://elianaapi.herokuapp.com/games/truth").json()
          truth = xyz.get("truth")
          update.effective_message.reply_text(truth)
       except:
           update.effective_message.reply_text(random.choice(fun.TRUTH))
    except:
        pass

@kigcmd(command="dare")
def dare(update: Update, context: CallbackContext):
    try:
       try:
          xyz = requests.get("https://elianaapi.herokuapp.com/games/dares").json()
          truth = xyz.get("dare")
          update.effective_message.reply_text(truth)
       except:
           update.effective_message.reply_text(random.choice(fun.DARE))
    except:
        pass



@kigcmd(command='runs')
def runs(update: Update, context: CallbackContext):
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


@kigcmd(command='hug')
def hug(update: Update, context: CallbackContext):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]

    # reply to correct message
    reply_to = msg.reply_to_message if msg.reply_to_message else msg

    # get user who sent message
    if msg.from_user.username:
        curr_user = "@" + escape_markdown(msg.from_user.username)
    else:
        curr_user = "[{}](tg://user?id={})".format(
            msg.from_user.first_name, msg.from_user.id
        )

    user_id = extract_user(update.effective_message, args)
    if user_id:
        hugged_user = context.bot.get_chat(user_id)
        user1 = curr_user
        if hugged_user.username:
            user2 = "@" + escape_markdown(hugged_user.username)
        else:
            user2 = "[{}](tg://user?id={})".format(
                hugged_user.first_name, hugged_user.id
            )

    # if no target found, bot targets the sender
    else:
        user1 = "Uwvv! [{}](tg://user?id={})".format(
            context.bot.first_name, context.bot.id
        )
        user2 = curr_user

    temp = random.choice(fun.HUG_TEMPLATES)
    hug = random.choice(fun.HUG)
    hugg = temp.format(user1=user1, user2=user2, hug=hug)
    try:
        hug_animu = requests.get('https://some-random-api.ml/animu/hug').json()
        reply_to.reply_animation(hug_animu['link'], caption=hugg, parse_mode=ParseMode.MARKDOWN)
    except:
        reply_to.reply_text(hugg, parse_mode=ParseMode.MARKDOWN)


@kigcmd(command='roll')
def roll(update: Update, context: CallbackContext):
    update.message.reply_text(random.choice(range(1, 7)))

@kigcmd(command='toss')
def toss(update: Update, context: CallbackContext):
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

@kigcmd(command='table')
def table(update: Update, context: CallbackContext):
    reply_text = (
        update.effective_message.reply_to_message.reply_text
        if update.effective_message.reply_to_message
        else update.effective_message.reply_text
    )
    reply_text(random.choice(fun.TABLE))


# Superhero Quote 
SQUOTES = InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="Change", callback_data="squote_change"),
                  ],
                ]
          )
@kigcmd(command='squote')
def squote(update: Update, context: CallbackContext):
    try:
        animu = requests.get('https://superhero-quotes.herokuapp.com/random').json()
        if animu['StatusCode'] == 200:
           banner = "DCU" if animu['Banner'] == "DC Universe (DCU)" else "MCU"
           update.effective_message.reply_text(f'❝ <em>{animu["Stuff"]["data"]["quote"]}</em> ❞'
                      f'\n\n- <b>{animu["Stuff"]["data"]["author"]}</b> || ( <b>{banner}</b> )',
                       parse_mode=ParseMode.HTML,
                       reply_markup=SQUOTES,
           )
    except:
        pass

@kigcallback(pattern=r"squote_.*")
def squote_button(update, context):
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
                        reply_markup=SQUOTES,
                )
            else:
                query.answer("API Is Down! Try Again!")

        context.bot.answer_callback_query(query.id)

    except BadRequest:
        pass


__mod_name__ = "Fun"

def get_help(chat):
    from tg_bot.modules.language import gs
    return gs(chat, "fun_help")
