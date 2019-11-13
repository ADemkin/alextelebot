from random import choice
from random import shuffle
from typing import List
import logging

from telebot import TeleBot
from telebot import apihelper
from telebot.types import Message

from storage import Storage


apihelper.proxy = None

logger = logging.getLogger(__name__)
FORMAT = '%(asctime)s: %(message)s'
logging.basicConfig(level="INFO", format=FORMAT)


bot = TeleBot("916790500:AAEvH6zgk0WdYikMZ5gtPWdLAwc19o5TrME")


def get_user(message: Message) -> str:
    try:
        return "@{}".format(message.from_user.username)
    except AttributeError:
        pass
    try:
        return "{} {}".format(
            message.from_user.first_name,
            message.from_user.last_name,
        )
    except AttributeError:
        pass
    try:
        return "id: {}".format(message.from_user.id)
    except AttributeError:
        return "UNKNOWN_USER"


class Messages:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.last_messages: List[str] = []
        self.all_messages: List[str] = list(self.storage.load())

    def get(self) -> str:
        if not self.all_messages:
            return ''
        if len(self.all_messages) < 10:
            return choice(self.all_messages)
        while True:
            message = choice(self.all_messages)
            if message in self.last_messages:
                continue
            if len(self.last_messages) > 10:
                self.last_messages.pop(0)
            self.last_messages.append(message)
            return message

    def add(self, message: str) -> None:
        self.all_messages.append(str(message))
        self.storage.save(self.all_messages)


messages = Messages(Storage("messages.json"))


@bot.message_handler(commands=['ping'])
def ping(message):
    logger.info("%s asked for ping", get_user(message))
    bot.reply_to(message, "pong")


@bot.message_handler(commands=['add'])
def _add(message):
    logger.info("%s asked to add new message", get_user(message))
    bot.reply_to(message, "Reply to this message with new hateful theme")
    bot.register_next_step_handler(message, add_message)


def add_message(message):
    new_msg = message.text
    messages.add(str(new_msg))
    logger.info("%s added new message: '%s'", get_user(message), new_msg)
    bot.send_message(
        message.chat.id,
        "New message stored!\n{}".format(new_msg),
    )


@bot.message_handler(commands=['hate'])
def hate(message):
    hate_message = messages.get()
    logger.info("%s got '%s'", get_user(message), hate_message)
    bot.send_message(message.chat.id, hate_message)


@bot.message_handler(commands=['stat'])
def stat(message):
    logger.info("%s asked for stat", get_user(message))
    bot.send_message(
        message.chat.id,
        "I have total {} messages".format(len(messages.all_messages)),
    )


if __name__ == '__main__':
    logger.info("Started")
    logger.info("%d messages loaded", len(messages.all_messages))
    bot.polling()
