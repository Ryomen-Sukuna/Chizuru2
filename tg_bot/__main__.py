'''#TODO

Dank-del
2020-12-29
'''

import importlib
import re
import json
import random
import traceback
from typing import Optional, List
from sys import argv
import requests
from pyrogram import idle, Client
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown
from tg_bot import (
    RentalBot,
    dispatcher,
    updater,
    TOKEN,
    WEBHOOK,
    OWNER_ID,
    CERT_PATH,
    PORT,
    URL,
    log,
    ALLOW_EXCL,
    telethn,
    kp,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from tg_bot.modules import ALL_MODULES
from tg_bot.modules.helper_funcs.chat_status import is_user_admin
from tg_bot.modules.helper_funcs.misc import paginate_modules
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigcallback, kigmsg
from tg_bot.modules.helper import get_help_btns
from tg_bot.modules.language import gs

SUPPORT_CHAT = "ElitesOfSupport"
START_IMG = "https://telegra.ph/file/e5100e06c03767af80023.jpg"

buttuns = [
    [        
        InlineKeyboardButton(
              text="About", callback_data="aboutmanu_"
        ),
    ],
    [
        InlineKeyboardButton(
              text="Try Inline",
              switch_inline_query_current_chat="",
        ),
    ],
    
]



IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []

CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("tg_bot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "get_help") and imported_module.get_help:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    '''#TODO

    Params:
        chat_id  -
        text     -
        keyboard -
    '''

    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
    )

@kigcmd(command='text')
def test(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    '''

    # pprint(eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)

@kigcmd(command='start', pass_args=True)
def start(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    '''
    chat = update.effective_chat
    args = context.args
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, (gs(chat.id, "pm_help_text")))

            elif args[0].lower() in ["formatting", "formattings"]:
                IMPORTED["misc"].send_formatting(update, context)

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)


        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_text(
                    gs(chat.id, "pm_start_text").format(
                           escape_markdown(context.bot.first_name),
                           START_IMG,
                           START_IMG,
                           SUPPORT_CHAT,
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(buttuns),
            )
    else:
        update.effective_message.reply_text(gs(chat.id, "grp_start_text"))


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update  -
        context -
    '''

    try:
        raise context.error
    except Unauthorized:
        pass
        # remove update.message.chat_id from conversation list
    except BadRequest:
        pass
        # handle malformed requests - read more below!
    except TimedOut:
        pass
        # handle slow connection problems
    except NetworkError:
        pass
        # handle other connection problems
    except ChatMigrated as e:
        pass
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        pass
        # handle all other telegram related errors

@kigcallback(pattern=r'help_.*')
def help_button(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update  -
        context -
    '''

    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    chat = update.effective_chat

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "Here is the help for the *{}* module:\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].get_help(update.effective_chat.id)
            )
            try:
                x = get_help_btns(HELPABLE[module].__mod_name__)
                if x is not None:
                     markup = InlineKeyboardMarkup(x)
                else:
                     markup = InlineKeyboardMarkup(
                                    [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                              )
            except:
                markup = InlineKeyboardMarkup(
                               [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                         )
            query.message.edit_text(
                text=text,
                reply_markup=markup,
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=gs(chat.id, "pm_help_text"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=gs(chat.id, "pm_help_text"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=gs(chat.id, "pm_help_text"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


@kigcallback(pattern=r'aboutmanu_.*')
def about_callback(update: Update, context: CallbackContext):
    chat = update.effective_chat
    query = update.callback_query
    if query.data == "aboutmanu_":
        query.message.edit_text(
            text=f"*Hey There! My Name Is {dispatcher.bot.first_name}. \n\nI Am An Anime Themed Group Management Bot.* \n_Build By Weebs For Weebs_"
                 f"\n\nI Specialize In Managing Anime And Similar Themed Groups With Additional Features."
                 f"\n\nIf Any Question About {dispatcher.bot.first_name}, Simply [Click Here](https://telegra.ph/Chizuru---Guides-11-27)", 
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                  [
                    InlineKeyboardButton(text="How To Use", callback_data="aboutmanu_howto"),
                    InlineKeyboardButton(text="T & C", callback_data="aboutmanu_tac")
                  ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="aboutmanu_back")
                 ]
                ]
            ),
        )
        query.answer("About Menu")

    elif query.data == "aboutmanu_back":
        query.message.edit_text(
                gs(chat.id, "pm_start_text").format(
                     escape_markdown(context.bot.first_name),
                     START_IMG,
                     START_IMG,
                     SUPPORT_CHAT,
                ),
                reply_markup=InlineKeyboardMarkup(buttuns),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60, 
            )
        query.answer("Welcome Back!")
        
    elif query.data == "aboutmanu_howto":
        query.message.edit_text(
            text="*Basic Help:*"
                f"\nTo Add {dispatcher.bot.first_name} To Your Chats, Simply [Click Here](http://t.me/{dispatcher.bot.username}?startgroup=true) And Select Chat. \n", 
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Admins Settings", callback_data="aboutmanu_permis"),
                InlineKeyboardButton(text="Anti-Spam", callback_data="aboutmanu_spamprot")],
                [InlineKeyboardButton(text="Back", callback_data="aboutmanu_")]
            ]),
        )
        query.answer("How To Use")

    elif query.data == "aboutmanu_credit":
        query.message.edit_text(
            text=f"*{dispatcher.bot.first_name} Is A Powerful Bot For Managing Groups With Additional Features.*"
                 f"\n\nFork Of [Marie](https://github.com/PaulSonOfLars/tgbot)."
                 f"\n\n{dispatcher.bot.first_name}'s Licensed Under The GNU _(General Public License v3.0)_"
                 f"\n\nHere Is The [Source Code](t.me/{SUPPORT_CHAT})."
                 f"\n\nIf Any Suggestions About {dispatcher.bot.first_name}, \nLet Us Know At @{SUPPORT_CHAT}.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data="aboutmanu_tac")]]),
        )
        query.answer("Credits")

    elif query.data == "aboutmanu_permis":
        query.message.edit_text(
            text="<b>Admin Permissions:</b>"
                f"\nTo avoid slowing down, {dispatcher.bot.first_name} caches admin rights for each user. This cache lasts about 10 minutes; this may change in the future. This means that if you promote a user manually (without using the /promote command), {dispatcher.bot.first_name} will only find out ~10 minutes later."
                 "\n\nIf you are getting a message saying:"
                 "\n<Code>You must be this chat administrator to perform this action!</code>"
                f"\nThis has nothing to do with {dispatcher.bot.first_name}'s rights; this is all about YOUR permissions as an admin. {dispatcher.bot.first_name} respects admin permissions; if you do not have the Ban Users permission as a telegram admin, you won't be able to ban users with {dispatcher.bot.first_name}. Similarly, to change {dispatcher.bot.first_name} settings, you need to have the Change group info permission."
                f"\n\nThe message very clearly says that you need these rights - <i>not {dispatcher.bot.first_name}.</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data="aboutmanu_howto")]]),
        )
        query.answer("Admin Permissions")

    elif query.data == "aboutmanu_spamprot":
        query.message.edit_text(
            text=gs(chat.id, "antispam_help"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="NPL", callback_data="aboutmanu_spamprotcf")],
                [InlineKeyboardButton(text="Back", callback_data="aboutmanu_howto")]
            ]), 
        )
        query.answer("Antispam")

    elif query.data == "aboutmanu_spamprotcf":
        query.message.edit_text(
            text=gs(chat.id, "nlp_help"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Back", callback_data="aboutmanu_spamprot")]
            ]), 
        )
        query.answer("Chatroom Spam Prediction")

    elif query.data == "aboutmanu_tac":
        query.message.edit_text(
            text="<b>Terms and Conditions:</b>\n"
                 "\n<i>To Use This Bot, You Need To Read Terms and Conditions</i>\n"
                 "\n∘ Watch your group, if someone \n  spamming your group, you can \n  use report feature from your \n  Telegram Client."
                 "\n∘ Make sure antiflood is enabled, so \n  nobody can ruin your group."
                 "\n∘ Do not spam commands, buttons, \n  or anything in bot PM, else you will \n  be Gbanned."
                f"\n∘ If you need to ask anything about \n  this bot, Go @{SUPPORT_CHAT}."
                 "\n∘ If you asking nonsense in Support \n  Chat, you will get banned."
                 "\n∘ Sharing any files/videos others \n  than about bot in Support Chat is \n  prohibited."
                 "\n∘ Sharing NSFW in Support Chat,\n  will reward you banned/gbanned \n  and reported to Telegram as well."
                 "\n\n<i>T & C will be changed anytime</i>\n",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                      InlineKeyboardButton(text="Credits", callback_data="aboutmanu_credit"),
                      InlineKeyboardButton(text="Back", callback_data="aboutmanu_")
                    ] 
                ]
            )
        )
        query.answer("Terms & Conditions")


@kigcmd(command='help')
def get_help(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update  -
        context -
    '''

    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:

        update.effective_message.reply_text(
            "Contact me in PM for help!",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].get_help
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            ),
        )

    elif len(args) >= 2 and args[1].lower() in ["formatting", "formattings"]:
          IMPORTED["misc"].formatting(update, context)

    else:
        send_help(chat.id, (gs(chat.id, "pm_help_text")))


def send_settings(chat_id, user_id, user=False):
    '''#TODO

    Params:
        chat_id -
        user_id -
        user    -
    '''

    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )

@kigcallback(pattern=r"stngs_")
def settings_button(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    '''

    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            log.exception("Exception in settings buttons. %s", str(query.data))

@kigcmd(command='settings')
def get_settings(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    '''

    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Settings",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)

@kigmsg((Filters.status_update.migrate))
def migrate_chats(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    '''

    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    log.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    log.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():
    dispatcher.add_error_handler(error_callback)
    # dispatcher.add_error_handler(error_handler)

    if WEBHOOK:
        log.info("Using webhooks.")
        updater.start_webhook(listen="127.0.0.1", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        log.info(f"Using long polling. | BOT: [@{dispatcher.bot.username}]")
        RentalBot.bot_id = dispatcher.bot.id
        RentalBot.bot_username = dispatcher.bot.username
        RentalBot.bot_name = dispatcher.bot.first_name
        updater.start_polling(timeout=15, read_latency=4, drop_pending_updates=True)
    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()
    updater.idle()

if __name__ == "__main__":
    kp.start()
    log.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    main()
    idle()
