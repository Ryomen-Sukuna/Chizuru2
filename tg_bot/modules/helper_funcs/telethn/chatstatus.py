from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator, ChannelParticipantsAdmins

from tg_bot import SUDO_USERS, WHITELIST_USERS
from tg_bot.modules.helper_funcs.telethn import telethn as tbot


async def user_is_ban_protected(user_id: int, message):
    if message.is_private or user_id in (WHITELIST_USERS + SUDO_USERS):
        return True

    if message.is_channel:
        participant = await tbot(
            GetParticipantRequest(message.chat_id, user_id))
        return isinstance(participant.participant,
                          (ChannelParticipantAdmin, ChannelParticipantCreator))

    async for user in tbot.iter_participants(message.chat_id,
                                             filter=ChannelParticipantsAdmins):
        if user_id == user.id:
            return True
    return False


async def user_is_admin(user_id: int, message):
    if message.is_private or user_id in SUDO_USERS:
        return True

    if message.is_channel:
        participant = await tbot(
            GetParticipantRequest(message.chat_id, user_id))
        return isinstance(participant.participant,
                          (ChannelParticipantAdmin, ChannelParticipantCreator))

    async for user in tbot.iter_participants(message.chat_id,
                                             filter=ChannelParticipantsAdmins):
        if user_id == user.id:
            return True
    return False


async def is_user_admin(user_id: int, message):
    if user_id in SUDO_USERS:
        return True

    try:
        participant = await tbot(GetParticipantRequest(message.chat_id, user_id))
        return isinstance(participant.participant,
                          (ChannelParticipantAdmin, ChannelParticipantCreator))
    except TypeError:
        async for user in tbot.iter_participants(
                message.chat_id, filter=ChannelParticipantsAdmins):
            if user_id == user.id:
                return True
    return False


async def bot_is_admin(chat_id: int):
    try:
        participant = await tbot(GetParticipantRequest(chat_id, 'me'))
        return isinstance(participant.participant, ChannelParticipantAdmin)
    except TypeError:
        async for user in tbot.iter_participants(
                chat_id, filter=ChannelParticipantsAdmins):
            if user.is_self:
                return True
    return False


async def is_user_in_chat(chat_id: int, user_id: int):
    status = False
    async for user in tbot.iter_participants(chat_id):
        if user_id == user.id:
            status = True
            break
    return status


async def can_delete_messages(message):
    if message.is_private:
        return True

    return (
        message.chat.admin_rights.delete_messages
        if message.chat.admin_rights
        else False
    )


async def can_change_info(message):
    return (
        message.chat.admin_rights.change_info
        if message.chat.admin_rights
        else False
    )


async def can_ban_users(message):
    return (
        message.chat.admin_rights.ban_users
        if message.chat.admin_rights
        else False
    )


async def can_invite_users(message):
    return (
        message.chat.admin_rights.invite_users
        if message.chat.admin_rights
        else False
    )


async def can_add_admins(message):
    return (
        message.chat.admin_rights.add_admins
        if message.chat.admin_rights
        else False
    )


async def can_pin_messages(message):
    return (
        message.chat.admin_rights.pin_messages
        if message.chat.admin_rights
        else False
    )
