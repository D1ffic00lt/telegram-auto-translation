import os

from . import translation
from . import exceptions


def load_env(filepath: str, *, force_load: bool = False):
    if "tg-bot-token" in os.environ and not force_load:
        return
    with open(filepath) as file:
        os.environ["tg-bot-token"] = file.read().strip()
