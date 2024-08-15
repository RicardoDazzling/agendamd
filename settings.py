
__all__ = ["settings", "start"]

import os
import sys

from appdirs import user_cache_dir


class Settings:

    NAME: str = "AgendaMD"
    CACHE_DIR: str = user_cache_dir(NAME.lower(), opinion=False)
    DEBUG: bool = True

    def __init__(self):
        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
        if not os.path.exists(os.path.join(self.CACHE_DIR, 'db')):
            os.makedirs(os.path.join(self.CACHE_DIR, 'db'))


def start() -> str:
    os.environ["NAME"] = settings.NAME
    os.environ["CACHE_DIR"] = settings.CACHE_DIR
    os.environ['KIVY_HOME'] = os.path.join(settings.CACHE_DIR, '.kivy')
    __pycache__ = os.path.join(settings.CACHE_DIR, 'pycache')
    os.environ["PYTHONPYCACHEPREFIX"] = __pycache__
    sys.pycache_prefix = __pycache__
    return __pycache__


if 'settings' not in globals():
    settings = Settings()
