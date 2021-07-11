import random
import humanize
from time import sleep
from datetime import datetime

from telegram import Update, MessageEntity, ParseMode
from telegram.utils.helpers import escape_markdown
from telegram.ext import Filters, CallbackContext
from telegram.error import BadRequest

from tg_bot import OWNER_ID
from tg_bot.modules.sql import afk_sql as sql
from tg_bot.modules.users import get_user_id
from tg_bot.modules.helper_funcs.decorators import kigcmd, kigmsg


@kigcmd(command=["afk", "dnd"], group=7)
def afk(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    user = update.effective_user

    if not user:  # ignore channels
        return

    if user.id in [
              777000,
          1087968824,
       ]:
        return

    notice = ""
    if len(args) > 1:
        reason = args[1]
        if len(reason) > 100:
            reason = reason[:100]
            notice = "\n\nYour afk reason was shortened to 100 characters."
    else:
        reason = ""

    sql.set_afk(user.id, reason)
    fname = user.first_name if user.id != OWNER_ID else "My Master"
    try:
        R = update.effective_message.reply_text(
                 "{} Is Now Away!{}".format(fname, notice),
            )
        sql.update_afk(user.id, update.effective_chat.id, R.message_id)
    except BadRequest:
        return


@kigmsg((Filters.all & (~Filters.update.edited_message & ~Filters.status_update & ~Filters.venue) & Filters.chat_type.groups), friendly='afk', group=7)
def no_longer_afk(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.effective_message

    if not user:  # ignore channels
        return

    if not sql.is_afk(user.id):
        return

    res = sql.rm_afk(user.id)
    if res: 
        try:
            options = [
                # "{} Is Ready To Fight!",
                "{} Is Back Online!",
                "{} Is Here!",
            ]
            reply_msg = random.choice(options)
            message.reply_text(
                reply_msg.format(user.first_name if user.id != OWNER_ID else "My Master"),
            )
        except:
            return


@kigmsg((Filters.all & ~Filters.update.edited_message & Filters.chat_type.groups), friendly='afk', group=8)
def reply_afk(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    userc = update.effective_user
    userc_id = userc.id
    if message.entities and message.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION],
    ):
        entities = message.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION],
        )

        chk_users = []
        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                fst_name = ent.user.first_name

                if user_id in chk_users:
                    return
                chk_users.append(user_id)

            if ent.type != MessageEntity.MENTION:
                return

            user_id = get_user_id(
                message.text[ent.offset: ent.offset + ent.length],
            )
            if not user_id:
                return # Should never happen, since for a user to become AFK they must have spoken. Maybe changed username?

            if user_id in chk_users:
                return
            chk_users.append(user_id)

            try:
                chat = bot.get_chat(user_id)
            except (BadRequest, ValueError):
                return
            fst_name = chat.first_name

            check_afk(update, context, user_id, fst_name, userc_id)

    elif message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        fst_name = message.reply_to_message.from_user.first_name
        check_afk(update, context, user_id, fst_name, userc_id)


def check_afk(update: Update, context: CallbackContext, user_id: int, fst_name: str, userc_id: int):
    if sql.is_afk(user_id):
        if int(userc_id) == int(user_id):
            return

        user = sql.check_afk_status(user_id)
        fname = "My Master" if int(user_id) == OWNER_ID else f"User *{escape_markdown(fst_name)}*"
        since_afk = humanize.naturaldelta(datetime.now() - user.time)
        textmsg = f"{fname} Is AFK Since {since_afk}!"

        try:
            if user.messageid != (None, ""):
                context.bot.delete_message(int(user.messageid.split(' ', 1)[0]), int(user.messageid.split(' ', 1)[1]))
        except:
            pass
        try:
            DND = update.effective_message.reply_text(
                      textmsg,
                      parse_mode=ParseMode.MARKDOWN,
                  )
        except BadRequest:
            return

        if user.reason:
            reason = user.reason
            if "%%%" in user.reason:
                split = user.reason.split("%%%")
                reason = random.choice(split) if all(split) else user.reason

            textmsg += f"\n\n*Says It's Because Of:*\n{reason}"
            try:
                DND.edit_text(textmsg, disable_web_page_preview=True, parse_mode=ParseMode.MARKDOWN)
            except:
                pass
        sql.update_afk(user_id, update.effective_chat.id, DND.message_id)



def __gdpr__(user_id):
    sql.rm_afk(user_id)


__mod_name__ = "AFK"
__commands__ = ["afk", "dnd"]
