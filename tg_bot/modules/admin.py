import os
import html

from telegram import ParseMode, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters
from telegram.utils.helpers import mention_html, mention_markdown

from tg_bot import SUDO_USERS, dispatcher
from tg_bot.modules.helper_funcs.chat_status import (
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
    ADMIN_CACHE,
)

from tg_bot.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from tg_bot.modules.log_channel import loggable
from tg_bot.modules.helper_funcs.alternate import send_message
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigcallback
from tg_bot.modules.helper_funcs.admin_rights import user_can_changeinfo
 

@kigcmd(command="fullpromote", pass_args=True)
@connection_status
@bot_admin
@can_promote
@user_admin
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and not user.id in SUDO_USERS
    ):
        message.reply_text("You don't have the necessary rights to do that!")
        return

    user_id, title = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_id == bot.id:
        message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("How am I meant to promote someone that's already an admin?")
        return

    if len(title) > 16:
        message.reply_text("Admin titles can only be 0-16 characters long, and cannot contain emoji.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)
    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("I can't promote someone who isn't in the group.")
        else:
            message.reply_text("An error occured while promoting.")
        return

    if title:
        try:
            bot.set_chat_administrator_custom_title(chat.id, user_id, title)
        except BadRequest:
            message.reply_text("Admin titles can only be 0-16 characters long, and cannot contain emoji.")

    bot.sendMessage(
        chat.id,
        f"<b>{mention_html(user_id, user_member.user.first_name or user_id)}</b> was promoted with all rights by <b>{mention_html(message.from_user.id, message.from_user.first_name or message.from_user.id)}</b> in <b>{chat.title}</b>!",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Demote", callback_data=f"admim-demote {user_id}")]]),
    )


@kigcmd(command="promote", pass_args=True, can_disable=False)
@connection_status
@bot_admin
@can_promote
@user_admin
def promote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    promoter = chat.get_member(user.id)

    if (
        not (promoter.can_promote_members or promoter.status == "creator")
        and not user.id in SUDO_USERS
    ):
        message.reply_text("You don't have the necessary rights to do that!")
        return

    user_id, title = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_member.status in ("administrator", "creator"):
        message.reply_text("How am I meant to promote someone that's already an admin?")
        return

    if user_id == bot.id:
        message.reply_text("I can't promote myself! Get an admin to do it for me.")
        return

    if len(title) > 16:
        message.reply_text("Admin titles can only be 0-16 characters long, and cannot contain emoji.")
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            # can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            # can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
    except BadRequest as err:
        if err.message == "User_not_mutual_contact":
            message.reply_text("I can't promote someone who isn't in the group.")
        else:
            message.reply_text("An error occured while promoting.")
        return

    if title:
        try:
            bot.set_chat_administrator_custom_title(chat.id, user_id, title)
        except BadRequest:
            message.reply_text("Admin titles can only be 0-16 characters long, and cannot contain emoji.")

    bot.sendMessage(
        chat.id,
        f"<b>{mention_html(user_id, user_member.user.first_name or user_id)}</b> was promoted by <b>{mention_html(message.from_user.id, message.from_user.first_name or message.from_user.id)}</b> in <b>{chat.title}</b>!",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Demote", callback_data=f"admim-demote {user_id}")]]),
    )


@kigcmd(command="demote", can_disable=False)
@connection_status
@bot_admin
@can_promote
@user_admin
def demote(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if user_id == bot.id:
        message.reply_text("I can't demote myself! Get an admin to do it for me.")
        return

    if user_member.status == "creator":
        message.reply_text("This person CREATED the chat, how would I demote them?")
        return

    if user_member.status != "administrator":
        message.reply_text("Can't demote what wasn't promoted!")
        return

    try:
        bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )

        bot.sendMessage(
            chat.id,
            f"<b>{mention_html(user_id, user_member.user.first_name or user_id)}</b> was demoted by <b>{mention_html(message.from_user.id, message.from_user.first_name or message.from_user.id)}</b> in <b>{chat.title}</b>!",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Demote", callback_data=f"admim-demote {user_id}")]]),
        )

    except BadRequest:
        message.reply_text(
            "Could not demote. I might not be admin, or the admin status was appointed by another"
            " user, so I can't act upon them!"
        )
        return


@kigcmd(command=["admincache", "reload"], can_disable=False)
@user_admin
def refresh_admin(update: Update, _):
    ADMIN_CACHE.pop(update.effective_chat.id)
    update.effective_message.reply_text("Admins cache refreshed!")


@kigcmd(command="title", can_disable=False)
@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect.."
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "This person CREATED the chat, how can i set custom title for him?"
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "Can't set title for non-admins!\nPromote them first to set custom title!"
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "I can't set my own title myself! Get the one who made me admin to do it for me."
        )
        return

    if not title:
        message.reply_text("Setting blank title doesn't do anything!")
        return

    if len(title) > 16:
        message.reply_text(
            "The title length is longer than 16 characters.\nTruncating it to 16 characters."
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text("I can't set custom title for admins that I didn't promote!")
        return

    bot.sendMessage(
        chat.id,
        f"Sucessfully set title for <code>{user_member.user.first_name or user_id}</code> "
        f"to <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )


@kigcmd(command="pin", can_disable=False)
@bot_admin
@can_pin
@user_admin
def pin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    args = context.args

    user = update.effective_user
    chat = update.effective_chat

    is_group = chat.type != "private" and chat.type != "channel"
    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise


@kigcmd(command="unpin", can_disable=False)
@bot_admin
@can_pin
@user_admin
def unpin(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise


@kigcmd(command="invitelink")
@bot_admin
@user_admin
@connection_status
def invite(update: Update, context: CallbackContext):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type == chat.SUPERGROUP or chat.type == chat.CHANNEL:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = bot.exportChatInviteLink(chat.id)
            update.effective_message.reply_text(invitelink)
        else:
            update.effective_message.reply_text(
                "I don't have access to the invite link, try changing my permissions!"
            )
    else:
        update.effective_message.reply_text(
            "I can only give you invite links for supergroups and channels, sorry!"
        )


@kigcmd(command="setgtitle")
@bot_admin
@user_admin
def chattitle(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    bot, args = context.bot, context.args

    if user_can_changeinfo(chat, user) is False:
        message.reply_text("You don't have the necessary rights to change group info!")
        return

    title = " ".join(args)
    if not title:
        message.reply_text("Setting blank title doesn't do anything!")
        return

    try:
        bot.set_chat_title(int(chat.id), str(title))
        message.reply_text(
            f"Successfully set <b>{title}</b> as new chat title!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        message.reply_text(f"Error! {excp.message}.")
        return


@kigcmd(command="delgpic")
@bot_admin
@user_admin
def delchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if user_can_changeinfo(chat, user) is False:
        message.reply_text("You don't have the necessary rights to change group info!")
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        message.reply_text("Successfully deleted chat's profile photo!")
    except BadRequest as excp:
        message.reply_text(f"Error! {excp.message}.")
        return


@kigcmd(command="setgpic")
@bot_admin
@user_admin
def chatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if user_can_changeinfo(chat, user) is False:
        message.reply_text("You don't have the necessary rights to change group info!")
        return

    if message.reply_to_message:
        if message.reply_to_message.photo:
            pic_id = message.reply_to_message.photo[-1].file_id
        elif message.reply_to_message.document:
            pic_id = message.reply_to_message.document.file_id
        else:
            message.reply_text("You can only set some photo as chat pic!")
            return
        dlmsg = message.reply_text("Just a sec...")
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                message.reply_text("Successfully set new chatpic!")
        except BadRequest as excp:
            message.reply_text(f"Error! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        message.reply_text("Reply to some photo or file to set new chat pic!")


@kigcmd(command="setsticker")
@bot_admin
@user_admin
def gstickerset(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if user_can_changeinfo(chat, user) is False:
        message.reply_text("You don't have the necessary rights to change group info!")
        return

    if message.reply_to_message:
        if not message.reply_to_message.sticker:
            message.reply_text("You need to reply to some sticker to set chat sticker set!")
            return

        stickers = message.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stickers)
            message.reply_text(f"Successfully set new group stickers in {chat.title}!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                message.reply_text("Sorry, due to telegram restrictions chat needs to have minimum 100 members before they can have group stickers!")
                return

            message.reply_text(f"Error! {excp.message}.")

    else:
        message.reply_text("You need to reply to some sticker to set chat sticker set!")


@kigcmd(command=["setdescription", "setdesc"])
@bot_admin
@user_admin
def set_desc(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if user_can_changeinfo(chat, user) is False:
        message.reply_text("You don't have the necessary rights to change group info!")
        return

    tesc = message.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        message.reply_text("Setting blank description doesn't do anything!")
        return
    try:
        if len(desc) > 255:
            message.reply_text("Description must needs to be under 255 characters!")
            return
        context.bot.set_chat_description(chat.id, desc)
        message.reply_text(f"Successfully updated chat description in {chat.title}!")
    except BadRequest as excp:
        message.reply_text(f"Error! {excp.message}.")



@kigcmd(command=["admins"])
def adminlist(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    bot = context.bot

    if chat.type == "private":
        send_message(update.effective_message, "This Command Only Works In Groups.")
        return

    admim = update.effective_message.reply_text("Just A Second...")
    administrators = bot.getChatAdministrators(chat.id)
    text = "Admins In *{}*:".format(chat.title)


    admins_list = []
    for admin in administrators:
        user = admin.user
        status = admin.status
        custom_title = admin.custom_title

        if user.first_name == '':
            name = "💀"
        else:
            name = "{}".format(mention_markdown(user.id, escape_markdown(custom_title if custom_title else user.first_name)))

        if status == "creator":
            text += "\n 👑 Creator :"
            text += "\n` • `{}\n".format(name)

        text += "\n🔱 Admins :"
        if status == "administrator":
            admins_list.append(name)
            for admin in admins_list:
               text += "\n` ∘ `{}".format(admin)

    try:
        admim.edit_text(text, parse_mode=ParseMode.MARKDOWN)
    except BadRequest:  # if original message is deleted
        return


# Callback Data For Promote / Demote
@kigcallback(pattern=r"admim-.*")
def admim_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    query = update.callback_query
    message = update.effective_message

    # Split query_match & user_id 
    splitter = query.data.split(" ")
    query_match = splitter[0]
    user_id = splitter[1]

    if query_match == "admim-promote":
        member = chat.get_member(int(user_id))
        if member.status == "creator":
           query.answer("This Person Is A Chat Creator! How am I meant to promote him?", show_alert=True)
           return
        if member.status == "kicked" or member.status == "left":
           query.answer("This Person Is Not Even A Member In This Chat! How am I meant to promote him?", show_alert=True)
           return
        if member.status == "administrator":
           query.answer("This Person Is Already An Administrator! How am I meant to promote him?", show_alert=True)
           return
        if member.status != "administrator":
            # set same perms as bot - bot can't assign higher perms than itself!
            bot = chat.get_member(context.bot.id)
            try:
                context.bot.promoteChatMember(
                     chat.id,
                     user_id,
                     can_change_info=bot.can_change_info,
                     can_post_messages=bot.can_post_messages,
                     can_edit_messages=bot.can_edit_messages,
                     can_delete_messages=bot.can_delete_messages,
                     can_invite_users=bot.can_invite_users,
                     can_restrict_members=bot.can_restrict_members,
                     can_pin_messages=bot.can_pin_messages,
                )
            except BadRequest as br:
                message.reply_text(f"failed to promote: \n{br.message}")
                return

            query.answer("Promoted Successfully!", show_alert=True)
            query.message.edit_text(
                text=f"<b>{mention_html(user_id, member.user.first_name or user_id)}</b> was promoted by <b>{mention_html(query.from_user.id, query.from_user.first_name or query.from_user.id)}</b> in <b>{chat.title}</b>!",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                timeout=60,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Demote", callback_data=f"admim-demote {user_id}")]]),
            )

    elif query_match == "admim-demote":
        member = chat.get_member(int(user_id))
        if member.status == "creator":
           query.answer("This Person Is A Chat Creator! How am I meant to demote him?", show_alert=True)
           return
        if member.status == "kicked" or member.status == "left":
           query.answer("This Person Is Not Even A Member In This Chat! How am I meant to demote him?", show_alert=True)
           return
        if member.status != "administrator":
           query.answer("This Person Is Not Even An Administrator! How am I meant to demote him?", show_alert=True)
           return
        if member.status == "administrator":
            try:
                context.bot.promoteChatMember(
                     chat.id,
                     user_id,
                     can_change_info=False,
                     can_post_messages=False,
                     can_edit_messages=False,
                     can_delete_messages=False,
                     can_invite_users=False,
                     can_restrict_members=False,
                     can_pin_messages=False,
                     can_promote_members=False,
                     can_manage_voice_chats=False,
                )
            except BadRequest as br:
                message.reply_text(f"failed to demote: \n{br.message}")
                return

            query.answer("Demoted Successfully!", show_alert=True)
            query.message.edit_text(
                text=f"<b>{mention_html(user_id, member.user.first_name or user_id)}</b> was demoted by <b>{mention_html(query.from_user.id, query.from_user.first_name or query.from_user.id)}</b> in <b>{chat.title}</b>!",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
                timeout=60,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="Demote", callback_data=f"admim-promote {user_id}")]]),
            )

    context.bot.answer_callback_query(query.id)



def get_help(chat):
    from tg_bot.modules.language import gs
    return gs(chat, "admin_help")

__mod_name__ = "Admin"

__commands__ = ["fullpromote", "invitelink", "admins", "setgtitle", "delgpic", "setgpic", "setsticker", "setdescription", "setdesc"]
