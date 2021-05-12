
from tg_bot.modules.language import gs

from telegram.error import BadRequest
from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.modules.helper_funcs.decorators import kigcallback




def get_help_btns(name):
     buttuns = None
     if str(name) == "Fun":
            buttuns = [
                [InlineKeyboardButton(text="AFK", callback_data="subhelp_afk"),
                InlineKeyboardButton(text="Sticker", callback_data="subhelp_stick"),
                InlineKeyboardButton(text="Translation", callback_data="subhelp_tr"),],
                [InlineKeyboardButton(text="Back", callback_data="help_back"),],
            ]
     if str(name) == "Greetings":
            buttuns = [
                [InlineKeyboardButton(text="Formatting", callback_data="subhelp_wel_format"),],
                [InlineKeyboardButton(text="Back", callback_data="help_back"),],
            ]
     return buttuns


@kigcallback(pattern=r'subhelp_.*')
def subhelp_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    query = update.callback_query

    # Sub - Buttons For FUN Help
    if query.data == "subhelp_back":
        query.message.edit_text(
                text="Here is the help for the *Fun* module:\n" + gs(chat, "fun_help"),
                reply_markup=InlineKeyboardMarkup(
                        get_help_btns("Fun")
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )
    elif query.data == "subhelp_afk":
        query.message.edit_text(
                text="Here is the help for the *AFK* module:\n" + gs(chat, "afk_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_stick":
        query.message.edit_text(
                text="Here is the help for the *Stickers* module:\n" + gs(chat, "sticker_help"),
                reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="Back", callback_data="subhelp_back"),]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                timeout=60, 
            )

    elif query.data == "subhelp_tr":
        query.message.edit_text(
                text="Here is the help for the *Translation* module:\n" + gs(chat, "gtranslate_help"),
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
                text="Here is the help for the *Greetings* module:\n" + gs(chat, "greetings_help"),
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

__mod_name__ = "Helper"
