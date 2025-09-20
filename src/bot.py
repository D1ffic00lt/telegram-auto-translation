from telebot import asyncio_filters
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage

from services.translator import ChatTranslator, ChannelTranslator
from utils.translation import MymemoryAPI


class TranslationBot(object):
    def __init__(self, token: str):
        self.bot = AsyncTeleBot(token, state_storage=StateMemoryStorage())
        self.bot.add_custom_filter(asyncio_filters.StateFilter(self.bot))

        api = MymemoryAPI()

        self.chat_translation_service = ChatTranslator(self.bot, api)
        self.channel_translation_service = ChannelTranslator(self.bot, api)

    async def run(self):
        await self.bot.polling()
