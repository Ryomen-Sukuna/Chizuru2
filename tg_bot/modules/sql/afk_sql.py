import threading
from datetime import datetime

from tg_bot.modules.sql import BASE, SESSION
from sqlalchemy import Boolean, Column, Integer, UnicodeText, DateTime


class AFK(BASE):
    __tablename__ = "dnd_users"

    user_id = Column(Integer, primary_key=True)
    is_afk = Column(Boolean)
    reason = Column(UnicodeText)
    time = Column(DateTime)
    messageid = Column(UnicodeText)

    def __init__(self, user_id: int, reason: str = "", messageid: str = '', is_afk: bool = True):
        self.user_id = user_id
        self.reason = reason
        self.messageid = messageid
        self.is_afk = is_afk
        self.time = datetime.now() # if int(user_id) != 1552759693 else datetime(2021, 2, 8)

    def __repr__(self):
        return "afk_status for {}".format(self.user_id)


AFK.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()

AFK_USERS = {}


def is_afk(user_id):
    return user_id in AFK_USERS


def check_afk_status(user_id):
    try:
        return SESSION.query(AFK).get(user_id)
    finally:
        SESSION.close()


def set_afk(user_id, reason=""):
    with INSERTION_LOCK:
        curr = SESSION.query(AFK).get(user_id)
        if not curr:
            curr = AFK(user_id, reason, '', True)
        else:
            curr.is_afk = True

        AFK_USERS[user_id] = {"reason": reason, "time": curr.time, "messageid": ""}

        SESSION.add(curr)
        SESSION.commit()


def update_afk(user_id: int, reason: str = None, chat_id: int = None, msg_id: int = None):
    with INSERTION_LOCK:
        curr = SESSION.query(AFK).get(user_id)
        curr.is_afk = True
        if reason:
            curr.reason = reason
        if chat_id:
            curr.messageid = f'{chat_id} {msg_id}'
        AFK_USERS[user_id] = {"reason": reason if reason else curr.reason, "time": curr.time, "messageid": f"{chat_id} {msg_id}" if chat_id else ""}

        SESSION.add(curr)
        SESSION.commit()


def rm_afk(user_id) -> bool:
    with INSERTION_LOCK:
        curr = SESSION.query(AFK).get(user_id)
        if curr:
            if user_id in AFK_USERS:  # sanity check
                del AFK_USERS[user_id]

            SESSION.delete(curr)
            SESSION.commit()
            return True

        SESSION.close()
        return False


def toggle_afk(user_id, reason=""):
    with INSERTION_LOCK:
        curr = SESSION.query(AFK).get(user_id)
        if not curr:
            curr = AFK(user_id, reason, '', True)
        elif curr.is_afk:
            curr.is_afk = False
        elif not curr.is_afk:
            curr.is_afk = True
        SESSION.add(curr)
        SESSION.commit()


def __load_afk_users():
    global AFK_USERS
    try:
        all_afk = SESSION.query(AFK).all()
        AFK_USERS = {
            user.user_id: {"reason": user.reason, "time": user.time, "messageid": user.messageid} for user in all_afk if user.is_afk
        }
    finally:
        SESSION.close()


__load_afk_users()
