import time
from telethon import events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError

from tg_bot import client
from tg_bot.modules.helper_funcs.telethn.chatstatus import can_delete_messages, user_is_admin


async def purge_messages(event):
    start = time.perf_counter()
    if event.from_id is None:
        return

    if not await user_is_admin(
            user_id=event.sender_id, message=event) and event.from_id not in [
                1087968824
            ]:
        await event.reply("Only Admins are allowed to use this command")
        return

    if not await can_delete_messages(message=event):
        await event.reply("Can't seem to purge the message")
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply(
            "Reply to a message to select where to start purging from.")
        return

    count = 0
    messages = []
    message_id = reply_msg.id
    delete_to = event.message.id
    reason = event.text.split(" ", 1)

    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == 100:
            await event.client.delete_messages(event.chat_id, messages)
            messages = []


    try:
        await event.client.delete_messages(event.chat_id, event.message.id)
        messages.append(event.reply_to_msg_id)
        for m_id in range(delete_to, message_id - 1, -1):
            messages.append(m_id)
            count += 1
            if len(messages) == 100:
                await event.client.delete_messages(event.chat_id, messages)
                messages = []

        try:
            await event.client.delete_messages(event.chat_id, messages)
        except:
            pass

        time_ = time.perf_counter() - start
        text = f"Purged {count} Messages In {time_:0.2f} Secs."
        if len(reason) > 1:
           text += "\n\n**Purged Reason:** " + reason[1]

        await event.client.send_message(event.chat_id, text)

    except MessageDeleteForbiddenError:
        text = "Failed to delete messages.\n"
        text += "Messages maybe too old or I'm not admin! or dont have delete rights!"
        await event.respond(text, parse_mode="md")



async def delete_messages(event):
    if event.from_id is None:
        return

    if not await user_is_admin(
            user_id=event.sender_id, message=event) and event.from_id not in [
                1087968824
            ]:
        await event.reply("Only Admins are allowed to use this command")
        return

    if not await can_delete_messages(message=event):
        await event.reply("Can't seem to delete this?")
        return

    message = await event.get_reply_message()
    if not message:
        await event.reply("Whadya want to delete?")
        return
    chat = await event.get_input_chat()
    del_message = [message, event.message]
    await event.client.delete_messages(chat, del_message)


def get_help(chat):
    from tg_bot.modules.language import gs
    return gs(chat, "purge_help")



me = await client.get_me()
PURGE_HANDLER = purge_messages, events.NewMessage(pattern=["^[!/]purge ?(.*)", f"^[!/]purge@{me.username} ?(.*)])
DEL_HANDLER = delete_messages, events.NewMessage(pattern=["^[!/]del ?(.*)", f"^[!/]del@{me.username} ?(.*)"])

client.add_event_handler(*PURGE_HANDLER)
client.add_event_handler(*DEL_HANDLER)

__mod_name__ = "Purges"
__command_list__ = ["del", "purge"]
__handlers__ = [PURGE_HANDLER, DEL_HANDLER]
