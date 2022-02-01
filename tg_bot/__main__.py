import re
import importlib
from sys import argv

from telegram.ext import Filters, CallbackContext
from telegram.utils.helpers import escape_markdown
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError

from tg_bot import SUPPORT_CHAT, TOKEN, dispatcher, updater, telethn, log

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from tg_bot.modules import ALL_MODULES
from tg_bot.modules.language import gs
from tg_bot.modules.helper_funcs.misc import paginate_modules
from tg_bot.modules.helper_funcs.chat_status import is_user_admin
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigcallback, kigmsg

START_IMG = "https://telegra.ph/file/70139da07d839b2d2c057.jpg"
buttuns = [
   [
      InlineKeyboardButton(text="About", callback_data="aboutmanu_"),
   ],
   [
      InlineKeyboardButton(text="Try Inline", switch_inline_query_current_chat=""),
   ],
]



IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
DATA_IMPORT = []
DATA_EXPORT = []

CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("tg_bot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
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

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
    )

def get_help_btns(name):
     buttuns = None

     if str(name) == "Admin":
            buttuns = [
                [InlineKeyboardButton(text="Bans", callback_data="subhelp_ban"),
                InlineKeyboardButton(text="Mute", callback_data="subhelp_mute")],
                [InlineKeyboardButton(text="Pin", callback_data="subhelp_pin"),
                InlineKeyboardButton(text="Warns", callback_data="subhelp_warn")],
                [InlineKeyboardButton(text="Back", callback_data="help_back")],
            ]

     elif str(name) == "Fun":
            buttuns = [
                [InlineKeyboardButton(text="AFK", callback_data="subhelp_afk"),
                InlineKeyboardButton(text="Anime", callback_data="subhelp_anime"),
                InlineKeyboardButton(text="Drama", callback_data="subhelp_drama")],
                [InlineKeyboardButton(text="Sticker", callback_data="subhelp_stick"),
                InlineKeyboardButton(text="Translation", callback_data="subhelp_tr")],
                [InlineKeyboardButton(text="Back", callback_data="help_back")],
            ]

     elif str(name) == "Greetings":
            buttuns = [
                [InlineKeyboardButton(text="Formatting", callback_data="subhelp_wel_format")],
                [InlineKeyboardButton(text="Back", callback_data="help_back")],
            ]

     return buttuns


@kigcmd(command='start', pass_args=True)
def start(update: Update, context: CallbackContext):
    chat = update.effective_chat
    args = context.args
    if update.effective_chat.type == "private":
        if args and len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, (gs(chat.id, "pm_help_text")))

            elif args[0].lower() == "formatting":
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

            elif any(args[0].lower() == x for x in HELPABLE):
                module = args[1].lower()
                text = "Here is the help for the *{}* module:\n".format(HELPABLE[module].__mod_name__) + HELPABLE[module].get_help(chat.id)
                send_help(
                     chat.id,
                     text,
                     InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data="help_back")]]),
                )


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
    try:
        raise context.error
    except (Unauthorized, BadRequest):
        pass
        # remove update.message.chat_id from conversation list
    except TimedOut:
        pass
        # handle slow connection problems
    except NetworkError:
        pass
        # handle other connection problems
    except ChatMigrated:
        pass
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        pass
        # handle all other telegram related errors


@kigcallback(pattern=r'help_.*')
def help_button(update: Update, context: CallbackContext):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    chat = update.effective_chat

    try:
        if mod_match:
            module = mod_match.group(1)
            text = "Here is the help for the *{}* module:\n".format(HELPABLE[module].__mod_name__) + HELPABLE[module].get_help(chat.id)
            x = get_help_btns(HELPABLE[module].__mod_name__)
            if x is None:
                x = [[InlineKeyboardButton(text="Back", callback_data="help_back")]]

            query.message.edit_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(x),
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
                  ],
                 [
                    InlineKeyboardButton(text="Commands", callback_data="help_back"),
                 ],
                 [
                    InlineKeyboardButton(text="Back", callback_data="aboutmanu_back"),
                 ],
                ]
            ),
        )

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

    elif query.data == "aboutmanu_spamprot":
        query.message.edit_text(
            text=gs(chat.id, "antispam_help"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data="aboutmanu_howto")]]),
        )

    context.bot.answer_callback_query(query.id)

@kigcallback(pattern=r'subhelp_.*')
def subhelp_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    query = update.callback_query

    # Sub - Buttons For ADMIN Help
    if query.data == "subhelp_back3":
        query.message.edit_text(
                text=gs(chat, "admin_help"),
                reply_markup=InlineKeyboardMarkup(
                        get_help_btns("Admin")
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )
    elif query.data == "subhelp_ban":
        query.message.edit_text(
                text=gs(chat, "bans_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back3"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_mute":
        query.message.edit_text(
                text=gs(chat, "muting_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back3"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_pin":
        query.message.edit_text(
                text=gs(chat, "pin_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back3"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_warn":
        query.message.edit_text(
                text=gs(chat, "warns_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back3"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    # Sub - Buttons For FUN Help
    if query.data == "subhelp_back":
        query.message.edit_text(
                text=gs(chat, "fun_help"),
                reply_markup=InlineKeyboardMarkup(
                        get_help_btns("Fun")
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )
    elif query.data == "subhelp_afk":
        query.message.edit_text(
                text=gs(chat, "afk_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_anime":
        query.message.edit_text(
                text=gs(chat, "anilist_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_drama":
        query.message.edit_text(
                text=gs(chat, "drama_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_stick":
        query.message.edit_text(
                text=gs(chat, "sticker_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_tr":
        query.message.edit_text(
                text=gs(chat, "gtranslate_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    # Sub - Buttons For GREETINGS Help
    elif query.data == "subhelp_back2":
        query.message.edit_text(
                text=gs(chat, "greetings_help"),
                reply_markup=InlineKeyboardMarkup(
                        get_help_btns("Greetings")
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )
    elif query.data == "subhelp_wel_format":
        query.message.edit_text(
                text=gs(chat, "greetings_format_help").format(context.bot.first_name),
                reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="Markdown", callback_data="subhelp_wel_markdown"),
                        InlineKeyboardButton(text="Fillings", callback_data="subhelp_wel_fillings"),],
                        [InlineKeyboardButton(text="Random Content", callback_data="subhelp_wel_random"),],
                        [InlineKeyboardButton(text="Back", callback_data="subhelp_back2"),],
                ]),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )
    elif query.data == "subhelp_wel_markdown":
        query.message.edit_text(
                text=gs(chat, "markdown_help_text"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_wel_format"),]]
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                timeout=60, 
            )
    elif query.data == "subhelp_wel_fillings":
        query.message.edit_text(
                text=gs(chat, "greetings_filling_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_wel_format"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )
    elif query.data == "subhelp_wel_random":
        query.message.edit_text(
                text=gs(chat, "greetings_random_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_wel_format"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    context.bot.answer_callback_query(query.id)


@kigcmd(command='help')
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(" " or None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:

        update.effective_message.reply_text(
            "Contact me in PM for help!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Help", url="t.me/{}?start=help".format(context.bot.username))]]),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = "Here is the help for the *{}* module:\n".format(HELPABLE[module].__mod_name__) + HELPABLE[module].get_help(chat.id)
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
            ),
        )

    elif len(args) >= 5 and args[1].lower() == "formatting":
          IMPORTED["misc"].formatting(update, context)

    else:
        send_help(chat.id, (gs(chat.id, "pm_help_text")))


def send_settings(chat_id, user_id, user=False):
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

    elif CHAT_SETTINGS:
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
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Back", callback_data="stngs_back({})".format(chat_id))]]),
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
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            log.exception("Exception in settings buttons. %s", str(query.data))


@kigcmd(command='settings')
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type == chat.PRIVATE:
        send_settings(chat.id, user.id, True)

    elif is_user_admin(chat, user.id):
        text = "Click here to get this chat's settings, as well as yours."
        msg.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Settings", url="t.me/{}?start=stngs_{}".format(context.bot.username, chat.id))]]),
        )
    else:
        text = "Click here to check your settings."


@kigmsg((Filters.status_update.migrate))
def migrate_chats(update: Update, context: CallbackContext):
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

    log.info(f"Using long polling. | BOT: [@{dispatcher.bot.username}]")
    updater.start_polling(timeout=15, read_latency=2.0, allowed_updates=Update.ALL_TYPES)
    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()
    updater.idle()

if __name__ == "__main__":
    log.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    main()
