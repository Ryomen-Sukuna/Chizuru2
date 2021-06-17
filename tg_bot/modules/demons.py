import asyncio

from telethon import events, Button
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights, ChannelParticipantsAdmins

from tg_bot import telethn
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

    demons: int = 0
    X = await event.respond("Searching For Demons...")
    async for user in event.client.iter_participants(event.chat_id):
            if user.deleted:
                demons += 1
                await asyncio.sleep(1)

    if demons > 0:
        markup = [
           [Button.inline("Yes", data="demons yes")],
           [Button.inline("No", data="demons no")],
        ]
        demon = f"Found **{demons}** Demon{'s' if demons > 1 else ''} In This Chat!\n\nWould You Like To Hunt {'Them All' if demons > 1 else 'That Demon'} ?"
        await X.edit(
            demon,
            buttons=markup,
        )
    else:
        await X.edit("There Are No Demons! \nThis Chat Is Safe For Now!")


@client.on(events.CallbackQuery)
async def dimonhandler(event):
    if event.data == "demons yes":
        # Here laying the sanity check
        but = await event.get_chat()
        admim = but.admin_rights

        # Check Permissions
        if not await user_is_admin(event.sender_id, event) and event.from_id not in [1087968824]:
            await event.respond("You don't have the necessary rights to do this!")
            return
        if not admim and not await can_ban_users(event):
            await event.respond("I haven't got the necessary rights to do this.")
            return

        await event.edit("Hunting Demons...")
        normy_demons: int = 0
        pro_demons: int = 0

        async for user in event.client.iter_participants(event.chat_id):
            if user.deleted:
                try:
                    await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
                    await asyncio.sleep(1)
                except ChatAdminRequiredError:
                    await event.edit("I haven't got the necessary rights to do this.")
                    return
                except UserAdminInvalidError:
                    normy_demons -= 1
                    pro_demons += 1
                await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
                normy_demons += 1

        demon = ""
        if normy_demons > 0:
            demon += f"**{normy_demons}** - Hunted Demon{'s' if normy_demons > 1 else ''}!"
        if pro_demons > 0:
            demon += f"\n**{pro_demons}** - Upper Level Demon{'s' if pro_demons > 1 else ''} {'Are' if pro_demons > 1 else 'Is'} Escaped!"

        await event.edit(demon)
        await event.answer("Demon Hunted!")
    elif event.data == "demons no":
          await event.edit("Demom Hunting Task Cancelled!")
          await event.answer("Cancelled!")



DEMONS = demons, events.NewMessage(pattern="^[!/]demons$")
telethn.add_event_handler(*DEMONS)


__mod_name__ = "Demons"
__command_list__ = ["demons"]
__handlers__ = [DEMONS]
