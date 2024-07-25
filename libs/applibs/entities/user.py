import os.path

import numpy as np

from typing import Optional, Callable, List, Union
from hashlib import sha256
from settings import settings


class User:
    user_db_dir: str = "."
    _password_string: Optional[str] = None

    def __init__(self,
                 name: Optional[str] = None,
                 email: Optional[str] = None,
                 password: Optional[str] = None,
                 keep: Optional[bool] = None,
                 array: Optional[np.ndarray] = None,
                 on_keep: Callable = lambda x: None):
        self._keep = keep if keep is not None else False
        if array is not None:
            self.array = array.copy()
        else:
            self.array = np.array([name, email, password], dtype='U64')
        if password is not None and array is None:
            self._password_string = password if len(password) < 64 else None
        elif password is None and array is not None:
            __len = len(str(array[2]))
            self._password_string = str(array[2]) if __len < 64 else None
        self._on_keep: Callable = on_keep

        self.user_db_dir = str(os.path.join(settings.CACHE_DIR, 'db', self.email))

        if not os.path.exists(self.user_db_dir):
            os.makedirs(self.user_db_dir)
        if not os.path.exists(os.path.join(self.user_db_dir, 'tasks')):
            os.makedirs(os.path.join(self.user_db_dir, 'tasks'))

    def __repr__(self):
        return repr(self._array)

    def __str__(self):
        return self.email

    @property
    def array(self) -> np.ndarray:
        return self._array.copy()

    @array.setter
    def array(self, array: np.ndarray):
        __array = array.copy()
        __array[2] = __array[2] if self._keep or len(__array[2]) == 64 else self.hash(str(__array[2]))
        self._array = __array

    @property
    def name(self) -> str:
        return str(self._array[0])

    @name.setter
    def name(self, name: str):
        self._array = np.array([name, self._array[1], self._array[2]], dtype='U128')

    @property
    def email(self) -> str:
        return str(self._array[1])

    @email.setter
    def email(self, email: str):
        self._array = np.array([self._array[0], email, self._array[2]], dtype='U128')

    @property
    def password_string(self) -> Optional[str]:
        return self._password_string

    @password_string.setter
    def password_string(self, password: str):
        self._password_string = password

    @property
    def password(self) -> str:
        return str(self._array[2])

    @password.setter
    def password(self, password: str):
        self._password_string = password
        __hash = self.hash(password) if not self._keep else password
        self._array = np.array([self._array[0], self._array[1], __hash], dtype='U128')

    @property
    def keep_logged(self) -> bool:
        return self._keep

    @keep_logged.setter
    def keep_logged(self, value: List[Union[bool, Optional[str]]]):
        if not isinstance(value, (list, bool)):
            raise ValueError(
                "Value need to be a list with the keep logged (required) and password (optional) or a bool.")
        if isinstance(value, bool):
            value = [value, None]
        elif len(value) == 2:
            if not isinstance(value[0], bool):
                raise ValueError("The first list value need to be the keep logged value (a boolean).")
            if not isinstance(value[1], Optional[str]):
                raise ValueError("The second list value need to be the decrypted password or None (a optional str)")
        elif len(value) == 1:
            if not isinstance(value[0], bool):
                raise ValueError("The first list value need to be the keep logged value (a boolean).")
            value.append(None)
        else:
            raise ValueError(
                "Value need to be a list with the keep logged (required) and password (optional) or a bool.")
        if value[0] == self._keep:
            return
        if value[0]:
            if value[1] is None or not isinstance(value[1], str):
                raise ValueError("Not hashed password is a required argument when keep logged is set to True.")
            if value[1] == self.password:
                raise ValueError("A hashed password was given, but a not hashed is required.")
            self._array = np.array([self._array[0], self._array[1], value[1]])
            self._password_string = value[1]
        else:
            self._array = np.array([self._array[0], self._array[1], self.hash(self.password)])
        self._keep = value[0]
        self._on_keep()

    def compare_password(self, password: str) -> bool:
        __hash = self.hash(password) if not self._keep else password
        __comparison = self.password == __hash
        if __comparison:
            self._password_string = password
        return __comparison

    @staticmethod
    def hash(string: str) -> str:
        return sha256(string.encode('utf-8')).hexdigest()
