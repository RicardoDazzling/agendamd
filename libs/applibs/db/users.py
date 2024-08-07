import os
import re
from functools import partial

from typing import Optional, Callable, Union, Literal

from settings import settings
from libs.applibs.db.config import CONFIG
from libs.applibs.entities import User
from libs.applibs.exceptions import UserNotExistException, EmptyFieldException, EMailException, PasswordException, \
    NameException, NotLoggedException, UserAlreadyExistsException, TooLongPasswordException, UserNotLoggedException
from libs.applibs.utils import utils, ignore_args


class Users:

    _bindings: dict[str, list[Callable]] = {
        "on_login": [],
        "on_logout": []
    }
    _user: User = User(CONFIG.keep_logged)

    def __init__(self):
        self._path = os.path.join(settings.CACHE_DIR, 'db', 'users')
        if not os.path.exists(self._path):
            os.mkdir(self._path)
        try:
            self._list_path = os.listdir(self._path)
        except FileNotFoundError:
            self._list_path = []
        self.load()
        __bindings = {f"on_{var}": self.save for var in self._user.public_variables}
        self._user.bind(**__bindings)

    def __getattr__(self, name: str):
        if self._user.password_string is not None:
            return getattr(self._user, name)
        raise NameError("Unknown property for user(s).")

    def __setattr__(self, name: str, value):
        if self._user.password_string is not None and hasattr(self._user, name):
            setattr(self._user, name, value)
            return
        super().__setattr__(name, value)

    @property
    def keep_logged(self) -> bool:
        return CONFIG.keep_logged

    def logged(self, raise_exception: bool = False) -> bool:
        __logged = self._user.password_string is not None
        if not __logged and raise_exception:
            raise UserNotLoggedException()
        return self._user.password_string is not None

    def logout(self):
        self._user.keep_logged = False
        CONFIG.keep_logged = False
        self.save()
        self.load()
        for method in self._bindings["on_logout"]:
            method()

    def bind(self, on_login: Optional[Callable] = None, on_logout: Optional[Callable] = None, **kwargs):
        if on_login is not None:
            self._bindings["on_login"].append(on_login)
        if on_logout is not None:
            self._bindings["on_logout"].append(on_logout)
        if kwargs and isinstance(self._user, User):
            self._user.bind(**kwargs)

    def unbind(self, on_login: Optional[Callable] = None, on_logout: Optional[Callable] = None, **kwargs):
        if on_login is not None:
            self._bindings["on_login"].remove(on_login)
        if on_logout is not None:
            self._bindings["on_logout"].remove(on_logout)
        if kwargs and isinstance(self._user, User):
            self._user.unbind(**kwargs)

    def login(self, email: str, password: str, keep_logged: bool = False) -> None:
        if email is None or password is None:
            raise EmptyFieldException()
        if not re.match(r'^[a-z0-9]+[._]?[a-z0-9]+@\w+[.]\w+$', email):
            raise EMailException()
        if email + ".npy" not in self._list_path:
            raise UserNotExistException()
        self._read_file(email, keep_logged=keep_logged)
        if len(password) > 32:
            raise TooLongPasswordException()
        if not self._user.match_password(password):
            raise PasswordException()
        CONFIG.keep_logged = keep_logged
        CONFIG.default_user = email
        self._user.keep_logged = keep_logged
        self.save()
        for method in self._bindings["on_login"]:
            method()

    def register(self, name: str, email: str, password: str, keep_logged: bool = False) -> None:
        if email is None or password is None:
            raise EmptyFieldException()

        if not re.match(r'^[a-z0-9]+[._]?[a-z0-9]+@\w+[.]\w+$', email):
            raise EMailException()

        if not all([letter.isalpha() or letter.isspace() for letter in name]):
            raise NameException()

        if email + ".json" in self._list_path:
            raise UserAlreadyExistsException()

        if len(password) > 32:
            raise TooLongPasswordException()

        CONFIG.keep_logged = keep_logged

        self._user = User(keep_logged=CONFIG.keep_logged, _bindings=self._user.bindings,
                          name=name, email=email, password_string=password,)
        self.save()
        self._list_path.append(email + ".json")
        CONFIG.default_user = email
        for method in self._bindings["on_login"]:
            method()

    def update_password(self, new_password: str):
        self._user.update_password(new_password)
        self.save()
        self.encrypt_database(False)

    def decrypt_database(self):
        self._crypt_database(utils.decrypt, extension=".npy.amc")

    def encrypt_database(self, remove_npy: bool = True):
        self._crypt_database(partial(utils.encrypt, remove_npy=remove_npy), extension=".npy")

    @ignore_args
    def save(self):
        if self.logged():
            __file = self._user.email
            __file += ".json"
            with open(os.path.join(self._path, __file), 'w') as file:
                file.write(self._user.serialize())

    def load(self):
        __bindings = self._user.bindings
        try:
            self._read_file()
        except FileNotFoundError:
            self._user = User(CONFIG.keep_logged, _bindings=__bindings)

    def _crypt_database(self, method: Callable, extension: Literal[".npy", ".npy.amc"]):
        if not self.logged():
            raise NotLoggedException()

        for root, dirs, files in os.walk(self.user_db_dir):
            for file in files:
                if file.endswith(extension):
                    method(
                        os.path.join(root, file),
                        utils.md5_hash(self._user.password_string),
                        utils.md5_hash(settings.NAME)
                    )

    def _read_file(self,
                   email: Optional[str] = None,
                   ignore: bool = False,
                   keep_logged: Optional[bool] = None) -> Union[User, bool]:
        if keep_logged is None:
            self._user.keep_logged = CONFIG.keep_logged
        if email is None:
            email = CONFIG.default_user
            if email == "":
                if ignore:
                    return False
                raise FileNotFoundError("User file not found.")
        __path = os.path.join(self._path, email + '.json')
        if os.path.exists(__path):
            with open(__path, 'r') as f:
                __dumps = f.read()
        else:
            if ignore:
                return False
            raise FileNotFoundError("User file not found.")
        self._user.deserialize(__dumps)
        return self._user

    @property
    def user_db_dir(self) -> str:
        return None if not self.logged() else self._user.user_db_dir

    @property
    def user(self) -> User:
        return self._user


if "USERS" not in globals():
    USERS = Users()
