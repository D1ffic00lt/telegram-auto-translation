from telebot.async_telebot import AsyncTeleBot

from .guard import guard_commands


@guard_commands(on_fail=lambda _, r: print(r))
class Command(object):
    def __init__(
        self, bot: AsyncTeleBot,
    ):
        self.bot = bot
