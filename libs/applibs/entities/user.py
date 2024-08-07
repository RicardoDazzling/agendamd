import json
import os.path

from typing import Callable, Optional, Literal
from hashlib import sha256
from functools import partial, cached_property

from libs.applibs.exceptions.login import PasswordException
from libs.applibs.utils import encrypt_data, md5_hash, decrypt_data
from settings import settings
from dataclasses import dataclass, asdict


@dataclass
class User:
    keep_logged: bool
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    password_string: Optional[str] = None
    tag_int_size: Optional[Literal["B", "H", "I", "L"]] = 'B'
    task_max_title_size: Optional[int] = 20
    task_max_description_size: Optional[int] = 80
    task_max_tag_size: Optional[int] = 20
    _bindings: Optional[dict[str, list[Callable]]] = None

    def __setattr__(self, key, value):
        if hasattr(self, key) and value is not None:
            if key in ['name', 'email', 'password', 'password_string', 'tag_int_size']:
                __expected_type = str
            elif key in ['task_max_title_size', 'task_max_description_size', 'task_max_tag_size']:
                __expected_type = int
            else:
                __expected_type = None
            if __expected_type is not None:
                if not isinstance(value, __expected_type):
                    raise TypeError(f'"{key}" argument need a <{__expected_type}> instance.')
        super(User, self).__setattr__(key, value)
        if value is None:
            return
        if key == 'password_string':
            if self.password is None:
                self.password = self.hash(value)
            else:
                if not self.match_password(value):
                    raise PasswordException()
        if key in self.public_variables and self._bindings is not None:
            __method_name = f'on_{key}'
            if __method_name in self._bindings:
                for method in self._bindings[__method_name]:
                    method(value)

    @property
    def user_db_dir(self) -> str:
        return str(os.path.join(settings.CACHE_DIR, 'db', self.email))

    @property
    def bindings(self) -> dict[str, list[Callable]]:
        return self._bindings

    @cached_property
    def public_variables(self):
        return list(filter(lambda v: not v.startswith("_"), asdict(self).keys()))

    def update_password(self, new_password: str):
        self.password = None  # To avoid PasswordException
        self.password_string = new_password

    def bind(self, **kwargs: Callable):
        for key, value in kwargs.items():
            if key.replace('on_', '') in self.public_variables:
                if self._bindings is None:
                    self._bindings = {key: [value]}
                elif key not in self._bindings:
                    self._bindings[key] = [value]
                else:
                    self._bindings[key].append(value)

    def unbind(self, **kwargs: Callable):
        for key, value in kwargs.items():
            if key in self._bindings:
                if value in self._bindings[key]:
                    self._bindings[key].remove(value)

    def match_password(self, new_password: str) -> bool:
        __hash = self.hash(new_password) if not self.keep_logged else new_password
        __comparison = self.password == __hash
        if __comparison and self.password_string is None:
            self.update_password(new_password)
        return __comparison

    _iv = md5_hash(settings.NAME)

    def serialize(self) -> str:
        encrypt = partial(encrypt_data, key=md5_hash(self.password_string), iv=self._iv)
        __dict = {
            "name": encrypt(self.name),
            "email": encrypt(self.email),
            "password": self.password_string if self.keep_logged else self.password,
            'tag_int_size': encrypt(self.tag_int_size),
            'task_max_title_size': encrypt(str(self.task_max_title_size)),
            'task_max_description_size': encrypt(str(self.task_max_description_size)),
            'task_max_tag_size': encrypt(str(self.task_max_tag_size))
        }
        return json.dumps(__dict)

    def deserialize(self, serialized_data: str):
        __dict: dict = json.loads(serialized_data)
        __password = __dict["password"]

        def deserialize(dict_data: dict, password, unbind: bool = False):
            i_decrypt = partial(decrypt_data, key=md5_hash(password), iv=self._iv)
            for i_key, i_value in dict_data.items():
                if i_key != "password":
                    i_decrypted = i_decrypt(i_value)
                    if isinstance(self.__getattribute__(i_key), int):
                        i_decrypted = int(i_decrypted)
                    self.__setattr__(i_key, i_decrypted)
            if unbind:
                self.unbind(on_password_string=partial(deserialize, dict_data, unbind=True))

        if not self.keep_logged and not self.password_string:
            self.password = __password
            self.bind(on_password_string=partial(deserialize, __dict, unbind=True))
            return
        elif not self.keep_logged:
            self.password = __password
            __password = self.password_string
        else:
            self.password_string = __password
        deserialize(__dict, __password)

    @staticmethod
    def hash(string: str) -> str:
        return sha256(string.encode('utf-8')).hexdigest()
