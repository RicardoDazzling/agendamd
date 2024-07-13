
__all__ = ["settings"]

import os

from appdirs import user_cache_dir


class Settings:
    def __init__(self):
        self.NAME: str = "AgendaMD"
        self.CACHE_DIR: str = user_cache_dir(self.NAME.lower(), opinion=False)

        if not os.path.exists(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
        if not os.path.exists(os.path.join(self.CACHE_DIR, 'db')):
            os.makedirs(os.path.join(self.CACHE_DIR, 'db'))


if 'settings' not in globals():
    settings = Settings()
