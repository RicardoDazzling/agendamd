__all__ = ["TAGS"]

import os
import logging

import numpy as np

from typing import Optional, Union, Callable

from settings import settings
from .tasks import TASKS
from .users import USERS

from libs.devlibs.translation import translator as _
from libs.applibs.utils import array_size, encrypt, md5_hash, decrypt


class Tags:

    datafile: Optional[str] = None

    _array: Optional[np.ndarray] = None
    _max_tag_size: int = 20

    _bindings = {
        "on_data": []
    }

    def __init__(self):
        USERS.bind(on_login=self._update_datafile, on_logout=self.clean,
                   on_task_max_tag_size=self._update_max_tag_size)
        self._update_datafile()

    def __iter__(self):
        if self._array is None:
            return
        for value in self._array:
            yield value

    def __add__(self, other: str):
        if not isinstance(other, str):
            raise TypeError("Other isn't a instance of str.")
        return self.add(other)

    def __getitem__(self, item: Union[str, int]):
        if isinstance(item, int):
            return self.get(item)
        return super(Tags, self).__getattribute__(item)

    def __setitem__(self, key: Union[str, int], value):
        if isinstance(key, int) and isinstance(value, str):
            self.update(key, value)
        else:
            super(Tags, self).__setattr__(key, value)

    def __sub__(self, other: int):
        if not isinstance(other, int):
            raise TypeError("Other isn't a tag index.")
        return self.remove(other)

    def add(self, tag: str) -> int:
        USERS.logged(raise_exception=True)
        if not isinstance(tag, str):
            raise TypeError(f"Tag doesn't is from 'str' type, but from '{type(tag)}'")
        self._len(tag)
        __old_dtype = array_size(self._array.size)
        self._array = np.append(self._array, [tag]).astype("U" + str(self._max_tag_size))
        __new_dtype = array_size(self._array.size)
        if __old_dtype != __new_dtype:
            USERS.tag_int_size = __new_dtype
        self.save()
        return self._array.size - 1

    def get(self, tag: Union[str, int], multiple: bool = False) -> Union[int, str, list[int]]:
        USERS.logged(raise_exception=True)
        if isinstance(tag, str):
            if multiple:
                __list = []
                for idx, value in np.ndenumerate(self._array):
                    if tag == value:
                        __list.append(idx[0])
                return __list
            else:
                for idx, value in np.ndenumerate(self._array):
                    if tag == value:
                        return idx[0]
        elif isinstance(tag, int):
            return str(self._array[tag])
        else:
            raise TypeError("Tag must be an integer or string")
        raise IndexError("Unknown Tag.")

    def update(self, index: int, new_value: str):
        USERS.logged(raise_exception=True)
        self._len(new_value)
        if self._array[index] == new_value:
            return

        self._array[index] = new_value
        self.save()

    def remove(self, index: int) -> str:
        USERS.logged(raise_exception=True)
        __value = str(self._array[index])
        TASKS.reset_tag(index)
        self._array[index] = np.nan
        self.save()
        return __value

    def save(self):
        USERS.logged(raise_exception=True)
        with open(self.datafile, "wb") as file:
            np.save(file, self._array, False, False)

        self.on_data(list(self))

        encrypt(self.datafile,
                md5_hash(USERS.password_string),
                md5_hash(settings.NAME),
                remove_npy=False)

    def load(self, already_corrupted: bool = False):
        USERS.logged(raise_exception=True)
        try:
            with open(self.datafile, "rb") as file:
                self._array = np.load(file)

            self.on_data(list(self))

        except ValueError:
            if already_corrupted:
                raise ValueError("Tag data was corrupted.")
            logging.error("TAGS: Tag data was corrupted, trying to recover...")
            decrypt(self.datafile + '.amc',
                    md5_hash(USERS.password_string),
                    md5_hash(settings.NAME))
            self.load(True)

    def clean(self):
        self.datafile = None
        self._array = None

        self.on_data([])

    def bind(self, on_data: Optional[Callable] = None):
        if on_data is not None:
            self._bindings["on_data"].append(on_data)

    def on_data(self, new_data: list):
        for method in self._bindings["on_data"]:
            method(new_data)

    def _update_datafile(self):
        self.datafile = None if not USERS.logged() else os.path.join(USERS.user_db_dir, 'tags.npy')
        if self.datafile is not None:
            if os.path.exists(self.datafile + '.amc') and not os.path.exists(self.datafile):
                decrypt(self.datafile + '.amc',
                        md5_hash(USERS.password_string),
                        md5_hash(settings.NAME))
            if not os.path.exists(self.datafile):
                self._array = np.array([_("Default")], dtype="U" + str(self._max_tag_size))
                self.save()
            else:
                self.load()

    def _update_max_tag_size(self, new_size: int):
        if new_size == self._max_tag_size:
            return
        self._max_tag_size = new_size
        self._array = self._array.astype(f'U{new_size}')
        self.save()

    def _len(self, tag: str):
        if 3 > len(tag) > self._max_tag_size:
            raise ValueError(f"Tag must be between 3 and {self._max_tag_size} characters")


if "TAGS" not in globals():
    TAGS = Tags()
