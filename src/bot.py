from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from services.translator import Translator
from utils.translation import MymemoryAPI


class TranslationBot(object):
    def __init__(self, token: str):
        self.bot = AsyncTeleBot(token, state_storage=StateMemoryStorage())
        self.bot.add_custom_filter(asyncio_filters.StateFilter(self.bot))

        self.translation_service = Translator(self.bot, MymemoryAPI())

    async def run(self):
        await self.bot.polling()
