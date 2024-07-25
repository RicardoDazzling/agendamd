import configparser
import os

from settings import settings
from typing import Literal


__all__ = ["CONFIG"]


class Config:
    def __init__(self):
        self.config_file = os.path.join(settings.CACHE_DIR, 'config.ini')
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self._create_file()

    @property
    def default_user(self) -> str:
        return self._get_current("DEFAULT_USER")

    @default_user.setter
    def default_user(self, default_user: str) -> None:
        self._set_current(self.default_user, default_user, "DEFAULT_USER")

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
    def tag_int_size(self) -> str:
        return self._get_current("TAG_INT_SIZE")

    @tag_int_size.setter
    def tag_int_size(self, tag_int_size: Literal["B", "H", "I", "L"]) -> None:
        self._set_current(self.tag_int_size, tag_int_size, "TAG_INT_SIZE", True)

    @property
    def task_max_title_size(self) -> str:
        return self._get_current("TASK_MAX_TITLE_SIZE")

    @task_max_title_size.setter
    def task_max_title_size(self, task_max_title_size: str) -> None:
        self._set_current(self.task_max_title_size, task_max_title_size, "TASK_MAX_TITLE_SIZE", True)

    @property
    def task_max_description_size(self) -> str:
        return self._get_current("TASK_MAX_DESCRIPTION_SIZE")

    @task_max_description_size.setter
    def task_max_description_size(self, task_max_description_size: str) -> None:
        self._set_current(self.task_max_description_size, task_max_description_size, "TASK_MAX_DESCRIPTION_SIZE", True)

    @property
    def task_max_tag_size(self) -> str:
        return self._get_current("TASK_MAX_TAG_SIZE")

    @task_max_tag_size.setter
    def task_max_tag_size(self, task_max_tag_size: str) -> None:
        self._set_current(self.task_max_tag_size, task_max_tag_size, "TASK_MAX_TAG_SIZE", True)

    @property
    def task_oldest_day(self) -> str:
        return self._get_current("TASK_OLDEST_DAY")

    @task_oldest_day.setter
    def task_oldest_day(self, task_oldest_day: str) -> None:
        self._set_current(self.task_oldest_day, task_oldest_day, "TASK_OLDEST_DAY", True)

    def _create_file(self):
        self.config["main"] = {
            "DEFAULT_USER": "",
            "LANGUAGE": "en_US",
            "TAG_INT_SIZE": "B",
            "TASK_MAX_TITLE_SIZE": "20",
            "TASK_MAX_DESCRIPTION_SIZE": "80",
            "TASK_MAX_TAG_SIZE": "20",
            "TASK_OLDEST_DAY": "0",
        }
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
