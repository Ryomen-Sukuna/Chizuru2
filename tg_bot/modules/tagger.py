import html
from tg_bot.modules.disable import DisableAbleCommandHandler
from tg_bot import dispatcher, SUDO_USERS
from tg_bot.modules.helper_funcs.extraction import extract_user
from telegram.ext import CallbackContext, CallbackQueryHandler, Filters
import tg_bot.modules.sql.tagger_sql as sql
from tg_bot.modules.helper_funcs.chat_status import user_admin
from tg_bot.modules.log_channel import loggable
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.utils.helpers import mention_html
from telegram.error import BadRequest
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigcallback


@user_admin
@kigcmd(command='tag', filters=Filters.chat_type.groups)
def tag(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return 
        else:
            return
    if sql.is_tag(message.chat_id, user_id):
        message.reply_text(
            f"[{member.user['first_name']}](tg://user?id={member.user['id']}) is already tagged in {chat_title}",
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    sql.tag(message.chat_id, user_id)
    message.reply_text(
        f"[{member.user['first_name']}](tg://user?id={member.user['id']}) accept this, if you want to add yourself into {chat_title}'s tag list! or just simply decline this.", 
        reply_markup=InlineKeyboardMarkup(
                                   [
                                      [
                                         InlineKeyboardButton(text="Accept", callback_data=f"addtag_accept={user_id}"),
                                         InlineKeyboardButton(text="Decline", callback_data=f"addtag_dicline={user_id}")  
                                      ]
                                   ]
                              ),
        parse_mode=ParseMode.MARKDOWN,
    )


@user_admin
@kigcmd(command='untag', filters=Filters.chat_type.groups)
def untag(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    args = context.args
    user = update.effective_user
    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return 
        else:
            return
    if not sql.is_tag(message.chat_id, user_id):
        message.reply_text(f"{member.user['first_name']} isn't tagged yet!")
        return
    sql.untag(message.chat_id, user_id)
    message.reply_text(
        f"{member.user['first_name']} is no longer tagged in {chat_title}.")


@kigcmd(command='tagme', filters=Filters.chat_type.groups)
def tagme(update, context): 
    chat = update.effective_chat  
    user = update.effective_user 
    message = update.effective_message
    if sql.is_tag(chat.id, user.id):
        message.reply_text(
            "You're Already Exist In {}'s Tag List!".format(chat.title)
        ) 
        return
    sql.tag(chat.id, user.id)
    message.reply_text(
        "{} has been successfully added in {}'s tag list.".format(
        mention_html(user.id, user.first_name), chat.title),
        parse_mode=ParseMode.HTML,
    )

@kigcmd(command='untagme', filters=Filters.chat_type.groups)
def untagme(update, context): 
    chat = update.effective_chat  
    user = update.effective_user 
    message = update.effective_message
    if not sql.is_tag(chat.id, user.id):
        message.reply_text(
            "You're Already Doesn't Exist In {}'s Tag List!".format(chat.title)
        ) 
        return
    sql.untag(chat.id, user.id)
    message.reply_text(
        "{} has been removed from {}'s tag list.".format(
        mention_html(user.id, user.first_name), chat.title),
        parse_mode=ParseMode.HTML,
    )


@user_admin
@kigcmd(command='tagall', filters=Filters.chat_type.groups)
def tagall(update, context):
    message = update.effective_message
    chat_title = message.chat.title
    chat = update.effective_chat
    msg = "The following users are tagged.\n\n"
    tagged_users = sql.list_tagger(message.chat_id)
    for i in tagged_users:
        member = chat.get_member(int(i.user_id))
        msg += f"{mention_html(member.user['id'], html.escape(member.user['first_name']))}, "
    if msg.endswith("tagged.\n\n"):
        message.reply_text(f"No users are tagged in {chat_title}.")
        return
    else:
        message.reply_text(msg, parse_mode=ParseMode.HTML)



@kigcmd(command='untagall', filters=Filters.chat_type.groups)
def untagall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in SUDO_USERS:
        update.effective_message.reply_text(
            "Only the chat owner can untag all users at once.")
    else:
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="Untag All",
                    callback_data="untagall_user")
            ],
            [
                InlineKeyboardButton(
                    text="Cancel", callback_data="untagall_cancel")
            ],
        ])
        update.effective_message.reply_text(
            f"Are you sure you would like to untag ALL users in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )

@kigcallback(pattern=r"addtag_.*")
def addtag_button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat  
    splitter = query.data.split('=')
    query_match = splitter[0]
    user_id = splitter[1]
    if query_match == "addtag_accept":
        if query.from_user.id == int(user_id):
            member = chat.get_member(int(user_id))
            sql.tag(chat.id, member.user.id)
            query.message.edit_text(
                "{} is accepted! to add yourself {}'s tag list.".format(
                mention_html(member.user.id, member.user.first_name), chat.title),
                parse_mode=ParseMode.HTML,
            )
            query.answer("Accepted")
        else:
            query.answer("You're not the user being added in tag list!")

    elif query_match == "addtag_dicline":
        if query.from_user.id == int(user_id):
            member = chat.get_member(int(user_id))
            query.message.edit_text(
                "{} is deslined! to add yourself {}'s tag list.".format(
                mention_html(member.user.id, member.user.first_name), chat.title),
                parse_mode=ParseMode.HTML,
            )
            query.answer("Declined")
        else:
            query.answer("You're not the user being added in tag list!")


@kigcallback(pattern=r"untagall_.*")
def untagall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "untagall_user":
        if member.status == "creator" or query.from_user.id in SUDO_USERS:
            users = []
            tagged_users = sql.tag_list(chat.id)
            for i in tagged_users:
                users.append(int(i.user_id))
            for user_id in users:
                sql.untag(chat.id, user_id)
            query.answer("OK!")
            message.edit_text(f"Successully Untagged All Users From {chat.title}!")
            return

        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")

        if member.status == "member":
            query.answer("You need to be admin to do this.")
    elif query.data == "untagll_cancel":
        if member.status == "creator" or query.from_user.id in SUDO_USERS:
            message.edit_text(
                "Removing of all tagged users has been cancelled.")
            return ""
        if member.status == "administrator":
            query.answer("Only owner of the chat can do this.")
        if member.status == "member":
            query.answer("You need to be admin to do this.")

from tg_bot.modules.language import gs

def get_help(chat):
    return gs(chat, "tagger_help")

__mod_name__ = "Tagger"
