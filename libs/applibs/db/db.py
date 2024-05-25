import configparser
import os
import re
from typing import Optional

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from hashlib import sha256

from libs.applibs.exceptions import UserNotExistException, EmptyFieldException, EMailException, PasswordException, \
    NameException


def read_numpy(path):
    if os.path.exists(path):
        with open(path, 'rb') as file:
            return np.load(file)  # ['name', 'email', 'password']
    return None


class DB:
    def __init__(self):
        self.cache_dir = os.path.join(os.getenv("CACHE_DIR"), 'db')
        self.config_file = os.path.join(os.getenv("CACHE_DIR"), 'config.ini')
        self.config = configparser.ConfigParser()
        self.this_month_df = None
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config["main"] = {"KEEP_LOGGED": "False"}
            self.save_config()
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        __tasks_folder = os.path.join(self.cache_dir, 'tasks')
        if not os.path.exists(__tasks_folder):
            os.makedirs(__tasks_folder)
        try:
            self._user = self._user_file
        except FileNotFoundError:
            self._user = None

    def logged(self) -> bool:
        return self._user is not None

    def login(self, email: str, password: str) -> None:
        if self._user is None:
            raise UserNotExistException()
        if email is None or password is None:
            raise EmptyFieldException()
        if email != self._user[1]:
            raise EMailException()
        if sha256(password.encode('utf-8')).hexdigest() != self._user[2]:
            raise PasswordException()

    def register(self, name: str, email: str, password: str) -> None:
        if email is None or password is None:
            raise EmptyFieldException()

        if not re.match(r'^[a-z0-9]+[._]?[a-z0-9]+[@]\w+[.]\w+$', email):
            raise EMailException()

        if not name.isalpha():
            raise NameException()

        self._user = np.array([name, email, sha256(password.encode('utf-8')).hexdigest()])
        self._user_file = self._user

    @property
    def dashboard_tasks(self) -> Optional[pd.DataFrame]:
        __tasks_folder = os.path.join(self.cache_dir, 'tasks')
        __now = datetime.today()
        __after_days = __now + timedelta(days=6)
        if self.this_month_df is not None:
            __df = self.this_month_df.copy()
        else:
            __before = __now - timedelta(days=30)
            __after = __now + timedelta(days=30)
            __up_a_month = __now.month != __after.month
            __path = [f"{__before.year}_{__before.month}", f"{__now.year}_{__now.month}", f"{__after.year}_{__after.month}"]

            __df = None
            for folder in __path:
                __month_folder = os.path.join(__tasks_folder, folder)
                if not os.path.exists(__month_folder):
                    continue
                __title = read_numpy(os.path.join(__month_folder, 'title.npy'))
                __start = read_numpy(os.path.join(__month_folder, 'start.npy'))
                __end = read_numpy(os.path.join(__month_folder, 'end.npy'))
                __description = read_numpy(os.path.join(__month_folder, 'description.npy'))
                __tag = read_numpy(os.path.join(__month_folder, 'tag.npy'))
                __closed = read_numpy(os.path.join(__month_folder, 'closed.npy'))
                __idf = pd.DataFrame({'title': __title,
                                      'start': __start,
                                      'end': __end,
                                      'description': __description,
                                      'tag': __tag,
                                      'closed': __closed})
                __df = __idf if __df is None else __df.set_index('start').join(__idf.set_index('start'))

            self.this_month_df = None if __df is None else __df.copy()

        if __df is None:
            return None
        return __df.loc[((__df['start'] > __now.timestamp()) &
                        (__df['start'] < __after_days.timestamp())) |
                        ((__df['end'] > __now.timestamp()) &
                        (__df['end'] < __after_days.timestamp()))]

    def add_task(self, title: str, start: int, duration: int, description: str, tag: int):
        __tasks_folder = os.path.join(self.cache_dir, 'tasks')
        __array = np.array([])

    @property
    def keep(self) -> bool:
        return self.config.getboolean('main', 'KEEP_LOGGED')

    @keep.setter
    def keep(self, keep: bool) -> None:
        __self_keep = self.keep
        if keep and not __self_keep:
            self.config['main']['KEEP_LOGGED'] = 'True'
            self.save_config()
        elif not keep and __self_keep:
            self.config['main']['KEEP_LOGGED'] = 'False'
            self.save_config()

    @property
    def _user_file(self) -> np.ndarray:
        __user_file = os.path.join(self.cache_dir, 'user.npy')
        __np = read_numpy(__user_file)
        if __np is None:
            raise FileNotFoundError("User file not found.")
        return __np

    @_user_file.setter
    def _user_file(self, val: np.ndarray) -> None:
        __user_file = os.path.join(self.cache_dir, 'user.npy')
        with open(__user_file, 'wb') as file:
            np.save(file, val)

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
