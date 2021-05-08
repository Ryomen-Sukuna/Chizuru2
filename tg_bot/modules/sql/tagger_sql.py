import threading

from sqlalchemy import Column, String, Integer

from tg_bot.modules.sql import BASE, SESSION


class Tagger(BASE):
    __tablename__ = "tagger"
    chat_id = Column(String(14), primary_key=True)
    user_id = Column(Integer, primary_key=True)

    def __init__(self, chat_id, user_id):
        self.chat_id = str(chat_id)  # ensure string
        self.user_id = user_id

    def __repr__(self):
        return "<Tag %s>" % self.user_id


Tagger.__table__.create(checkfirst=True)

TAG_INSERTION_LOCK = threading.RLock()


def tag(chat_id, user_id):
    with TAG_INSERTION_LOCK:
        tag_user = Tagger(str(chat_id), user_id)
        SESSION.add(tag_user)
        SESSION.commit()


def is_tag(chat_id, user_id):
    try:
        return SESSION.query(Tagger).get((str(chat_id), user_id))
    finally:
        SESSION.close()


def untag(chat_id, user_id):
    with TAG_INSERTION_LOCK:
        untag_user = SESSION.query(Tagger).get((str(chat_id), user_id))
        if untag_user:
            SESSION.delete(untag_user)
            SESSION.commit()
            return True
        else:
            SESSION.close()
            return False


def tag_list(chat_id):
    try:
        return (SESSION.query(Tagger).filter(
            Tagger.chat_id == str(chat_id)).order_by(
                Tagger.user_id.asc()).all())
    finally:
        SESSION.close()
