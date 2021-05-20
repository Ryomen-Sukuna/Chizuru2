from typing import Union
from tg_bot.langs import get_string
import tg_bot.modules.sql.language_sql as sql



def gs(chat_id: Union[int, str], string: str) -> str:
    lang = sql.get_chat_lang(chat_id)
    return get_string(lang, string)
