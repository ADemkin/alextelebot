from copy import deepcopy
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

with open("token", "rb") as fd:
    token = fd.read().decode("ascii")

bot = TeleBot(token)


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
        self.all: List[str] = list(self.storage.load())
        self.current: List[str] = self._get_all_shuffled()

    def _get_all_shuffled(self) -> List[str]:
        current = deepcopy(self.all)
        shuffle(current)
        return current

    def get(self) -> str:
        if not self.current:
            if not self.all:
                return ''
            self.current = self._get_all_shuffled()
        return self.current.pop()

    def add(self, message: str) -> None:
        self.all.append(message)
        self.storage.save(sorted(self.all))

    def __len__(self):
        return len(self.all)


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
    if "/" in message:
        bot.send_message(message.chat.id, "Can not add command")
    # TODO: Check message time and maybe exit on timeout
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
        "I have total {} messages".format(len(messages)),
    )


if __name__ == '__main__':
    logger.info("Started")
    logger.info("%d messages loaded", len(messages))
    bot.polling()
