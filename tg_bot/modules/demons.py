import asyncio
from asyncio import sleep

from telethon import events, Button
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

from tg_bot import client, OWNER_ID, DEV_USERS, SUDO_USERS


# =================== CONSTANT ===================
BANNED_RIGHTS = ChatBannedRights(
         until_date=None,
         view_messages=True,
         send_messages=True,
         send_media=True,
         send_stickers=True,
         send_gifs=True,
         send_games=True,
         send_inline=True,
         embed_links=True,
)
UNBAN_RIGHTS = ChatBannedRights(
        until_date=None,
        send_messages=None,
        send_media=None,
        send_stickers=None,
        send_gifs=None,
        send_games=None,
        send_inline=None,
        embed_links=None,
)


SLAYERS = [OWNER_ID] + DEV_USERS + SUDO_USERS

# Check if user has admin rights
async def is_admin(user_id: int, message):
    admin = False
    async for user in client.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or user_id in SLAYERS:
            admin = True
            break
    return admin


# Demons
async def demons(event):
    del_u = 0 

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights

    # Check Permissions
    if not await is_admin(event.sender_id, event) and event.from_id not in [1087968824]:
        await event.respond("You're Not An Admin!")
        return
    if not admin:
        await event.respond("I Am Not An Admin Here!")
        return

    X = await event.respond("Searching For Demons...")
    async for user in event.client.iter_participants(event.chat_id):
            if user.deleted:
                del_u += 1
                await sleep(1)
    if del_u > 0:
        markup = [
           [Button.inline('Yes', data='demon_yes'),],
           [Button.inline('No', data='demon_no'),],
        ]
        dimon = f"Found **{del_u} - Demon** In This Chat!\n\nWould You Like To Kill That Demon ?"
        dimons = f"Found **{del_u} - Demons** In This Chat!\n\nWould You Like To Kill All That Demons ?"
        demons = dimons if del_u > 1 else dimon
        await X.edit(
            demons,
            buttons=markup,
        )
    else:
        await X.edit("There Are No Demons! \nThis Chat Is Safe For Now!")


@client.on(events.CallbackQuery)
async def dimonhandler(event):
    if event.data == 'demon_yes':
        if not await is_admin(event.query.user_id, event) and event.from_id not in [1087968824]:
             await event.answer("You're Not An Admin!")
             return
        admim = await event.get_chat().admin_rights
        if not admim:
             await event.answer("I Am Not An Admin Here!")
             return
        await event.edit("Hunting Demons...")
        del_u = 0
        del_a = 0

        async for user in event.client.iter_participants(event.chat_id):
            if user.deleted:
                try:
                    await event.client(
                        EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS)
                    )
                except ChatAdminRequiredError:
                    await event.edit("I Don't Have Ban Rights In This Chat!")
                    return
                except UserAdminInvalidError:
                    del_u -= 1
                    del_a += 1
                await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
                del_u += 1

        if del_u > 0:
            demon = f"Hunted `{del_u}` - Demon{'s' if del_u > 1 else ''}"
            if del_a > 0:
                demon += f"\n`{del_a}` - Upper Level Demon{'s' if del_a > 1 else ''} {'Are' if del_a > 1 else 'Is'} Escaped!"

            await event.edit(demon)
            await event.answer("Demon Hunted!")
    elif event.data == 'demon_no':
          await event.edit("Demom Hunting Task Cancelled!")
          await event.answer("Cancelled!")



DEMONS = demons, events.NewMessage(pattern=f"^[!/]demons")
client.add_event_handler(*DEMONS)


__mod_name__ = "Demons"
__command_list__ = ["demons"]
__handlers__ = [DEMONS]
