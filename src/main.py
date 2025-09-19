import os
import asyncio

from bot import TranslationBot
from utils import load_env

load_env("./secrets/token.txt")

bot = TranslationBot(os.environ["tg-bot-token"])
asyncio.run(bot.run())
