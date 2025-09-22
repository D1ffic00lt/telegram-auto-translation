import telebot
import telebot.formatting as formatting

from telebot.async_telebot import AsyncTeleBot

from .template import Command
from .guard import guard_commands
from .utils.translation import TranslationInterface


@guard_commands(on_fail=lambda _, r: print(r))
class ChatTranslator(Command):
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
            formatting.format_text(
                formatting.mcite(
                    (await self.translator.translate_async(message.reply_to_message.text)), expandable=True
                ),
                separator="\n\n",
            ),
            reply_to_message_id=message.reply_to_message.message_id,
            parse_mode="MarkdownV2",
        )


@guard_commands(on_fail=lambda _, r: print(r))
class ChannelTranslator(Command):
    def __init__(self, bot: AsyncTeleBot, translator: TranslationInterface):
        super().__init__(bot)
        self.translator = translator

        @self.bot.channel_post_handler(commands=["translate"])
        async def translate(message: telebot.types.Message):
            await self._translate(message)

    async def _translate(self, message: telebot.types.Message):
        print(message.reply_to_message.forward_origin)
        await self.bot.delete_message(message.chat.id, message.message_id)
        if not message.reply_to_message:
            return
        if message.reply_to_message.forward_origin is None:
            await self.bot.edit_message_text(
                formatting.format_text(
                    message.reply_to_message.text or "",
                    formatting.mcite(
                        (await self.translator.translate_async(message.reply_to_message.text)), expandable=True
                    ),
                    separator="\n\n",
                ),
                message.chat.id,
                message.reply_to_message.message_id,
                parse_mode="MarkdownV2",
            )
            return
        await self.bot.send_message(
            message.chat.id,
            formatting.format_text(
                formatting.mcite(
                    (await self.translator.translate_async(message.reply_to_message.text)), expandable=True
                ),
                separator="\n\n",
            ),
            reply_to_message_id=message.reply_to_message.message_id,
            parse_mode="MarkdownV2",
        )
