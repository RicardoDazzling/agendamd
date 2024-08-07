__all__ = ["CONFIG"]

import configparser
import os
from functools import cached_property

from settings import settings
from typing import Literal


class Config:
    def __init__(self):
        self.config_file = os.path.join(settings.CACHE_DIR, 'config.ini')
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            self._read_file()
        else:
            self._create_file()

    @property
    def default_user(self) -> str:
        return self._get_current("DEFAULT_USER")

    @default_user.setter
    def default_user(self, default_user: str) -> None:
        self._set_current(self.default_user, default_user, "DEFAULT_USER")

    @property
    def dark_mode(self) -> bool:
        return self._get_current_boolean("DARK_MODE")

    @dark_mode.setter
    def dark_mode(self, dark_mode: bool) -> None:
        self._set_current_boolean(self.dark_mode, dark_mode, 'DARK_MODE')

    @property
    def keep_logged(self) -> bool:
        return self._get_current_boolean("KEEP_LOGGED")

    @keep_logged.setter
    def keep_logged(self, keep_logged: bool) -> None:
        self._set_current_boolean(self.keep_logged, keep_logged, 'KEEP_LOGGED')

    @property
    def language(self) -> Literal['pt_BR', 'en_US']:
        __language = self._get_current("LANGUAGE")
        if __language == 'pt_BR':
            return 'pt_BR'
        elif __language == 'en_US':
            return 'en_US'
        else:
            raise ValueError(f'Unknown language: {__language}')

    @language.setter
    def language(self, language: Literal['pt_BR', 'en_US']) -> None:
        self._set_current(self.language, language, "LANGUAGE")

    @property
    def task_oldest_day(self) -> str:
        # TODO: implement this
        return self._get_current("TASK_OLDEST_DAY")

    @task_oldest_day.setter
    def task_oldest_day(self, task_oldest_day: str) -> None:
        self._set_current(self.task_oldest_day, task_oldest_day, "TASK_OLDEST_DAY", True)

    @cached_property
    def default_config(self) -> dict:
        return {
            "CONFIG_VERSION": "2",
            "KEEP_LOGGED": "FALSE",
            "DEFAULT_USER": "",
            "DARK_MODE": "FALSE",
            "LANGUAGE": "en_US",
            "TASK_OLDEST_DAY": "0",
        }

    def _read_file(self):
        self.config.read(self.config_file)
        config_version = self.config.get('main', 'CONFIG_VERSION', fallback='0')

        if config_version != self.default_config["CONFIG_VERSION"]:
            self._update_file()

    def _create_file(self):
        self.config["main"] = self.default_config
        self.save_config()

    def _update_file(self):
        __default_config = self.default_config.copy()
        for key in self.config['main'].keys():
            key = key.upper()
            if key in __default_config.keys():
                __default_config[key] = self.config['main'][key]
        self.config["main"] = __default_config
        self.save_config()

    def _get_current_boolean(self, name: str) -> bool:
        __value = self._get_current(name).lower()
        return __value == 'true' or __value == '1'

    def _set_current_boolean(self, old: bool, new: bool, name: str) -> None:
        if old != new:
            self.config['main'][name] = 'TRUE' if new else 'FALSE'
            self.save_config()

    def _get_current(self, name: str) -> str:
        return self.config.get("main", name)

    def _set_current(self, old, new, name: str, is_numeric: bool = False):
        if is_numeric and isinstance(new, str):
            if not new.isnumeric():
                raise AttributeError("New value isn't numeric.")
        if old != new:
            self.config['main'][name] = new
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)


if "CONFIG" not in globals():
    CONFIG = Config()
