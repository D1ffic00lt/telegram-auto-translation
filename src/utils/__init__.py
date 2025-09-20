import os

from . import translation
from . import exceptions


def load_env(filepath: str, name: str, *, force_load: bool = False):
    if name in os.environ and not force_load:
        return
    with open(filepath) as file:
        os.environ[name] = file.read().strip()
