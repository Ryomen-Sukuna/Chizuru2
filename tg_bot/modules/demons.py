import asyncio
from asyncio import sleep

from telethon import events, Button
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

from tg_bot import client
from tg_bot.modules.helper_funcs.telethn.chatstatus import user_is_admin, can_ban_users


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


# Demons
async def demons(event):
    del_u = 0 

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights

    # Check Permissions
    if not await user_is_admin(event.sender_id, event) and event.from_id not in [1087968824]:
        await event.respond("You don't have the necessary rights to do this!")
        return
    if not admin and not await can_ban_users(event):
        await event.respond("I haven't got the rights to do this.")
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
        dimon = f"Found **{del_u} - Demon** In This Chat!\n\nWould You Like To Hunt That Demon ?"
        dimons = f"Found **{del_u} - Demons** In This Chat!\n\nWould You Like To Hunt Them All ?"
        demons = dimons if del_u > 1 else dimon
        await X.edit(
            demons,
            buttons=markup,
        )
    else:
        await X.edit("There Are No Demons! \nThis Chat Is Safe For Now!")


@client.on(events.CallbackQuery)
async def dimonhandler(event):
    if event.data == b'demon_yes':
        # Here laying the sanity check
        but = await event.get_chat()
        admim = but.admin_rights

        # Check Permissions
        if not await user_is_admin(event.sender_id, event) and event.from_id not in [1087968824]:
            await event.respond("You don't have the necessary rights to do this!")
            return
        if not admim and not await can_ban_users(event):
            await event.respond("I haven't got the rights to do this.")
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
    elif event.data == b'demon_no':
          await event.edit("Demom Hunting Task Cancelled!")
          await event.answer("Cancelled!")



DEMONS = demons, events.NewMessage(pattern="^[!/]demons$")
client.add_event_handler(*DEMONS)


__mod_name__ = "Demons"
__command_list__ = ["demons"]
__handlers__ = [DEMONS]
