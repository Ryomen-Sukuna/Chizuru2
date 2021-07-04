import re
import html
import time
import random
from io import BytesIO
from functools import partial
from contextlib import suppress
from typing import Tuple, Optional
from multicolorcaptcha import CaptchaGenerator

from tg_bot import log, dispatcher, OWNER_ID, DEV_USERS, JOIN_LOGGER
import tg_bot.modules.sql.welcome_sql as sql
from tg_bot.modules.sql.antispam_sql import is_user_gbanned
from tg_bot.modules.helper_funcs.msg_types import get_welcome_type
from tg_bot.modules.helper_funcs.misc import build_keyboard, revert_buttons
from tg_bot.modules.helper_funcs.chat_status import user_admin, is_user_ban_protected
from tg_bot.modules.helper_funcs.string_handling import markdown_parser, escape_invalid_curly_brackets

from telegram.error import BadRequest
from telegram.utils.helpers import escape_markdown, mention_html, mention_markdown
from telegram.ext import Filters, MessageHandler, CommandHandler, CallbackContext, CallbackQueryHandler, ChatMemberHandler
from telegram import Update, ParseMode, ChatMember, ChatPermissions, ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]
ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
}
VERIFIED_USER_WAITLIST = {}
CAPTCHA_ANS_DICT = {}


def extract_status_change(
    chat_member_update: ChatMemberUpdated,
) -> Optional[Tuple[bool, bool]]:
    """Takes a ChatMemberUpdated instance and extracts whether the 'old_chat_member' was a member
    of the chat and whether the 'new_chat_member' is a member of the chat. Returns None, if
    the status didn't change."""
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get(
        "is_member", (None, None)
    )

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = (
        old_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR,
        ]
        or (old_status == ChatMember.RESTRICTED and old_is_member is True)
    )
    is_member = (
        new_status
        in [
            ChatMember.MEMBER,
            ChatMember.CREATOR,
            ChatMember.ADMINISTRATOR,
        ]
        or (new_status == ChatMember.RESTRICTED and new_is_member is True)
    )

    return was_member, is_member


# do not async
def send(update, message, keyboard, backup_message):
    chat = update.effective_chat
    reply = update.message.message_id

    try:
        msg = chat.send_message(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=reply,
            reply_markup=keyboard,
        )
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            msg = chat.send_message(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
            )
        elif excp.message == "Button_url_invalid":
            msg = chat.send_message(
                markdown_parser(
                    backup_message + "\nNote: the current message has an invalid url "
                    "in one of its buttons. Please update."
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        elif excp.message == "Unsupported url protocol":
            msg = chat.send_message(
                markdown_parser(
                    backup_message + "\nNote: the current message has buttons which "
                    "use url protocols that are unsupported by "
                    "telegram. Please update."
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
        elif excp.message == "Wrong url host":
            msg = chat.send_message(
                markdown_parser(
                    backup_message + "\nNote: the current message has some bad urls. *Please update*."
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
            log.warning(message)
            log.warning(keyboard)
            log.exception("Could not parse! got invalid url host errors")
        elif excp.message == "Have no rights to send a message":
            dispatcher.bot.leave_chat(chat.id)
            return
        else:
            msg = chat.send_message(
                markdown_parser(
                    backup_message + "\nNote: An error occured when sending the "
                    "custom message. Please update."
                ),
                parse_mode=ParseMode.MARKDOWN,
            )
            log.exception()

    cleanserv = sql.clean_service(chat.id)
    if cleanserv:
        try:
            dispatcher.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass

    return msg


def new_member(update: Update, context: CallbackContext):
    bot, job_queue = context.bot, context.job_queue
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    result = extract_status_change(update.chat_member)
    if result is None:
        return

    was_member, is_member = result
    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)
    human_checks = sql.get_human_checks(user.id, chat.id)

    if not was_member and is_member:

        new_mem = update.chat_member.new_chat_member.user
        res = None
        sent = None
        media_wel = False
        should_mute = True
        welcome_bool = True

        if new_mem.id == bot.id and user.id not in DEV_USERS:
          try:
              member = bot.get_chat_member(-1001287667199, user.id)
              if member.status in ("kicked", "left"):
                  with suppress(BadRequest):
                        chat.send_message("You Can't Add Me Because, You Are Not Member Of @TheLaughingCoffin!")
                  bot.leave_chat(chat.id)
                  return
          except BadRequest as BR:
              if BR.message in ("User not found", "User_not_mutual_contact", "User_not_participant"):
                  with suppress(BadRequest):
                        chat.send_message("You Can't Add Me Because, You Are Not Member Of @TheLaughingCoffin!")
                  bot.leave_chat(chat.id)
                  return

        if is_user_gbanned(new_mem.id):
            return

        if should_welc:

            # Give the owner a special welcome
            if new_mem.id == OWNER_ID:
                chat.send_message("Oh hi, my creator.")

            # Welcome Devs
            elif new_mem.id in DEV_USERS:
                chat.send_message("Whoa! An Admin of the @TheLaughingCoffin just joined!")

            # Welcome yourself
            elif new_mem.id == bot.id:
                chet_name = f"<a href='t.me/{chat.username}'>{html.escape(chat.title)}</a>" if chat.username else html.escape(chat.title)
                creator = None

                for x in bot.get_chat_administrators(chat.id):
                    if x.status == "creator":
                        creator = mention_html(x.user.id, html.escape(x.user.first_name) or "Creator") + f" (<code>{x.user.id}</code>)"
                        break

                bot.send_message(
                     JOIN_LOGGER,
                     "#NEW_GROUP\n\n"
                     "<b>Count:</b> {}\n<b>Chat:</b> {} (<code>{}</code>) {}\n\n<b>Adder:</b> {} (<code>{}</code>)".
                     format(chat.get_members_count(), chet_name, chat.id, ('\n\n<b>Creator:</b> ' + creator) if creator is not None else '', mention_html(user.id, html.escape(user.first_name) or "Adder"), user.id),
                     parse_mode=ParseMode.HTML, 
                     disable_web_page_preview=True,
                )

                chat.send_message(
                     f"You Have Rented {bot.first_name} For Your Chat. *That's Awesome!*" 
                     "\nSend [/help](t.me/ElitesOfRobot?start=help) Command In PM To Know About Me More. " 
                     "Join Our Chats For [Discussion](https://t.me/TheLaughingCoffin) & [Support](https://t.me/ElitesOfSupport).", 
                     parse_mode=ParseMode.MARKDOWN, 
                     disable_web_page_preview=True,
                )

            else:
                buttons = sql.get_welc_buttons(chat.id)
                keyb = build_keyboard(buttons)

                if welc_type not in (sql.Types.TEXT, sql.Types.BUTTON_TEXT):
                    media_wel = True

                first_name = (
                    new_mem.first_name or "PersonWithNoName"
                )  # edge case of empty name - occurs for some bugs.

                if cust_welcome:
                    if cust_welcome == sql.DEFAULT_WELCOME:
                        cust_welcome = random.choice(
                            sql.DEFAULT_WELCOME_MESSAGES
                        ).format(first=escape_markdown(first_name))

                    if new_mem.last_name:
                        fullname = escape_markdown(f"{first_name} {new_mem.last_name}")
                    else:
                        fullname = escape_markdown(first_name)
                    count = chat.get_members_count()
                    mention = mention_markdown(new_mem.id, escape_markdown(first_name))
                    if new_mem.username:
                        username = "@" + escape_markdown(new_mem.username)
                    else:
                        username = mention

                    valid_format = escape_invalid_curly_brackets(
                        cust_welcome, VALID_WELCOME_FORMATTERS
                    )

                    if "%%%" in valid_format:
                        split = valid_format.split("%%%")
                        if all(split):
                            cust_wel = random.choice(split)
                        else:
                            cust_wel = valid_format
                    else:
                        cust_wel = valid_format

                    res = cust_wel.format(
                        first=escape_markdown(first_name),
                        last=escape_markdown(new_mem.last_name or first_name),
                        fullname=escape_markdown(fullname),
                        username=username,
                        mention=mention,
                        count=count,
                        chatname=escape_markdown(chat.title),
                        id=new_mem.id,
                    )

                else:
                    res = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                    keyb = []

                backup_message = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                    first=escape_markdown(first_name)
                )
                keyboard = InlineKeyboardMarkup(keyb)

        else:
            welcome_bool = False
            res = None
            keyboard = None
            backup_message = None

        # User exceptions from welcomemutes
        if (
            is_user_ban_protected(chat, new_mem.id, chat.get_member(new_mem.id))
            or human_checks
        ):
            should_mute = False
        # Join welcome: soft mute
        if new_mem.is_bot:
            should_mute = False

        if user.id == new_mem.id:
            if should_mute and chat.get_member(bot.id).can_restrict_members:
                if welc_mutes == "soft":
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_add_web_page_previews=False,
                        ),
                        until_date=(int(time.time() + 24 * 60 * 60)),
                    )
                if welc_mutes == "strong":
                    welcome_bool = False
                    if not media_wel:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                (chat.id, new_mem.id): {
                                    "should_welc": should_welc,
                                    "media_wel": False,
                                    "status": False,
                                    "update": update,
                                    "res": res,
                                    "keyboard": keyboard,
                                    "backup_message": backup_message,
                                }
                            }
                        )
                    else:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                (chat.id, new_mem.id): {
                                    "should_welc": should_welc,
                                    "chat_id": chat.id,
                                    "status": False,
                                    "media_wel": True,
                                    "cust_content": cust_content,
                                    "welc_type": welc_type,
                                    "res": res,
                                    "keyboard": keyboard,
                                }
                            }
                        )
                    new_join_mem = f"[{escape_markdown(new_mem.first_name)}](tg://user?id={user.id})"
                    message = chat.send_message(
                        f"{new_join_mem}, click the button below to prove you're human.\nYou have 120 seconds.",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                {
                                    InlineKeyboardButton(
                                        text="Yes, I'm human.",
                                        callback_data=f"user_join_({new_mem.id})",
                                    )
                                }
                            ]
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False,
                        ),
                    )
                    job_queue.run_once(
                        partial(check_not_bot, new_mem, chat.id, message.message_id),
                        120,
                        name="welcomemute",
                    )
                if welc_mutes == "captcha":
                    btn = []
                    # Captcha image size number (2 -> 640x360)
                    CAPCTHA_SIZE_NUM = 2
                    # Create Captcha Generator object of specified size
                    generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)

                    # Generate a captcha image
                    captcha = generator.gen_captcha_image(difficult_level=2, multicolor=True)
                    # Get information
                    image = captcha["image"]
                    characters = captcha["characters"]
                    #print(characters)
                    fileobj = BytesIO()
                    fileobj.name=f'captcha_{new_mem.id}.png'
                    image.save(fp=fileobj)
                    fileobj.seek(0)
                    CAPTCHA_ANS_DICT[(chat.id, new_mem.id)] = int(characters)
                    welcome_bool = False
                    if not media_wel:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                (chat.id, new_mem.id): {
                                    "should_welc": should_welc,
                                    "media_wel": False,
                                    "status": False,
                                    "update": update,
                                    "res": res,
                                    "keyboard": keyboard,
                                    "backup_message": backup_message,
                                    "captcha_correct": characters,
                                }
                            }
                        )
                    else:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                (chat.id, new_mem.id): {
                                    "should_welc": should_welc,
                                    "chat_id": chat.id,
                                    "status": False,
                                    "media_wel": True,
                                    "cust_content": cust_content,
                                    "welc_type": welc_type,
                                    "res": res,
                                    "keyboard": keyboard,
                                    "captcha_correct": characters,
                                }
                            }
                        )

                    nums = [random.randint(1000, 9999) for _ in range(7)]
                    nums.append(characters)
                    random.shuffle(nums)
                    to_append = []
                    #print(nums)
                    for a in nums:
                        to_append.append(InlineKeyboardButton(text=str(a), callback_data=f"user_captchajoin_({chat.id},{new_mem.id})_({a})"))
                        if len(to_append) > 2:
                            btn.append(to_append)
                            to_append = []
                    if to_append:
                        btn.append(to_append)

                    message = chat.send_photo(fileobj, caption=f'Welcome [{escape_markdown(new_mem.first_name)}](tg://user?id={user.id}). Click the correct button to get unmuted!',
                                    reply_markup=InlineKeyboardMarkup(btn),
                                    parse_mode=ParseMode.MARKDOWN,
                              )
                    bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False,
                        ),
                    )

        if welcome_bool:
            if media_wel:
                if ENUM_FUNC_MAP[welc_type] == dispatcher.bot.send_sticker:
                    sent = ENUM_FUNC_MAP[welc_type](
                        chat.id,
                        cust_content,
                        reply_markup=keyboard,
                    )
                else:
                    sent = ENUM_FUNC_MAP[welc_type](
                        chat.id,
                        cust_content,
                        caption=res,
                        reply_markup=keyboard,
                        parse_mode=ParseMode.MARKDOWN,
                    )
            else:
                sent = send(update, res, keyboard, backup_message)
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

            if sent:
                sql.set_clean_welcome(chat.id, sent.message_id)


def auto_clean_wel(chat_id:int, message_id: int, context: CallbackContext):
     try:
         context.bot.delete_message(chat_id, message_id)
     except BadRequest:
         pass

def check_not_bot(member, chat_id: int, message_id: int, context: CallbackContext):
    bot = context.bot
    member_dict = VERIFIED_USER_WAITLIST.pop((chat_id, member.id))
    member_status = member_dict.get("status")
    if not member_status:
        try:
            bot.unban_chat_member(chat_id, member.id)
        except:
            pass

        try:
            bot.edit_message_text(
                "*kicks user*\nThey can always rejoin and try.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except:
            pass



@user_admin
def welcome(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    # if no args, show current replies.
    if not args or args[0].lower() == "noformat":
        noformat = True
        pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
        update.effective_message.reply_text(
            f"This chat has it's welcome setting set to: `{pref}`.\n"
            f"*The welcome message (not filling the {{}}) is:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if welcome_type == sql.Types.BUTTON_TEXT or welcome_type == sql.Types.TEXT:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)
        else:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)
                ENUM_FUNC_MAP[welcome_type](
                    chat.id,
                    cust_content,
                    caption=welcome_m,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_welc_preference(str(chat.id), True)
            update.effective_message.reply_text(
                "Okay! I'll greet members when they join."
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id), False)
            update.effective_message.reply_text(
                "I'll go loaf around and not welcome anyone then."
            )

        else:
            update.effective_message.reply_text(
                "I understand 'on/yes' or 'off/no' only!"
            )


@user_admin
def set_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("You didn't specify what to reply with!")
        return

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    msg.reply_text("Successfully set custom welcome message!")


@user_admin
def reset_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, sql.Types.TEXT)
    update.effective_message.reply_text(
        "Successfully reset welcome message to default!"
    )


@user_admin
def welcomemute(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if len(args) >= 1:
        if args[0].lower() in ("off", "no"):
            sql.set_welcome_mutes(chat.id, False)
            msg.reply_text("I will no longer mute people on joining!")

        elif args[0].lower() in ["soft"]:
            sql.set_welcome_mutes(chat.id, "soft")
            msg.reply_text(
                "I will restrict users' permission to send media for 24 hours."
            )

        elif args[0].lower() in ["strong"]:
            sql.set_welcome_mutes(chat.id, "strong")
            msg.reply_text(
                "I will now mute people when they join until they prove they're not a bot.\nThey will have 120seconds before they get kicked."
            )

        elif args[0].lower() in ["captcha"]:
            sql.set_welcome_mutes(chat.id, "captcha")
            msg.reply_text(
                "I will now mute people when they join until they prove they're not a bot.\nThey have to solve a captcha to get unmuted."
            )

        else:
            msg.reply_text(
                "Please enter `off`/`no`/`soft`/`strong`/`captcha`!",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        curr_setting = sql.welcome_mutes(chat.id)
        reply = (
            f"\n Give me a setting!\nChoose one out of: `off`/`no` or `soft`, `strong` or `captcha` only! \n"
            f"Current setting: `{curr_setting}`"
        )
        msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


@user_admin
def clean_welcome(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
            update.effective_message.reply_text(
                "I should be deleting welcome messages up to two days old."
            )
        else:
            update.effective_message.reply_text(
                "I'm currently not deleting old welcome messages!"
            )
        return

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id), True)
        update.effective_message.reply_text("I'll try to delete old welcome messages!")

    elif args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id), False)
        update.effective_message.reply_text("I won't delete old welcome messages.")

    else:
        update.effective_message.reply_text("I understand 'on/yes' or 'off/no' only!")


@user_admin
def cleanservice(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    if chat.type != chat.PRIVATE:
        if len(args) >= 1:
            var = args[0]
            if var in ("no", "off"):
                sql.set_clean_service(chat.id, False)
                update.effective_message.reply_text("Welcome clean service is : off")
            elif var in ("yes", "on"):
                sql.set_clean_service(chat.id, True)
                update.effective_message.reply_text("Welcome clean service is : on")
            else:
                update.effective_message.reply_text(
                    "Invalid option", parse_mode=ParseMode.MARKDOWN
                )
        else:
            update.effective_message.reply_text(
                "Usage is on/yes or off/no", parse_mode=ParseMode.MARKDOWN
            )
    else:
        curr = sql.clean_service(chat.id)
        if curr:
            update.effective_message.reply_text(
                "Welcome clean service is : on", parse_mode=ParseMode.MARKDOWN
            )
        else:
            update.effective_message.reply_text(
                "Welcome clean service is : off", parse_mode=ParseMode.MARKDOWN
            )


def user_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    match = re.match(r"user_join_\((.+?)\)", query.data)
    message = update.effective_message
    join_user = int(match.group(1))

    if join_user == user.id:
        sql.set_human_checks(user.id, chat.id)
        member_dict = VERIFIED_USER_WAITLIST[(chat.id, user.id)]
        member_dict["status"] = True
        query.answer(text="Yeet! You're a human, unmuted!")
        bot.restrict_chat_member(
            chat.id,
            user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        try:
            bot.deleteMessage(chat.id, message.message_id)
        except:
            pass
        if member_dict["should_welc"]:
            if member_dict["media_wel"]:
                sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                    member_dict["chat_id"],
                    member_dict["cust_content"],
                    caption=member_dict["res"],
                    reply_markup=member_dict["keyboard"],
                    parse_mode="markdown",
                )
            else:
                sent = send(
                    member_dict["update"],
                    member_dict["res"],
                    member_dict["keyboard"],
                    member_dict["backup_message"],
                )

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

    else:
        query.answer(text="You're not allowed to do this!")

def user_captcha_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    #print(query.data)
    match = re.match(r"user_captchajoin_\(([\d\-]+),(\d+)\)_\((\d{4})\)", query.data)
    message = update.effective_message
    join_chat = int(match.group(1))
    join_user = int(match.group(2))
    captcha_ans = int(match.group(3))
    join_usr_data = bot.getChat(join_user)


    if join_user == user.id:
        c_captcha_ans = CAPTCHA_ANS_DICT.pop((join_chat, join_user))
        if c_captcha_ans == captcha_ans:
            sql.set_human_checks(user.id, chat.id)
            member_dict = VERIFIED_USER_WAITLIST[(chat.id, user.id)]
            member_dict["status"] = True
            query.answer(text="Yeet! You're a human, unmuted!")
            bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    can_send_polls=True,
                    can_change_info=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            try:
                bot.deleteMessage(chat.id, message.message_id)
            except:
                pass
            if member_dict["should_welc"]:
                if member_dict["media_wel"]:
                    sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                        member_dict["chat_id"],
                        member_dict["cust_content"],
                        caption=member_dict["res"],
                        reply_markup=member_dict["keyboard"],
                        parse_mode="markdown",
                    )
                else:
                    sent = send(
                        member_dict["update"],
                        member_dict["res"],
                        member_dict["keyboard"],
                        member_dict["backup_message"],
                    )

                prev_welc = sql.get_clean_pref(chat.id)
                if prev_welc:
                    try:
                        bot.delete_message(chat.id, prev_welc)
                    except BadRequest:
                        pass

                    if sent:
                        sql.set_clean_welcome(chat.id, sent.message_id)
        else:
            try:
                bot.deleteMessage(chat.id, message.message_id)
            except:
                pass
            kicked_msg = f'''
            ❌ [{escape_markdown(join_usr_data.first_name)}](tg://user?id={join_user}) failed the captcha and was kicked.
            '''
            query.answer(text="Wrong answer")
            res = chat.unban_member(join_user)
            if res:
                bot.sendMessage(chat_id=chat.id, text=kicked_msg, parse_mode=ParseMode.MARKDOWN)


    else:
        query.answer(text="You're not allowed to do this!")



WELC_MUTE_HELP_TXT = (
    "You can get the bot to mute new people who join your group and hence prevent spambots from flooding your group. "
    "The following options are possible:\n"
    "• `/welcomemute soft`*:* restricts new members from sending media for 24 hours.\n"
    "• `/welcomemute strong`*:* mutes new members till they tap on a button thereby verifying they're human.\n"
    "• `/welcomemute captcha`*:*  mutes new members till they solve a button captcha thereby verifying they're human.\n"
    "• `/welcomemute off`*:* turns off welcomemute.\n"
    "*Note:* Strong mode kicks a user from the chat if they dont verify in 120seconds. They can always rejoin though"
)

@user_admin
def welcome_mute_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        WELC_MUTE_HELP_TXT, parse_mode=ParseMode.MARKDOWN
    )


# TODO: get welcome data from group butler snap
def __import_data__(chat_id, data):
     welcome = data.get('info', {}).get('rules')
     welcome = welcome.replace('$username', '{username}')
     welcome = welcome.replace('$name', '{fullname}')
     welcome = welcome.replace('$id', '{id}')
     welcome = welcome.replace('$title', '{chatname}')
     welcome = welcome.replace('$surname', '{lastname}')
     welcome = welcome.replace('$rules', '{rules}')
     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    welcome_pref = sql.get_welc_pref(chat_id)[0]
    return (
        "This chat has it's welcome preference set to `{}`.\n".format(welcome_pref)
    )



def get_help(chat):
    from tg_bot.modules.language import gs
    return gs(chat, "greetings_help")

NEW_MEM_HANDLER = ChatMemberHandler(
       new_member, ChatMemberHandler.CHAT_MEMBER
)
WELC_PREF_HANDLER = CommandHandler(
    "welcome", welcome, filters=Filters.chat_type.groups, run_async=True
)
SET_WELCOME = CommandHandler(
    "setwelcome", set_welcome, filters=Filters.chat_type.groups, run_async=True
)
RESET_WELCOME = CommandHandler(
    "resetwelcome", reset_welcome, filters=Filters.chat_type.groups, run_async=True
)
WELCOMEMUTE_HANDLER = CommandHandler(
    "welcomemute", welcomemute, filters=Filters.chat_type.groups, run_async=True
)
CLEAN_SERVICE_HANDLER = CommandHandler(
    "cleanservice", cleanservice, filters=Filters.chat_type.groups, run_async=True
)
WELCOME_MUTE_HELP = CommandHandler("welcomemutehelp", welcome_mute_help, run_async=True)
BUTTON_VERIFY_HANDLER = CallbackQueryHandler(
    user_button, pattern=r"user_join_", run_async=True
)
CAPTCHA_BUTTON_VERIFY_HANDLER = CallbackQueryHandler(
    user_captcha_button, pattern=r"user_captchajoin_\([\d\-]+,\d+\)_\(\d{4}\)", run_async=True
)

dispatcher.add_handler(NEW_MEM_HANDLER)
dispatcher.add_handler(WELC_PREF_HANDLER)
dispatcher.add_handler(SET_WELCOME)
dispatcher.add_handler(RESET_WELCOME)
dispatcher.add_handler(CLEAN_WELCOME)
dispatcher.add_handler(WELCOMEMUTE_HANDLER)
dispatcher.add_handler(CLEAN_SERVICE_HANDLER)
dispatcher.add_handler(BUTTON_VERIFY_HANDLER)
dispatcher.add_handler(WELCOME_MUTE_HELP)
dispatcher.add_handler(CAPTCHA_BUTTON_VERIFY_HANDLER)

__mod_name__ = "Greetings"
__commands__ = ["welcome", "setwelcome", "welcomemute", "welcomemute"]
__handlers__ = [
    NEW_MEM_HANDLER,
    WELC_PREF_HANDLER,
    SET_WELCOME,
    RESET_WELCOME,
    CLEAN_WELCOME,
    WELCOMEMUTE_HANDLER,
    CLEAN_SERVICE_HANDLER,
    BUTTON_VERIFY_HANDLER,
    CAPTCHA_BUTTON_VERIFY_HANDLER,
    WELCOME_MUTE_HELP,
]
