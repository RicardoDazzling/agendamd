import os

import numpy as np
import pandas as pd

from datetime import datetime, date
from typing import Optional, Callable, Literal, Union

from .config import CONFIG
from .users import USERS
from libs.applibs.exceptions.tasks import *
from libs.applibs.utils import read_numpy, get_date_from_datestamp


dtypes = {'title': f'U{CONFIG.task_max_title_size}',
          'day': np.uint32,
          'start': np.uint16,
          'end': np.uint16,
          'description': f'U{CONFIG.task_max_description_size}',
          'tag': CONFIG.tag_int_size,
          'closed': '?'}


class Tasks:

    task_dir: Optional[str] = None
    _bindings: dict[str, list[Callable]] = {
        "on_add": [],
        "on_update": [],
        "on_remove": [],
    }

    def __init__(self):
        USERS.bind(on_login=self._update_task_dir)
        self._update_task_dir()

    def __add__(self, other: dict):
        if not isinstance(other, dict):
            raise TypeError("Other isn't a instance of dict.")
        return self.add(other)

    def __sub__(self, other: dict):
        if not isinstance(other, dict):
            raise TypeError("Other isn't a instance of dict.")
        return self.remove(other)

    def __getitem__(self, item: Union[str, date]):
        if isinstance(item, date):
            return self.get(year=item.year, month=item.month)
        return super(Tasks, self).__getattribute__(item)

    def __setitem__(self, key: Union[str, dict], value):
        if isinstance(key, dict) and isinstance(value, dict):
            self.update(key, value)
        else:
            super(Tasks, self).__setattr__(key, value)

    def bind(self,
             on_add: Optional[Callable] = None,
             on_update: Optional[Callable] = None,
             on_remove: Optional[Callable] = None):
        if on_add is not None:
            self._bindings['on_add'].append(on_add)
        if on_update is not None:
            self._bindings['on_update'].append(on_update)
        if on_remove is not None:
            self._bindings['on_remove'].append(on_remove)

    def unbind(self,
               on_add: Optional[Callable] = None,
               on_update: Optional[Callable] = None,
               on_remove: Optional[Callable] = None):
        if on_add is not None:
            if on_add in self._bindings['on_add']:
                self._bindings['on_add'].remove(on_add)
        if on_update is not None:
            if on_update in self._bindings['on_update']:
                self._bindings['on_update'].remove(on_update)
        if on_remove is not None:
            if on_remove in self._bindings['on_remove']:
                self._bindings['on_remove'].remove(on_remove)

    def get_all(self):
        USERS.logged(raise_exception=True)
        __now = datetime.today()
        __path = os.listdir(self.task_dir)

        __df = None
        for folder in __path:
            __df = self._get_folder(folder, __df, concat=True)

        if __df is None:
            return None
        return __df

    def get(self,
            year: int,
            month: int):
        USERS.logged(raise_exception=True)
        __now = datetime.today()
        __path = f'{year}_{month}'

        __df = self._get_folder(__path)

        if __df is None:
            return None
        return __df

    def update(self, old: dict, new: dict):
        USERS.logged(raise_exception=True)
        __old_day = get_date_from_datestamp(old['day'])
        __new_day = get_date_from_datestamp(new['day'])
        __month_folder = os.path.join(self.task_dir, f"{__old_day.year}_{__old_day.month}")
        if __old_day.month != __new_day.month:
            self.remove(old)
            self.add(new)
            return
        if os.path.exists(__month_folder):
            __df = self.read(__month_folder)
            __find = __df.isin({k: [v] for k, v in old.items()}).all(axis=1)
            if not __find.any():
                raise TaskNotExistsException()
            __df.loc[__df.loc[__find].index[0]] = new
        else:
            raise TaskNotExistsException()
        self.write(__month_folder, __df)
        for method in self._bindings['on_update']:
            method(old, new)

    def add(self, row: dict) -> pd.DataFrame:
        USERS.logged(raise_exception=True)
        __day = get_date_from_datestamp(row['day'])
        __month_folder = os.path.join(self.task_dir, f"{__day.year}_{__day.month}")
        if os.path.exists(__month_folder):
            __df = self.read(__month_folder)
            if __df.isin({k: [v] for k, v in row.items()}).all(axis=1).any():
                raise TaskAlreadyExistsException()
            __df.loc[len(__df), row.keys()] = row.values()
        else:
            __df = pd.DataFrame({'title': [row.get('title')],
                                 'day': [row.get('day')],
                                 'start': [row.get('start')],
                                 'end': [row.get('end')],
                                 'description': [row.get('description')],
                                 'tag': [row.get('tag')],
                                 'closed': [row.get('closed')]})
        self.write(__month_folder, __df)
        for method in self._bindings['on_add']:
            method(row)
        return __df

    def remove(self, row: dict) -> pd.DataFrame:
        USERS.logged(raise_exception=True)
        __day = get_date_from_datestamp(row['day'])
        __month_folder = os.path.join(self.task_dir, f"{__day.year}_{__day.month}")
        if not os.path.exists(__month_folder):
            raise MonthFolderNotFoundException()

        __df = self.read(__month_folder)
        __df_isin = __df.isin({k: [v] for k, v in row.items()})
        __df_isin_all = __df_isin.all(axis=1)
        __s = __df.loc[__df_isin_all]
        __index = __s.index
        __df.drop(__index)
        if __df.empty:
            os.remove(__month_folder)
        else:
            self.write(__month_folder, __df)
        for method in self._bindings['on_remove']:
            method(row)
        return __df

    def _get_folder(self, folder: str, df: Optional[pd.DataFrame] = None, concat: bool = False) \
            -> Optional[pd.DataFrame]:
        __month_folder = os.path.join(self.task_dir, folder)
        if not os.path.exists(__month_folder):
            return None
        __idf = self.read(__month_folder)
        if not concat:
            return __idf
        __df = __idf if df is None else pd.concat([df, __idf], ignore_index=True)
        return __df

    def _update_task_dir(self):
        self.task_dir = None if not USERS.logged() else os.path.join(USERS.user_db_dir, 'tasks')
        if self.task_dir is not None:
            if not os.path.exists(self.task_dir):
                os.makedirs(self.task_dir)

    @staticmethod
    def read(folder: str) -> pd.DataFrame:
        __title = read_numpy(os.path.join(folder, 'title.npy'))
        __day = read_numpy(os.path.join(folder, 'day.npy'))
        __start = read_numpy(os.path.join(folder, 'start.npy'))
        __end = read_numpy(os.path.join(folder, 'end.npy'))
        __description = read_numpy(os.path.join(folder, 'description.npy'))
        __tag = read_numpy(os.path.join(folder, 'tag.npy'))
        __closed = read_numpy(os.path.join(folder, 'closed.npy'))
        __idf = pd.DataFrame(data={'title': __title,
                                   'day': __day,
                                   'start': __start,
                                   'end': __end,
                                   'description': __description,
                                   'tag': __tag,
                                   'closed': __closed},
                             columns=['title', 'day', 'start', 'end', 'description', 'tag', 'closed'])
        __idf.astype(dtypes)
        return __idf

    @staticmethod
    def write(folder: str, df: pd.DataFrame) -> None:
        __columns = df.columns.tolist()
        __dtypes = dtypes
        for column in __columns:
            __value = df[column]
            if not isinstance(df[column], np.ndarray):
                __value = np.array(__value, dtype=__dtypes[column])
            else:
                __value = __value.astype(__dtypes[column])
            if not os.path.exists(folder):
                os.mkdir(folder)
            with open(os.path.join(folder, column + '.npy'), 'wb') as f:
                np.save(f, __value)

    @staticmethod
    def reset_tag(tag: int):
        Tasks._update_array('tags.npy', lambda array: np.where(array == tag, 0, array))

    @staticmethod
    def resize_tag(dtype: Literal["B", "H", "I", "L"]):
        Tasks._update_array('tags.npy', lambda array: array.astype(dtype))

    @staticmethod
    def _update_array(file: str, method: Callable):
        USERS.logged(raise_exception=True)
        __task_dir = os.path.join(USERS.user_db_dir, 'tasks')
        for path in os.listdir(__task_dir):
            __adir = os.path.join(__task_dir, path)
            if os.path.isdir(__adir):
                __tags_file = os.path.join(__adir, file)
                if os.path.exists(__tags_file):
                    with open(__tags_file, 'rb') as f:
                        __array = np.load(f)
                    __array = method(__array)
                    with open(__tags_file, 'wb') as f:
                        np.save(f, __array)


if 'TASKS' not in globals():
    TASKS = Tasks()
