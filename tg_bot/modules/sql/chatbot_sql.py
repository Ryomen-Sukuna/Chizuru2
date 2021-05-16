import threading

from sqlalchemy import Column, String
from tg_bot.modules.sql import BASE, SESSION


class ChatbotChats(BASE):
    __tablename__ = "chatbot_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id: str):
        self.chat_id = chat_id

    def __repr__(self):
        return "chatbot for {}".format(self.chat_id)



ChatbotChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_chat(chat_id):
    try:
        chat = SESSION.query(ChatbotChats).get(str(chat_id))
        if chat:
            return True
        else:
            return False
    finally:
        SESSION.close()


def add_chat(chat_id: str):
    with INSERTION_LOCK:
        chatbot = SESSION.query(ChatbotChats).get(str(chat_id))
        if not chatbot:
            chatbot = ChatbotChats(str(chat_id))
            SESSION.add(chatbot)

        SESSION.commit()


def del_chat(chat_id):
    with INSERTION_LOCK:
        chatbot = SESSION.query(ChatbotChats).get(str(chat_id))
        if chatbot:
            SESSION.delete(chatbot)

        SESSION.commit()


def get_all_chats():
    try:
        return SESSION.query(ChatbotChats.chat_id).all()
    finally:
        SESSION.close()
