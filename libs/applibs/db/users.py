import os
import re
import numpy as np

from typing import Optional, Callable, Union, Literal

from settings import settings
from libs.applibs.db.config import CONFIG
from libs.applibs.entities import User
from libs.applibs.exceptions import UserNotExistException, EmptyFieldException, EMailException, PasswordException, \
    NameException, NotLoggedException, UserAlreadyExistsException, TooLongPasswordException, UserNotLoggedException
from libs.applibs.utils import read_numpy, utils


class Users:

    _bindings: dict[str, list[Callable]] = {
        "on_login": []
    }

    def __init__(self):
        self._path = os.path.join(settings.CACHE_DIR, 'db', 'users')
        if not os.path.exists(self._path):
            os.mkdir(self._path)
        try:
            self._list_path = os.listdir(self._path)
        except FileNotFoundError:
            self._list_path = []
        try:
            self._user = self._user_file
        except FileNotFoundError:
            self._user = None

    def logged(self, raise_exception: bool = False) -> bool:
        __logged = self._user is not None
        if not __logged and raise_exception:
            raise UserNotLoggedException()
        return __logged

    def bind(self, on_login: Optional[Callable] = None):
        if on_login is not None:
            self._bindings["on_login"].append(on_login)

    def login(self, email: str, password: str, keep_logged: bool = False) -> None:
        if self._user is None:
            raise UserNotExistException()
        if email is None or password is None:
            raise EmptyFieldException()
        __user = self._read_file(email + ".npy", ignore=True)
        if email + ".npy" not in self._list_path or not isinstance(__user, User):
            raise EMailException()
        if len(password) > 32:
            raise TooLongPasswordException()
        if not __user.compare_password(password):
            raise PasswordException()
        self._user = __user
        if keep_logged != self._user.keep_logged:
            self._user.keep_logged = [keep_logged, password]
        CONFIG.default_user = email
        for method in self._bindings["on_login"]:
            method()

    def register(self, name: str, email: str, password: str, keep_logged: bool = False) -> None:
        if email is None or password is None:
            raise EmptyFieldException()

        if not re.match(r'^[a-z0-9]+[._]?[a-z0-9]+@\w+[.]\w+$', email):
            raise EMailException()

        if not all([letter.isalpha() or letter.isspace() for letter in name]):
            raise NameException()

        if email + ".npy" in self._list_path:
            raise UserAlreadyExistsException()

        if len(password) > 32:
            raise TooLongPasswordException()

        self._user = User(name=name, email=email, password=password, keep=keep_logged, on_keep=self.save)
        self._user_file = self._user.array
        CONFIG.default_user = email
        for method in self._bindings["on_login"]:
            method()

    def decrypt_database(self):
        self._crypt_database(utils.decrypt, extension=".npy.amc")

    def encrypt_database(self):
        self._crypt_database(utils.encrypt, extension=".npy")

    def save(self):
        if isinstance(self._user, User):
            self._user_file = self._user.array

    def _crypt_database(self, method: Callable, extension: Literal[".npy", ".npy.amc"]):
        if not isinstance(self._user, User) or not self.logged():
            raise NotLoggedException()

        for root, dirs, files in os.walk(self.user_db_dir):
            for file in files:
                if file.endswith(extension):
                    method(
                        os.path.join(root, file),
                        utils.md5_hash(self._user.password),
                        utils.md5_hash(settings.NAME)
                    )

    def _read_file(self, email: Optional[str] = None, ignore: bool = False) -> Union[User, False]:
        if email is None:
            email = CONFIG.default_user
            if email == "":
                if ignore:
                    return False
                raise FileNotFoundError("User file not found.")
        __np = read_numpy(os.path.join(self._path, email + '.npy'))
        if __np is None:
            if ignore:
                return False
            raise FileNotFoundError("User file not found.")
        return User(array=__np, on_keep=self.save)

    @property
    def user_db_dir(self) -> str:
        return None if self._user is None else str(os.path.join(settings.CACHE_DIR, 'db', self.user.email))

    @property
    def user(self) -> User:
        return self._user

    @property
    def _user_file(self) -> User:
        return self._read_file()

    @_user_file.setter
    def _user_file(self, val: np.ndarray | User) -> None:
        if isinstance(val, User):
            __file = val.email
        elif isinstance(val, np.ndarray):
            __file = val[1]
        else:
            raise TypeError("User file need to be a User or a NdArray.")
        __file += ".npy"
        with open(os.path.join(self._path, __file), 'wb') as file:
            __val = val if isinstance(val, np.ndarray) else val.array
            np.save(file, __val)


if "USERS" not in globals():
    USERS = Users()
