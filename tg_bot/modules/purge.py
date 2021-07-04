from telethon import events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError
PURGE = {}
from tg_bot import telethn
from tg_bot.modules.helper_funcs.telethn.chatstatus import is_user_admin, can_delete_messages


# Purge From
async def purge_from(event):
    if event.fwd_from or event.from_id is None:
        return

    if not await is_user_admin(
            user_id=event.sender_id, message=event) and event.from_id not in [
                1087968824
            ]:
        await event.reply("Only Admins are allowed to use this command")
        return

    if not await can_delete_messages(message=event):
        await event.reply("I can't delete messages in this chat! Give me admin and message deleting rights first.")
        return

    reply = await event.get_reply_message()
    if not reply:
        await event.reply("Reply to a message to let me know what to delete.")
        return

    reply = await event.reply(
            "This Message marked for deletion. Reply to another message with /purgeto to delete all messages in between.",
    )
    print(reply)
    await event.client.delete_messages(event.chat_id, (await event.get_reply_message()).id)
    PURGE[event.chat_id] = [event.reply_to_msg_id, reply.id]

# Purge To
async def purge_to(event):
    if event.fwd_from or event.from_id is None:
        return

    if not await is_user_admin(
            user_id=event.sender_id, message=event) and event.from_id not in [
                1087968824
            ]:
        await event.reply("Only Admins are allowed to use this command")
        return

    try:
        purge_from = PURGE[event.chat_id]
    except KeyError:
        await event.reply(
            "You can only use this command after having used the /purgefrom command.",
        )
        return

    if not await can_delete_messages(message=event):
        await event.client.delete_messages(event.chat_id, purge_from[1])
        PURGE.pop(event.chat_id)
        await event.reply("I can't delete messages in this chat! Give me admin and message deleting rights first.")
        return

    reply = await event.get_reply_message()
    if not reply:
        await event.reply(
            "Reply to a message to let me know what to delete.",
        )
        return

    messages = []
    purge_to = reply.id
    try:
        await event.client.delete_messages(event.chat_id, event.message.id)
        messages.append(event.reply_to_msg_id)
        for message in range(purge_to, purge_from[0] - 1, -1):
             messages.append(message)
             if len(messages) == 100:
                 await event.client.delete_messages(event.chat_id, messages)
                 messages = []

        if messages:
            await event.client.delete_messages(event.chat_id, messages)

        await event.respond("**Purged Completed!**")

    except MessageDeleteForbiddenError:
        await event.client.delete_messages(event.chat_id, purge_from[1])
        PURGE.pop(event.chat_id)
        text = "Failed to delete messages.\n"
        text += "Messages maybe too old or I'm not admin! or dont have delete rights!"

    except Exception as e:
        await event.client.delete_messages(event.chat_id, purge_from[1])
        PURGE.pop(event.chat_id)
        text = "Failed to purge:" + e
        await event.respond(text)

# Message Purge
async def purge_messages(event):
    if event.fwd_from or event.from_id is None:
        return

    if not await is_user_admin(
            user_id=event.sender_id, message=event) and event.from_id not in [
                1087968824
            ]:
        await event.reply("Only Admins are allowed to use this command")
        return

    if not await can_delete_messages(message=event):
        await event.reply("I can't delete messages in this chat! Give me admin and message deleting rights first.")
        return

    reply_message = await event.get_reply_message()
    if not reply_message:
        await event.reply(
            "Reply to a message to let me know what to delete.")
        return

    messages = []
    reason = event.text.split(" ", 1)
    purge_from, purge_to = reply_message.id, event.message.id

    try:
        await event.client.delete_messages(event.chat_id, purge_to)
        messages.append(event.reply_to_msg_id)
        for msg in range(purge_to, purge_from - 1, -1):
             messages.append(msg)
             if len(messages) == 100:
                 await event.client.delete_messages(event.chat_id, messages)
                 messages = []

        if messages:
            await event.client.delete_messages(event.chat_id, messages)

        text = "**Purged Completed!**"
        if len(reason) > 1 and not reason[1].isdigit():
            text += "\n\n**Purged Reason:** \n" + reason[1]

        if not event.text.startswith("/s"):
            await event.client.send_message(event.chat_id, text)

    except MessageDeleteForbiddenError:
        text = "Failed to delete messages.\n"
        text += "Messages maybe too old or I'm not admin! or dont have delete rights!"
        await event.respond(text)

# Message Deleting
async def delete_messages(event):
    if event.fwd_from or event.from_id is None:
        return

    if not await is_user_admin(
            user_id=event.sender_id, message=event) and event.from_id not in [
                1087968824
            ]:
        await event.reply("Only Admins are allowed to use this command")
        return

    if not await can_delete_messages(message=event):
        await event.reply("I can't delete messages in this chat! Give me admin and message deleting rights first.")
        return

    message = await event.get_reply_message()
    if not message:
        await event.reply("Reply to a message to let me know what to delete.")
        return

    chat = await event.get_input_chat()
    del_message = [message, event.message]
    await event.client.delete_messages(chat, del_message)


def get_help(chat):
    from tg_bot.modules.language import gs
    return gs(chat, "purge_help")



PURGE_FROM_HANDLER = purge_from, events.NewMessage(pattern=r"^[!/]purgefrom$")
PURGE_TO_HANDLER = purge_to, events.NewMessage(pattern=r"^[!/]purgeto$")
PURGE_HANDLER = purge_messages, events.NewMessage(pattern=r"^[!/](purge|spurge)($| (.*))")
DEL_HANDLER = delete_messages, events.NewMessage(pattern=r"^[!/](del|delete)$")

telethn.add_event_handler(*PURGE_FROM_HANDLER)
telethn.add_event_handler(*PURGE_TO_HANDLER)
telethn.add_event_handler(*PURGE_HANDLER)
telethn.add_event_handler(*DEL_HANDLER)

__mod_name__ = "Purges"
__commands__ = ["purgefrom", "purgeto", "purge", "del", "delete"]
__handlers__ = [
        PURGE_FROM_HANDLER,
        PURGE_TO_HANDLER,
        PURGE_HANDLER,
        DEL_HANDLER,
               ]
