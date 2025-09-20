import os
import asyncio

from bot import TranslationBot
from utils import load_env

load_env("../secrets/token.txt", "tg-bot-token")

bot = TranslationBot(os.environ["tg-bot-token"])
asyncio.run(bot.run())
