import telebot
import telebot.formatting

from telebot.async_telebot import AsyncTeleBot

from .template import Command
from .guard import guard_commands
from src.utils.translation import TranslationInterface  # FIXME


@guard_commands(on_fail=lambda _, r: print(r))
class Translator(Command):
    def __init__(self, bot: AsyncTeleBot, translator: TranslationInterface):
        super().__init__(bot)
        self.translator = translator

        @self.bot.message_handler(commands=["translate"])
        async def translate(message: telebot.types.Message):
            await self._translate(message)

    async def _translate(self, message: telebot.types.Message):
        await self.bot.delete_message(message.chat.id, message.message_id)
        if not message.reply_to_message:
            return

        await self.bot.send_message(
            message.chat.id,
            telebot.formatting.hcite(
                await self.translator.translate_async(message.reply_to_message.text),
                expandable=True
            ),
            reply_to_message_id=message.reply_to_message.message_id,
            parse_mode="html"
        )
