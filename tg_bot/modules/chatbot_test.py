from asyncio import sleep

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import BadRequest, Unauthorized

from tg_bot import kp as app, arq, RentalBot


# Get Response From API
async def getresp(query: str, id: int):
       luna = await arq.luna(query, id)
       return luna.result

def checker(message: Message):
    if message.text.lower() == f"@{RentalBot.bot_username}":
        return True
    reply_msg = message.reply_to_message
    if reply_msg and reply_msg.from_user is not None:
        if reply_msg.from_user.is_self:
            return True
    return False


@app.on_message(filters.text & ~filters.edited & ~filters.private)
async def chatbot_grp(_, message: Message):

    if not message.text:
        return
    if not checker(message):
        return
    if (message.text.startswith("/") or
        message.text.startswith("!") or
        message.text.startswith("#")):
        return

    query = message.text
    if len(query) > 50:
        return

    try:

        await app.send_chat_action(message.chat.id, "typing")
        luna = await getresp(query, message.from_user.id)
        await sleep(0.5)
        await message.reply_text(luna)
        await app.send_chat_action(message.chat.id, "cancel")

    except BadRequest as b:
        await app.send_message(-1001317669454,
                               f"AI ERROR: BadRequest \n\nChat: {message.chat.title} (`{message.chat.id}`)\n\n{b}",
                               parse_mode='md',
        )
    except Unauthorized as u:
        await app.send_message(-1001317669454,
                               f"AI ERROR: Unauthorized \n\nChat: {message.chat.title} (`{message.chat.id}`)\n\n{u}",
                               parse_mode='md',
        )
    except Exception as e:
        await app.send_message(-1001317669454,
                               f"AI ERROR: Exception \n\nChat: {message.chat.title} (`{message.chat.id}`)\n\n{e}",
                               parse_mode='md',
        )
