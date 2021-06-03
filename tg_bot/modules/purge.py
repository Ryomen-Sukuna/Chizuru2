from telethon import events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError

from tg_bot import telethn
from tg_bot.modules.helper_funcs.telethn.chatstatus import user_is_admin, can_delete_messages



async def purge_messages(event):
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

    reply_message = await event.get_reply_message()
    if not reply_message:
        await event.reply(
            "Reply to a message to select where to start purging from.")
        return

    messages = []
    reason = event.text.split(" ", 1)
    chat = await event.get_input_chat()
    message_id, delete_to = reply_message.id, event.message.id

    try:
        await event.client.delete_messages(event.chat_id, event.message.id)
        messages.append(event.reply_to_msg_id)
        for msg in range(delete_to, message_id - 1, -1):
             messages.append(msg)
             if len(messages) == 100:
                 await event.client.delete_messages(event.chat_id, messages)
                 messages = []

        if messages:
            await event.client.delete_messages(event.chat_id, messages)

        text = "Purged Completed!"
        if len(reason) > 1:
            text += "\n\n**Purged Reason:** \n" + reason[1]

        await event.client.send_message(event.chat_id, text)

    except MessageDeleteForbiddenError:
        text = "Failed to delete messages.\n"
        text += "Messages maybe too old or I'm not admin! or dont have delete rights!"
        await event.respond(text)



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



PURGE_HANDLER = purge_messages, events.NewMessage(pattern="^[!/]purge ?(.*)")
DEL_HANDLER = delete_messages, events.NewMessage(pattern="^[!/]del$")

telethn.add_event_handler(*PURGE_HANDLER)
telethn.add_event_handler(*DEL_HANDLER)

__mod_name__ = "Purges"
__command_list__ = ["purge", "del"]
__handlers__ = [PURGE_HANDLER, DEL_HANDLER]
