import configparser
import os
import re
import numpy as np
from hashlib import sha256

from libs.applibs.exceptions import UserNotExistException, EmptyFieldException, EMailException, PasswordException, \
    NameException


class DB:
    def __init__(self):
        self.cache_dir = os.path.join(os.getenv("CACHE_DIR"), 'db')
        self.config_file = os.path.join(os.getenv("CACHE_DIR"), 'config.ini')
        self.config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config["main"] = {"KEEP_LOGGED": "False"}
            self.save_config()
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
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
        if os.path.exists(__user_file):
            with open(__user_file, 'rb') as file:
                return np.load(file)  # ['name', 'email', 'password']
        raise FileNotFoundError("User file not found.")

    @_user_file.setter
    def _user_file(self, val: np.ndarray) -> None:
        __user_file = os.path.join(self.cache_dir, 'user.npy')
        with open(__user_file, 'wb') as file:
            np.save(file, val)

    def save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
